#!/usr/bin/env python3
"""Real-model smoke test for semantic spectral bottlenecks.

This deliberately small CPU experiment extracts hidden states from a frozen
compact language model, builds label-blind kNN/Laplacian geometry on training
sentences, and asks whether the learned Fiedler coordinate extends to held-out
contexts and held-out paraphrases.

A positive result is evidence that the measurement pipeline finds reproducible
semantic structure in one small model. It is not evidence for universal concept
manifolds, causal steering advantage, or the full Semantic Atlas.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import scipy
import torch
import transformers
from scipy.sparse import csr_matrix, diags, eye
from scipy.sparse.linalg import eigsh
from scipy.spatial.distance import cdist
from transformers import AutoModelForCausalLM, AutoTokenizer

from experiment import conductance

MODEL_DEFAULT = "HuggingFaceTB/SmolLM2-135M"


@dataclass(frozen=True)
class Example:
    axis: str
    split: str
    context_id: str
    phrase_id: str
    label: int
    text: str


@dataclass(frozen=True)
class AxisSpec:
    name: str
    template: str
    contexts: tuple[tuple[str, str], ...]
    negative: tuple[str, ...]
    bridge: tuple[str, ...]
    positive: tuple[str, ...]


AXES: tuple[AxisSpec, ...] = (
    AxisSpec(
        name="approval",
        template="{actor} {predicate} {obj} after reviewing the available evidence.",
        contexts=(
            ("The committee", "the proposal"),
            ("The review panel", "the submission"),
            ("The board", "the revised plan"),
            ("The editor", "the manuscript"),
            ("The council", "the funding request"),
            ("The jury", "the recommendation"),
            ("The auditors", "the remediation plan"),
            ("The delegates", "the draft agreement"),
            ("The faculty senate", "the curriculum change"),
            ("The ethics panel", "the protocol amendment"),
            ("The neighborhood group", "the zoning request"),
            ("The technical reviewers", "the deployment proposal"),
        ),
        negative=(
            "decisively rejected",
            "strongly opposed",
            "firmly disapproved of",
            "declined to support",
            "expressly voted against",
            "concluded it should be refused",
        ),
        bridge=(
            "remained divided over",
            "withheld a final judgment on",
            "expressed mixed views about",
            "considered arguments on both sides of",
            "left the decision unresolved on",
            "gave only conditional support to",
        ),
        positive=(
            "decisively endorsed",
            "strongly supported",
            "firmly approved",
            "agreed to back",
            "expressly voted for",
            "concluded it should be accepted",
        ),
    ),
    AxisSpec(
        name="certainty",
        template="{actor} described {obj} as {predicate} after examining the record.",
        contexts=(
            ("The scientist", "the causal explanation"),
            ("The analyst", "the demand forecast"),
            ("The physician", "the working diagnosis"),
            ("The investigator", "the proposed timeline"),
            ("The engineer", "the failure mechanism"),
            ("The historian", "the source attribution"),
            ("The statistician", "the estimated effect"),
            ("The inspector", "the reported defect"),
            ("The meteorologist", "the storm projection"),
            ("The archaeologist", "the dating hypothesis"),
            ("The economist", "the inflation estimate"),
            ("The examiner", "the identification result"),
        ),
        negative=(
            "highly uncertain",
            "poorly established",
            "too doubtful to rely on",
            "unsupported by a firm conclusion",
            "still subject to serious uncertainty",
            "far from conclusively demonstrated",
        ),
        bridge=(
            "plausible but unresolved",
            "supported only provisionally",
            "neither confirmed nor ruled out",
            "consistent with several interpretations",
            "credible but still open to revision",
            "balanced between confirming and contrary evidence",
        ),
        positive=(
            "highly certain",
            "well established",
            "reliable enough to accept",
            "supported by a firm conclusion",
            "no longer subject to serious uncertainty",
            "conclusively demonstrated",
        ),
    ),
    AxisSpec(
        name="direction",
        template="{actor} reported that {obj} was {predicate} over the observed interval.",
        contexts=(
            ("The operations team", "system demand"),
            ("The market report", "customer activity"),
            ("The ecology survey", "the local population"),
            ("The hospital dashboard", "patient volume"),
            ("The transport study", "daily ridership"),
            ("The energy monitor", "power consumption"),
            ("The staffing review", "workforce size"),
            ("The school report", "student enrollment"),
            ("The housing survey", "available inventory"),
            ("The network monitor", "packet traffic"),
            ("The production log", "factory output"),
            ("The water authority", "reservoir storage"),
        ),
        negative=(
            "falling rapidly",
            "steadily contracting",
            "clearly declining",
            "moving downward overall",
            "shrinking at a sustained pace",
            "ending substantially below its starting level",
        ),
        bridge=(
            "roughly stable",
            "fluctuating without a clear direction",
            "nearly unchanged overall",
            "alternating between gains and losses",
            "showing no sustained trend",
            "ending close to its starting level",
        ),
        positive=(
            "rising rapidly",
            "steadily expanding",
            "clearly increasing",
            "moving upward overall",
            "growing at a sustained pace",
            "ending substantially above its starting level",
        ),
    ),
)


def build_corpus() -> list[Example]:
    """Freeze train/test by both context and paraphrase family."""
    rows: list[Example] = []
    for spec in AXES:
        phrase_groups = ((-1, spec.negative), (0, spec.bridge), (1, spec.positive))
        for split, context_slice, phrase_slice in (
            ("train", range(0, 8), range(0, 4)),
            ("test", range(8, 12), range(4, 6)),
        ):
            for context_index in context_slice:
                actor, obj = spec.contexts[context_index]
                for label, phrases in phrase_groups:
                    for phrase_index in phrase_slice:
                        rows.append(
                            Example(
                                axis=spec.name,
                                split=split,
                                context_id=f"{spec.name}-c{context_index}",
                                phrase_id=f"{spec.name}-l{label}-p{phrase_index}",
                                label=label,
                                text=spec.template.format(
                                    actor=actor,
                                    predicate=phrases[phrase_index],
                                    obj=obj,
                                ),
                            )
                        )
    return rows


def normalize_rows(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.clip(norms, 1e-12, None)


def knn_graph_with_sigma(points: np.ndarray, k: int) -> tuple[csr_matrix, float]:
    if not 2 <= k < len(points):
        raise ValueError("k must be >= 2 and smaller than the sample size")
    distances = cdist(points, points)
    np.fill_diagonal(distances, np.inf)
    neighbors = np.argpartition(distances, kth=k - 1, axis=1)[:, :k]
    local = np.take_along_axis(distances, neighbors, axis=1)
    sigma = float(np.median(local[np.isfinite(local)]))
    if sigma <= 0:
        raise ValueError("non-positive graph kernel scale")
    rows = np.repeat(np.arange(len(points)), k)
    cols = neighbors.ravel()
    edge_distances = distances[rows, cols]
    weights = np.exp(-(edge_distances**2) / (2.0 * sigma**2))
    directed = csr_matrix((weights, (rows, cols)), shape=(len(points), len(points)))
    graph = directed.maximum(directed.T)
    graph.setdiag(0.0)
    graph.eliminate_zeros()
    return graph, sigma


def spectral_coordinate(
    graph: csr_matrix, min_fraction: float = 0.20
) -> tuple[float, float, np.ndarray, np.ndarray]:
    n = graph.shape[0]
    degree = np.asarray(graph.sum(axis=1)).ravel()
    if np.any(degree <= 0):
        raise ValueError("graph contains isolated vertices")
    inv_sqrt = 1.0 / np.sqrt(degree)
    laplacian = eye(n, format="csr") - diags(inv_sqrt) @ graph @ diags(inv_sqrt)
    values, vectors = eigsh(
        laplacian,
        k=3,
        which="SM",
        tol=1e-8,
        v0=np.ones(n, dtype=float),
    )
    order = np.argsort(values)
    lambda2 = float(values[order[1]])
    fiedler = vectors[:, order[1]].astype(float)

    sorted_nodes = np.argsort(fiedler)
    lower = max(1, int(math.ceil(min_fraction * n)))
    upper = min(n - 1, int(math.floor((1.0 - min_fraction) * n)))
    best_phi = float("inf")
    best_mask: np.ndarray | None = None
    for size in range(lower, upper + 1):
        mask = np.zeros(n, dtype=bool)
        mask[sorted_nodes[:size]] = True
        phi = conductance(graph, mask)
        if phi < best_phi:
            best_phi = phi
            best_mask = mask
    if best_mask is None:
        raise RuntimeError("no admissible Fiedler sweep cut")
    return lambda2, float(best_phi), fiedler, best_mask


def orient_fiedler(fiedler: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, float]:
    pole = labels != 0
    positive_mean = float(np.mean(fiedler[labels == 1]))
    negative_mean = float(np.mean(fiedler[labels == -1]))
    sign = 1.0 if positive_mean >= negative_mean else -1.0
    oriented = sign * fiedler
    prediction = np.where(oriented[pole] >= 0.0, 1, -1)
    return oriented, float(np.mean(prediction == labels[pole]))


def weighted_extension(
    train: np.ndarray,
    train_scores: np.ndarray,
    test: np.ndarray,
    *,
    k: int,
    sigma: float,
) -> np.ndarray:
    distances = cdist(test, train)
    neighbors = np.argpartition(distances, kth=k - 1, axis=1)[:, :k]
    selected_distances = np.take_along_axis(distances, neighbors, axis=1)
    selected_scores = train_scores[neighbors]
    weights = np.exp(-(selected_distances**2) / (2.0 * sigma**2))
    weight_sum = np.clip(weights.sum(axis=1), 1e-12, None)
    return (weights * selected_scores).sum(axis=1) / weight_sum


def pole_accuracy(scores: np.ndarray, labels: np.ndarray) -> float:
    pole = labels != 0
    prediction = np.where(scores[pole] >= 0.0, 1, -1)
    return float(np.mean(prediction == labels[pole]))


def bridge_ratio(scores: np.ndarray, labels: np.ndarray) -> float:
    bridge = labels == 0
    pole = labels != 0
    denominator = float(np.median(np.abs(scores[pole])))
    if denominator <= 1e-12:
        return float("inf")
    return float(np.median(np.abs(scores[bridge])) / denominator)


def centroid_accuracy(
    train: np.ndarray,
    train_labels: np.ndarray,
    test: np.ndarray,
    test_labels: np.ndarray,
) -> float:
    negative = normalize_rows(train[train_labels == -1].mean(axis=0, keepdims=True))[0]
    positive = normalize_rows(train[train_labels == 1].mean(axis=0, keepdims=True))[0]
    pole = test_labels != 0
    samples = normalize_rows(test[pole])
    score = samples @ positive - samples @ negative
    prediction = np.where(score >= 0.0, 1, -1)
    return float(np.mean(prediction == test_labels[pole]))


def shuffled_label_accuracy(
    scores: np.ndarray, labels: np.ndarray, seed: int, repeats: int = 100
) -> float:
    rng = np.random.default_rng(seed)
    pole = labels != 0
    true = labels[pole].copy()
    pred = np.where(scores[pole] >= 0.0, 1, -1)
    return float(np.mean([np.mean(pred == rng.permutation(true)) for _ in range(repeats)]))


def scramble_features(values: np.ndarray, seed: int) -> np.ndarray:
    """Destroy row-level geometry while preserving each feature marginal."""
    rng = np.random.default_rng(seed)
    scrambled = values.copy()
    for column in range(scrambled.shape[1]):
        scrambled[:, column] = scrambled[rng.permutation(len(scrambled)), column]
    return normalize_rows(scrambled)


def configure_padding(tokenizer, model) -> str:
    """Use EOS only for masked batch padding when a causal tokenizer has no PAD."""
    if tokenizer.pad_token_id is None:
        if tokenizer.eos_token_id is None:
            raise ValueError("tokenizer defines neither pad_token nor eos_token")
        tokenizer.pad_token = tokenizer.eos_token
        strategy = "eos_as_masked_padding"
    else:
        strategy = "native_pad_token"
    if getattr(model.config, "pad_token_id", None) is None:
        model.config.pad_token_id = tokenizer.pad_token_id
    return strategy


def extract_representations(
    texts: list[str],
    model_name: str,
    revision: str,
    batch_size: int,
    max_length: int,
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision)
    padding_strategy = configure_padding(tokenizer, model)
    model.eval()
    model.to("cpu")
    torch.set_grad_enabled(False)

    layer_count = int(model.config.num_hidden_layers)
    selected = {
        "embedding": 0,
        "early": max(1, int(round(layer_count * 0.25))),
        "mid": max(1, int(round(layer_count * 0.50))),
        "final": layer_count,
    }
    storage: dict[str, list[np.ndarray]] = {name: [] for name in selected}

    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[start : start + batch_size],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )
        outputs = model(
            **encoded,
            output_hidden_states=True,
            use_cache=False,
            return_dict=True,
        )
        mask = encoded["attention_mask"].unsqueeze(-1).to(torch.float32)
        denom = mask.sum(dim=1).clamp_min(1.0)
        for name, index in selected.items():
            hidden = outputs.hidden_states[index].to(torch.float32)
            pooled = (hidden * mask).sum(dim=1) / denom
            storage[name].append(pooled.cpu().numpy())
        del outputs

    arrays = {
        name: normalize_rows(np.concatenate(parts, axis=0))
        for name, parts in storage.items()
    }
    metadata = {
        "model": model_name,
        "requested_revision": revision,
        "resolved_revision": getattr(model.config, "_commit_hash", None),
        "model_type": getattr(model.config, "model_type", None),
        "hidden_size": int(model.config.hidden_size),
        "num_hidden_layers": layer_count,
        "selected_hidden_state_indices": selected,
        "pooling": "attention-mask weighted token mean, then L2 normalization",
        "padding_strategy": padding_strategy,
    }
    return arrays, metadata


def axis_indices(corpus: list[Example], axis: str, split: str) -> np.ndarray:
    return np.asarray(
        [i for i, row in enumerate(corpus) if row.axis == axis and row.split == split],
        dtype=int,
    )


def evaluate_one(
    embeddings: np.ndarray,
    corpus: list[Example],
    axis: str,
    layer: str,
    k: int,
) -> dict[str, object]:
    train_idx = axis_indices(corpus, axis, "train")
    test_idx = axis_indices(corpus, axis, "test")
    train = embeddings[train_idx]
    test = embeddings[test_idx]
    train_labels = np.asarray([corpus[i].label for i in train_idx], dtype=int)
    test_labels = np.asarray([corpus[i].label for i in test_idx], dtype=int)

    graph, sigma = knn_graph_with_sigma(train, k)
    lambda2, phi, fiedler, _ = spectral_coordinate(graph)
    oriented, train_accuracy = orient_fiedler(fiedler, train_labels)
    test_scores = weighted_extension(train, oriented, test, k=k, sigma=sigma)

    scrambled_train = scramble_features(train, seed=71_000 + k)
    scrambled_test = scramble_features(test, seed=91_000 + k)
    scrambled_graph, scrambled_sigma = knn_graph_with_sigma(scrambled_train, k)
    _, _, scrambled_fiedler, _ = spectral_coordinate(scrambled_graph)
    scrambled_oriented, _ = orient_fiedler(scrambled_fiedler, train_labels)
    scrambled_scores = weighted_extension(
        scrambled_train,
        scrambled_oriented,
        scrambled_test,
        k=k,
        sigma=scrambled_sigma,
    )

    return {
        "axis": axis,
        "layer": layer,
        "k": k,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "lambda2": lambda2,
        "conductance": phi,
        "train_pole_accuracy": train_accuracy,
        "heldout_pole_accuracy": pole_accuracy(test_scores, test_labels),
        "heldout_bridge_abs_score_ratio": bridge_ratio(test_scores, test_labels),
        "centroid_heldout_accuracy": centroid_accuracy(
            train, train_labels, test, test_labels
        ),
        "shuffled_label_accuracy": shuffled_label_accuracy(
            test_scores, test_labels, seed=31_000 + k
        ),
        "scrambled_representation_accuracy": pole_accuracy(
            scrambled_scores, test_labels
        ),
    }


def median(records: list[dict[str, object]], key: str) -> float:
    return float(np.median([float(record[key]) for record in records]))


def aggregate_result(records: list[dict[str, object]]) -> dict[str, object]:
    registered = [record for record in records if record["layer"] == "mid"]
    axes = sorted({str(record["axis"]) for record in registered})
    axis_accuracy = {
        axis: median(
            [record for record in registered if record["axis"] == axis],
            "heldout_pole_accuracy",
        )
        for axis in axes
    }
    robust_flags = [
        float(record["heldout_pole_accuracy"]) >= 0.65
        and float(record["heldout_bridge_abs_score_ratio"]) <= 0.95
        and float(record["scrambled_representation_accuracy"]) <= 0.70
        for record in registered
    ]
    aggregate = {
        "registered_layer": "mid",
        "median_heldout_pole_accuracy": median(registered, "heldout_pole_accuracy"),
        "median_bridge_abs_score_ratio": median(
            registered, "heldout_bridge_abs_score_ratio"
        ),
        "median_centroid_heldout_accuracy": median(
            registered, "centroid_heldout_accuracy"
        ),
        "median_shuffled_label_accuracy": median(
            registered, "shuffled_label_accuracy"
        ),
        "median_scrambled_representation_accuracy": median(
            registered, "scrambled_representation_accuracy"
        ),
        "median_conductance": median(registered, "conductance"),
        "median_lambda2": median(registered, "lambda2"),
        "robust_axis_k_fraction": float(np.mean(robust_flags)),
        "axis_median_heldout_accuracy": axis_accuracy,
    }
    gates = {
        "heldout_semantic_partition": aggregate["median_heldout_pole_accuracy"] >= 0.70,
        "bridges_near_spectral_boundary": aggregate[
            "median_bridge_abs_score_ratio"
        ]
        <= 0.85,
        "shuffled_labels_near_chance": aggregate["median_shuffled_label_accuracy"]
        <= 0.58,
        "scrambled_geometry_near_chance": aggregate[
            "median_scrambled_representation_accuracy"
        ]
        <= 0.65,
        "not_driven_by_one_axis": min(axis_accuracy.values()) >= 0.60,
        "robust_across_axis_and_k": aggregate["robust_axis_k_fraction"] >= 0.60,
    }
    return {
        "aggregate": aggregate,
        "gates": gates,
        "supported": all(gates.values()),
    }


def write_outputs(
    output: Path,
    result: dict[str, object],
    corpus: list[Example],
    embeddings: dict[str, np.ndarray],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "corpus.json").write_text(
        json.dumps([asdict(row) for row in corpus], indent=2) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(output / "registered-mid-embeddings.npz", mid=embeddings["mid"])

    a = result["aggregate"]
    g = result["gates"]
    lines = [
        "# Real-model semantic spectral bottleneck smoke",
        "",
        f"**Hypothesis supported by registered smoke gates:** `{result['supported']}`",
        "",
        result["claim_boundary"],
        "",
        "## Registered aggregate (mid layer)",
        "",
        f"- held-out pole accuracy: `{a['median_heldout_pole_accuracy']:.4f}`",
        f"- bridge |Fiedler-extension| / pole ratio: `{a['median_bridge_abs_score_ratio']:.4f}`",
        f"- supervised centroid held-out accuracy: `{a['median_centroid_heldout_accuracy']:.4f}`",
        f"- shuffled-label accuracy: `{a['median_shuffled_label_accuracy']:.4f}`",
        f"- scrambled-representation accuracy: `{a['median_scrambled_representation_accuracy']:.4f}`",
        f"- robust axis×k fraction: `{a['robust_axis_k_fraction']:.4f}`",
        "",
        "### Per-axis held-out accuracy",
        "",
    ]
    for axis, value in a["axis_median_heldout_accuracy"].items():
        lines.append(f"- {axis}: `{value:.4f}`")
    lines.extend(["", "## Gates", ""])
    lines.extend(f"- {'PASS' if ok else 'FAIL'} — `{name}`" for name, ok in g.items())
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            (
                "This run uses a frozen compact LLM and genuinely held-out contexts and "
                "paraphrases, so it is stronger than the planted synthetic smoke. It still "
                "does not establish natural-corpus manifold structure, causal steering "
                "cost, cross-model portability, or the full Semantic Atlas hypothesis."
            ),
            "",
        ]
    )
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def parse_int_list(raw: str) -> list[int]:
    values = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("empty integer list")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_DEFAULT)
    parser.add_argument("--revision", default="main")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=64)
    parser.add_argument("--k-values", default="6,10,14")
    parser.add_argument("--output", default="results-real")
    args = parser.parse_args()

    corpus = build_corpus()
    representations, model_metadata = extract_representations(
        [row.text for row in corpus],
        model_name=args.model,
        revision=args.revision,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    ks = parse_int_list(args.k_values)
    records = [
        evaluate_one(representations[layer], corpus, axis.name, layer, k)
        for layer in ("embedding", "early", "mid", "final")
        for axis in AXES
        for k in ks
    ]
    aggregated = aggregate_result(records)
    result: dict[str, object] = {
        "claim_boundary": (
            "Frozen-small-model controlled-corpus smoke test. A positive result shows "
            "that label-blind spectral geometry can generalize across held-out contexts "
            "and paraphrases in this model; it does not establish universal semantic "
            "manifolds or causal navigation advantage."
        ),
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
        },
        "model": model_metadata,
        "design": {
            "axes": [axis.name for axis in AXES],
            "train_contexts_per_axis": 8,
            "heldout_contexts_per_axis": 4,
            "train_paraphrases_per_class": 4,
            "heldout_paraphrases_per_class": 2,
            "k_values": ks,
            "graph": "L2-normalized hidden-state mean; symmetric Gaussian weighted kNN",
            "spectral_operator": "normalized graph Laplacian",
            "cut": "label-blind balanced Fiedler sweep on training states",
            "out_of_sample": "Gaussian-weighted local extension of oriented training Fiedler coordinate",
            "registered_layer": "mid (50% hidden-state depth)",
            "controls": [
                "held-out context and paraphrase split",
                "shuffled endpoint labels",
                "feature-marginal-preserving row-geometry scramble",
                "supervised centroid baseline",
                "embedding/early/final layer descriptive comparisons",
            ],
        },
        "aggregate": aggregated["aggregate"],
        "gates": aggregated["gates"],
        "supported": aggregated["supported"],
        "records": records,
    }
    write_outputs(Path(args.output), result, corpus, representations)
    print(
        json.dumps(
            {
                "model": result["model"],
                "aggregate": result["aggregate"],
                "gates": result["gates"],
                "supported": result["supported"],
            },
            indent=2,
        )
    )
    # Negative scientific gates intentionally exit 0. Runtime errors still fail CI.


if __name__ == "__main__":
    main()
