#!/usr/bin/env python3
"""Natural-text test of spectral predictability for future model uncertainty.

Motivation
----------
Hand-crafted semantic-polarity experiments showed that a linearly decodable
concept need not be the graph's first Fiedler bottleneck, and a fresh
cross-model relative-depth confirmation failed. This experiment removes manual
semantic labels entirely.

For one deterministic natural-text excerpt per Markdown file in this repository:

1. take a fixed 64-token teacher-forced window;
2. observe the model's final-layer causal state q_t at token position 31;
3. build a label-free kNN representation graph from q_t;
4. measure the model's predictive entropy at t, t+4, t+8, and t+16;
5. ask whether future entropy is a smooth graph signal and whether representation
   neighbors predict it better than a scalar baseline that knows only entropy at t.

The primary horizon is H=8. H=0 is a positive sanity control because current
entropy is directly downstream of the current final hidden state. H=4 and H=16
are secondary horizon probes. All samples have the same model-token prefix
position, removing token-count as a nuisance by construction.

A scientific negative exits normally. Runtime or protocol failures fail CI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy
import torch
import transformers
from scipy.spatial.distance import cdist
from transformers import AutoModelForCausalLM, AutoTokenizer

from real_model_experiment import (
    configure_padding,
    knn_graph_with_sigma,
    normalize_rows,
    scramble_features,
)

CURRENT_POSITION = 31
WINDOW_TOKENS = 64
HORIZONS = (0, 4, 8, 16)
PRIMARY_HORIZON = 8
GRAPH_K = 8
PERMUTATIONS = 500
MAX_FILES = 160
MIN_FILES = 80
WORDS_PER_EXCERPT = 140
EXCLUDED_TOP_LEVEL = {
    ".git",
    ".github",
    "experiments",
    "yesindeed",
    "okf",
    "node_modules",
}
EXCLUDED_FILENAMES = {"CLAUDE.md", "AGENTS.md", "SKILL.md"}


@dataclass(frozen=True)
class NaturalSample:
    path: str
    excerpt_sha256: str
    excerpt: str


def _stable_int(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:16], 16)


def clean_markdown(raw: str) -> str:
    lines = raw.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, min(len(lines), 80)):
            if lines[index].strip() == "---":
                lines = lines[index + 1 :]
                break

    kept: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped:
            kept.append(" ")
            continue
        if stripped.startswith(("#", "|---", "<!--")):
            continue
        if re.match(r"^\s*[-*+]\s+`[^`]+`\s*$", line):
            continue
        kept.append(line)

    text = "\n".join(kept)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\$[^$]+\$", " ", text)
    text = re.sub(r"\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def collect_samples(repo_root: Path, max_files: int = MAX_FILES) -> list[NaturalSample]:
    candidates: list[tuple[str, Path, str]] = []
    for path in repo_root.rglob("*.md"):
        relative = path.relative_to(repo_root)
        if not relative.parts:
            continue
        if relative.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        if path.name in EXCLUDED_FILENAMES:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        text = clean_markdown(raw)
        words = text.split()
        if len(words) < WORDS_PER_EXCERPT:
            continue
        max_start = len(words) - WORDS_PER_EXCERPT
        start = _stable_int(relative.as_posix()) % (max_start + 1)
        excerpt = " ".join(words[start : start + WORDS_PER_EXCERPT])
        candidates.append((relative.as_posix(), path, excerpt))

    candidates.sort(key=lambda item: hashlib.sha256(item[0].encode()).hexdigest())
    selected = candidates[:max_files]
    return [
        NaturalSample(
            path=relative,
            excerpt_sha256=hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
            excerpt=excerpt,
        )
        for relative, _, excerpt in selected
    ]


def filter_tokenizable_samples(
    samples: list[NaturalSample], tokenizer, window_tokens: int = WINDOW_TOKENS
) -> list[NaturalSample]:
    accepted: list[NaturalSample] = []
    for sample in samples:
        ids = tokenizer(sample.excerpt, add_special_tokens=True, truncation=False)[
            "input_ids"
        ]
        if len(ids) >= window_tokens:
            accepted.append(sample)
    return accepted


def entropy_from_logits(logits: torch.Tensor) -> torch.Tensor:
    log_probs = torch.log_softmax(logits.to(torch.float32), dim=-1)
    probs = torch.exp(log_probs)
    return -(probs * log_probs).sum(dim=-1)


def extract_states_and_observables(
    samples: list[NaturalSample],
    *,
    model_name: str,
    revision: str,
    batch_size: int,
) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray], dict[str, object]]:
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision)
    configure_padding(tokenizer, model)
    tokenizer.padding_side = "right"
    model.eval().to("cpu")

    filtered = filter_tokenizable_samples(samples, tokenizer)
    if len(filtered) < MIN_FILES:
        raise RuntimeError(
            f"only {len(filtered)} natural files have >= {WINDOW_TOKENS} model tokens; "
            f"need at least {MIN_FILES}"
        )
    # Freeze the same deterministic prefix of the preselected file list after the
    # tokenizer length gate.
    filtered = filtered[:MAX_FILES]

    states: list[np.ndarray] = []
    entropy_parts: dict[int, list[np.ndarray]] = {h: [] for h in HORIZONS}
    surprisal_parts: dict[int, list[np.ndarray]] = {h: [] for h in HORIZONS}

    with torch.inference_mode():
        for start in range(0, len(filtered), batch_size):
            batch = filtered[start : start + batch_size]
            encoded = tokenizer(
                [sample.excerpt for sample in batch],
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=WINDOW_TOKENS,
            )
            if not torch.all(encoded["attention_mask"].sum(dim=1) == WINDOW_TOKENS):
                raise RuntimeError("fixed-window token protocol unexpectedly introduced padding")
            outputs = model(
                **encoded,
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
            current = outputs.hidden_states[-1][:, CURRENT_POSITION, :].to(torch.float32)
            states.append(current.cpu().numpy())

            for horizon in HORIZONS:
                position = CURRENT_POSITION + horizon
                logits = outputs.logits[:, position, :]
                entropy = entropy_from_logits(logits)
                entropy_parts[horizon].append(entropy.cpu().numpy())

                target = encoded["input_ids"][:, position + 1]
                log_probs = torch.log_softmax(logits.to(torch.float32), dim=-1)
                surprisal = -log_probs.gather(1, target[:, None]).squeeze(1)
                surprisal_parts[horizon].append(surprisal.cpu().numpy())
            del outputs

    state_array = normalize_rows(np.concatenate(states, axis=0))
    entropies = {
        h: np.concatenate(parts).astype(float) for h, parts in entropy_parts.items()
    }
    surprisals = {
        h: np.concatenate(parts).astype(float) for h, parts in surprisal_parts.items()
    }
    metadata = {
        "model": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None),
        "hidden_size": int(model.config.hidden_size),
        "num_hidden_layers": int(model.config.num_hidden_layers),
        "observer": f"final-layer causal state at token index {CURRENT_POSITION}",
        "n_samples": int(len(filtered)),
        "sample_paths": [sample.path for sample in filtered],
        "sample_hashes": [sample.excerpt_sha256 for sample in filtered],
    }
    return state_array, entropies, surprisals, metadata


def normalized_laplacian_dense(graph) -> np.ndarray:
    weights = graph.toarray().astype(float)
    degree = weights.sum(axis=1)
    if np.any(degree <= 0):
        raise RuntimeError("representation graph has isolated nodes")
    inv_sqrt = 1.0 / np.sqrt(degree)
    return np.eye(len(degree)) - inv_sqrt[:, None] * weights * inv_sqrt[None, :]


def standardized(values: np.ndarray) -> np.ndarray:
    centered = values - float(np.mean(values))
    scale = float(np.std(centered))
    if scale <= 1e-12:
        raise RuntimeError("observable has effectively zero variance")
    return centered / scale


def rayleigh_energy(laplacian: np.ndarray, values: np.ndarray) -> float:
    z = standardized(values)
    return float((z @ laplacian @ z) / (z @ z))


def low_frequency_power(
    laplacian: np.ndarray, values: np.ndarray, fraction: float = 0.10
) -> tuple[float, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
    order = np.argsort(eigenvalues)
    eigenvectors = eigenvectors[:, order]
    z = standardized(values)
    coefficients = eigenvectors.T @ z
    total = float(np.sum(coefficients**2))
    count = max(1, int(math.ceil(fraction * len(values))))
    # Skip the trivial first eigenvector.
    low = float(np.sum(coefficients[1 : 1 + count] ** 2) / max(total, 1e-12))
    return low, eigenvalues[order]


def permutation_smoothness(
    laplacian: np.ndarray,
    values: np.ndarray,
    *,
    seed: int,
    repeats: int = PERMUTATIONS,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    observed_energy = rayleigh_energy(laplacian, values)
    observed_power, _ = low_frequency_power(laplacian, values)
    null_energy: list[float] = []
    null_power: list[float] = []
    for _ in range(repeats):
        shuffled = rng.permutation(values)
        null_energy.append(rayleigh_energy(laplacian, shuffled))
        null_power.append(low_frequency_power(laplacian, shuffled)[0])
    return {
        "rayleigh_energy": observed_energy,
        "permutation_energy_mean": float(np.mean(null_energy)),
        "permutation_energy_std": float(np.std(null_energy)),
        "energy_lower_tail_p": float(
            (1 + sum(value <= observed_energy for value in null_energy))
            / (repeats + 1)
        ),
        "low_frequency_power_10pct": observed_power,
        "permutation_low_power_mean": float(np.mean(null_power)),
        "low_power_upper_tail_p": float(
            (1 + sum(value >= observed_power for value in null_power))
            / (repeats + 1)
        ),
    }


def deterministic_folds(paths: list[str], folds: int = 5) -> np.ndarray:
    assignments = np.asarray([_stable_int(path + "|fold") % folds for path in paths])
    # Extremely unlikely, but do not silently accept an empty fold.
    if len(set(assignments.tolist())) < folds:
        order = np.argsort([_stable_int(path + "|rebalance") for path in paths])
        assignments = np.empty(len(paths), dtype=int)
        assignments[order] = np.arange(len(paths)) % folds
    return assignments


def weighted_knn_predict(
    train_x: np.ndarray,
    train_y: np.ndarray,
    test_x: np.ndarray,
    k: int = GRAPH_K,
) -> np.ndarray:
    distances = cdist(test_x, train_x)
    k_eff = min(k, len(train_x))
    neighbors = np.argpartition(distances, kth=k_eff - 1, axis=1)[:, :k_eff]
    local_distances = np.take_along_axis(distances, neighbors, axis=1)
    sigma = float(np.median(local_distances))
    sigma = max(sigma, 1e-8)
    weights = np.exp(-(local_distances**2) / (2.0 * sigma**2))
    selected_y = train_y[neighbors]
    return (weights * selected_y).sum(axis=1) / np.clip(
        weights.sum(axis=1), 1e-12, None
    )


def ridge_scalar_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    mean = float(np.mean(train_x))
    scale = float(np.std(train_x)) or 1.0
    z_train = (train_x - mean) / scale
    z_test = (test_x - mean) / scale
    design = np.column_stack([np.ones(len(z_train)), z_train])
    ridge = np.diag([0.0, 1e-3])
    beta = np.linalg.solve(design.T @ design + ridge, design.T @ train_y)
    return np.column_stack([np.ones(len(z_test)), z_test]) @ beta


def cross_validated_prediction(
    states: np.ndarray,
    current_entropy: np.ndarray,
    future_entropy: np.ndarray,
    paths: list[str],
) -> dict[str, float]:
    folds = deterministic_folds(paths)
    knn_predictions = np.empty(len(future_entropy), dtype=float)
    scalar_predictions = np.empty(len(future_entropy), dtype=float)
    mean_predictions = np.empty(len(future_entropy), dtype=float)
    for fold in range(5):
        test = folds == fold
        train = ~test
        knn_predictions[test] = weighted_knn_predict(
            states[train], future_entropy[train], states[test]
        )
        scalar_predictions[test] = ridge_scalar_predict(
            current_entropy[train], future_entropy[train], current_entropy[test]
        )
        mean_predictions[test] = float(np.mean(future_entropy[train]))

    def mse(prediction: np.ndarray) -> float:
        return float(np.mean((prediction - future_entropy) ** 2))

    knn_mse = mse(knn_predictions)
    scalar_mse = mse(scalar_predictions)
    mean_mse = mse(mean_predictions)
    variance = float(np.var(future_entropy))
    return {
        "knn_mse": knn_mse,
        "current_entropy_scalar_mse": scalar_mse,
        "train_mean_mse": mean_mse,
        "knn_vs_current_entropy_ratio": knn_mse / max(scalar_mse, 1e-12),
        "knn_r2_vs_global_mean": 1.0 - knn_mse / max(variance, 1e-12),
    }


def analyze(
    states: np.ndarray,
    entropies: dict[int, np.ndarray],
    surprisals: dict[int, np.ndarray],
    paths: list[str],
) -> dict[str, object]:
    graph, sigma = knn_graph_with_sigma(states, GRAPH_K)
    laplacian = normalized_laplacian_dense(graph)
    scrambled = scramble_features(states, seed=91_337)
    scrambled_graph, _ = knn_graph_with_sigma(scrambled, GRAPH_K)
    scrambled_laplacian = normalized_laplacian_dense(scrambled_graph)

    horizons: dict[str, object] = {}
    for horizon in HORIZONS:
        entropy = entropies[horizon]
        smoothness = permutation_smoothness(
            laplacian, entropy, seed=10_000 + horizon
        )
        smoothness["scrambled_representation_energy"] = rayleigh_energy(
            scrambled_laplacian, entropy
        )
        smoothness["observed_vs_scrambled_energy_ratio"] = (
            smoothness["rayleigh_energy"]
            / max(smoothness["scrambled_representation_energy"], 1e-12)
        )
        prediction = cross_validated_prediction(
            states, entropies[0], entropy, paths
        )
        surprisal_smoothness = permutation_smoothness(
            laplacian, surprisals[horizon], seed=20_000 + horizon
        )
        horizons[str(horizon)] = {
            "entropy": smoothness,
            "entropy_prediction": prediction,
            "target_surprisal": surprisal_smoothness,
            "entropy_mean": float(np.mean(entropy)),
            "entropy_std": float(np.std(entropy)),
            "target_surprisal_mean": float(np.mean(surprisals[horizon])),
        }

    h0 = horizons["0"]["entropy"]
    primary = horizons[str(PRIMARY_HORIZON)]
    gates = {
        "current_entropy_positive_control": h0["energy_lower_tail_p"] <= 0.05,
        "future_entropy_spectral_smoothness": primary["entropy"][
            "energy_lower_tail_p"
        ]
        <= 0.05,
        "future_entropy_low_frequency_enrichment": primary["entropy"][
            "low_power_upper_tail_p"
        ]
        <= 0.05,
        "future_entropy_beats_scalar_baseline": primary["entropy_prediction"][
            "knn_vs_current_entropy_ratio"
        ]
        <= 0.95,
        "future_entropy_beats_scrambled_geometry": primary["entropy"][
            "observed_vs_scrambled_energy_ratio"
        ]
        <= 0.95,
    }
    return {
        "graph_kernel_sigma": sigma,
        "horizons": horizons,
        "gates": gates,
        "supported": all(gates.values()),
    }


def write_outputs(output: Path, result: dict[str, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = [
        {"path": path, "excerpt_sha256": digest}
        for path, digest in zip(
            result["model"]["sample_paths"], result["model"]["sample_hashes"]
        )
    ]
    (output / "sample_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Natural-text future-entropy spectral test",
        "",
        f"**Primary H=8 hypothesis supported:** `{result['analysis']['supported']}`",
        "",
        f"- model: `{result['model']['model']}`",
        f"- revision: `{result['model']['resolved_revision']}`",
        f"- natural files: `{result['model']['n_samples']}`",
        f"- fixed token window: `{WINDOW_TOKENS}`",
        f"- observed state position: `{CURRENT_POSITION}`",
        f"- graph k: `{GRAPH_K}`",
        "",
        "## Horizons",
        "",
        "| H | entropy energy | perm p | low-freq power | low-freq p | kNN/scalar MSE | scrambled ratio |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for horizon in HORIZONS:
        item = result["analysis"]["horizons"][str(horizon)]
        e = item["entropy"]
        p = item["entropy_prediction"]
        lines.append(
            f"| {horizon} | {e['rayleigh_energy']:.4f} | "
            f"{e['energy_lower_tail_p']:.4f} | {e['low_frequency_power_10pct']:.4f} | "
            f"{e['low_power_upper_tail_p']:.4f} | {p['knn_vs_current_entropy_ratio']:.4f} | "
            f"{e['observed_vs_scrambled_energy_ratio']:.4f} |"
        )
    lines.extend(["", "## Primary gates", ""])
    lines.extend(
        f"- {'PASS' if passed else 'FAIL'} — `{name}`"
        for name, passed in result["analysis"]["gates"].items()
    )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "This test uses no hand-labelled semantic classes. A positive H=8 result would show that the final causal representation graph at t contains structure predictive of the model's own uncertainty after eight additional natural-text tokens, beyond a scalar current-entropy baseline. It would not by itself establish manifolds, causal control, or observer-independent geometry.",
            "",
        ]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    samples = collect_samples(repo_root)
    if len(samples) < MIN_FILES:
        raise RuntimeError(
            f"only {len(samples)} eligible natural Markdown files; need {MIN_FILES}"
        )

    states, entropies, surprisals, model_metadata = extract_states_and_observables(
        samples,
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
    )
    analysis = analyze(
        states,
        entropies,
        surprisals,
        model_metadata["sample_paths"],
    )
    result: dict[str, object] = {
        "claim_boundary": (
            "Natural-text, label-free future-uncertainty experiment after falsification "
            "of the fresh relative-depth semantic-bottleneck confirmation."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
        "protocol": {
            "source": "eligible Markdown prose already versioned in this repository",
            "one_excerpt_per_file": True,
            "max_files": MAX_FILES,
            "min_files": MIN_FILES,
            "words_per_excerpt_before_tokenization": WORDS_PER_EXCERPT,
            "window_tokens": WINDOW_TOKENS,
            "current_position": CURRENT_POSITION,
            "horizons": list(HORIZONS),
            "primary_horizon": PRIMARY_HORIZON,
            "graph_k": GRAPH_K,
            "permutations": PERMUTATIONS,
            "observer": "final-layer causal hidden state at current position",
            "baseline": "5-fold scalar ridge using current predictive entropy only",
        },
        "model": model_metadata,
        "analysis": analysis,
    }
    write_outputs(Path(args.output), result)
    print(
        json.dumps(
            {
                "model": result["model"],
                "gates": analysis["gates"],
                "supported": analysis["supported"],
                "primary": analysis["horizons"][str(PRIMARY_HORIZON)],
            },
            indent=2,
        )
    )
    # Scientific negative exits 0 by design.


if __name__ == "__main__":
    main()
