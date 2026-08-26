from __future__ import annotations

import argparse
import functools
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from semantic_atlas.embedding_cache import write_embedding_cache
from semantic_atlas.gallery_scale import (
    aggregate_curve,
    apply_static_gate,
    deterministic_subset,
    local_rankings,
    markdown_format_view,
    permutation_calibration,
)
from semantic_atlas.relational_dynamics import l2_normalize


@functools.lru_cache(maxsize=1)
def _repo_root() -> str:
    here = Path(__file__).resolve().parent
    return subprocess.check_output(
        ["git", "-C", str(here), "rev-parse", "--show-toplevel"], text=True
    ).strip()


def _git_paths(commit: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", _repo_root(), "ls-tree", "-r", "--name-only", commit],
        text=True,
    )
    paths = [line.strip() for line in output.splitlines() if line.strip().endswith(".md")]
    return sorted(paths, key=lambda path: hashlib.sha256(path.encode("utf-8")).hexdigest())


def _git_text(commit: str, path: str, limit: int) -> str:
    raw = subprocess.check_output(["git", "-C", _repo_root(), "show", f"{commit}:{path}"])
    return raw.decode("utf-8", errors="replace").strip()[:limit]


def _first_touch_unix(commit: str, path: str) -> int:
    output = subprocess.check_output(
        ["git", "-C", _repo_root(), "log", "--follow", "--format=%ct", commit, "--", path],
        text=True,
    )
    rows = [line.strip() for line in output.splitlines() if line.strip()]
    if not rows:
        raise RuntimeError(f"no git history for corpus path: {path}")
    return int(rows[-1])


def _load_sentence_model(spec: dict):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(spec["model"], revision=spec["revision"])


def _encode_raw(model, texts: list[str]) -> np.ndarray:
    return np.asarray(
        model.encode(texts, convert_to_numpy=True, normalize_embeddings=False),
        dtype=np.float64,
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _cache_view(
    cache_dir: Path,
    *,
    observer: dict,
    source_commit: str,
    paths: list[str],
    texts: list[str],
    raw: np.ndarray,
) -> dict:
    normalized = l2_normalize(raw)
    ref = write_embedding_cache(
        cache_dir,
        observer=observer,
        source_commit=source_commit,
        paths_by_split={"gallery": paths},
        texts_by_split={"gallery": texts},
        raw_by_split={"gallery": raw},
        normalized_by_split={"gallery": normalized},
    )
    return {
        "matrix": normalized,
        "manifest": str(ref.manifest_path),
        "data": str(ref.data_path),
        "data_sha256": ref.data_sha256,
        "corpus_sha256": ref.corpus_sha256,
    }


def _pair_rows(
    matrices: dict[str, np.ndarray],
    paths: list[str],
    manifest: dict,
) -> list[dict]:
    gallery = manifest["gallery"]
    sizes = [int(value) for value in gallery["sizes"]]
    ks = [int(value) for value in gallery["ks"]]
    subset_replicates = int(gallery["subset_replicates"])
    subset_seed = int(gallery["subset_seed"])
    null_permutations = int(gallery["correspondence_null_permutations"])
    null_seed = int(gallery["correspondence_null_seed"])
    pairs = {
        "cross_model": ("reference_markdown", "transfer_markdown"),
        "reference_format_stability": ("reference_markdown", "reference_plain"),
        "transfer_format_stability": ("transfer_markdown", "transfer_plain"),
    }

    rows: list[dict] = []
    for size in sizes:
        replicates = 1 if size == len(paths) else subset_replicates
        for replicate in range(replicates):
            subset = deterministic_subset(paths, size, replicate, subset_seed)
            rankings = {
                name: local_rankings(matrix, subset) for name, matrix in matrices.items()
            }
            rng = np.random.default_rng(
                np.random.SeedSequence([null_seed, size, replicate])
            )
            permutations = [rng.permutation(size) for _ in range(null_permutations)]
            subset_sha256 = hashlib.sha256(
                "\n".join(paths[index] for index in subset).encode("utf-8")
            ).hexdigest()
            for pair, (left, right) in pairs.items():
                calibrated = permutation_calibration(
                    rankings[left], rankings[right], ks=ks, permutations=permutations
                )
                for k in ks:
                    rows.append(
                        {
                            "gallery_n": size,
                            "replicate": replicate,
                            "subset_sha256": subset_sha256,
                            "pair": pair,
                            "k": k,
                            **calibrated[str(k)],
                        }
                    )
    return rows


def _write_figure(aggregated: list[dict], gate_result: dict, output: Path) -> None:
    import matplotlib.pyplot as plt

    pairs = {
        "cross_model": ("cross-model", "#1f77b4"),
        "reference_format_stability": ("Qwen format stability", "#2ca02c"),
        "transfer_format_stability": ("MiniLM format stability", "#ff7f0e"),
    }

    def series(pair: str, k: int, metric: str):
        rows = sorted(
            (
                row
                for row in aggregated
                if row["pair"] == pair and int(row["k"]) == k
            ),
            key=lambda row: row["gallery_n"],
        )
        x = np.asarray([row["gallery_n"] for row in rows])
        y = np.asarray([row[metric]["median"] for row in rows])
        low = np.asarray([row[metric]["q10"] for row in rows])
        high = np.asarray([row[metric]["q90"] for row in rows])
        return x, y, low, high

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for k, color in ((3, "#9467bd"), (5, "#1f77b4"), (10, "#d62728")):
        for axis, metric, title in (
            (axes[0], "raw_mknn", "Raw cross-model mKNN"),
            (axes[1], "calibrated_mknn", "Permutation-calibrated mKNN"),
        ):
            x, y, low, high = series("cross_model", k, metric)
            axis.plot(x, y, marker="o", label=f"k={k}", color=color)
            axis.fill_between(x, low, high, alpha=0.14, color=color)
            axis.set_title(title)
            axis.set_xscale("log")
            axis.set_xlabel("gallery N")
            axis.set_ylim(0, 1)
            axis.grid(alpha=0.25)

    for pair, (label, color) in pairs.items():
        x, y, low, high = series(pair, 5, "calibrated_mknn")
        axes[2].plot(x, y, marker="o", label=label, color=color)
        axes[2].fill_between(x, low, high, alpha=0.12, color=color)
    axes[2].set_title(f"Primary gate: {gate_result['decision']}")
    axes[2].set_xscale("log")
    axes[2].set_xlabel("gallery N")
    axes[2].set_ylim(0, 1)
    axes[2].grid(alpha=0.25)
    for axis in axes:
        axis.legend(fontsize=8)
    axes[0].set_ylabel("mKNN")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def run(manifest_path: Path, protocol_path: Path, output_path: Path, cache_dir: Path, figure: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_commit = str(manifest["source_commit"])
    paths = _git_paths(source_commit)
    expected = int(manifest["corpus"]["expected_document_count"])
    if len(paths) != expected:
        raise RuntimeError(
            f"frozen corpus mismatch: expected {expected} markdown files, found {len(paths)}"
        )
    excerpt_chars = int(manifest["corpus"]["excerpt_chars"])
    markdown_texts = [_git_text(source_commit, path, excerpt_chars) for path in paths]
    if any(len(text) != excerpt_chars for text in markdown_texts):
        raise RuntimeError("every frozen corpus document must fill the excerpt window")
    plain_texts = [markdown_format_view(text) for text in markdown_texts]
    if any(not text for text in plain_texts):
        raise RuntimeError("format perturbation produced an empty document")

    matrices: dict[str, np.ndarray] = {}
    cache_refs = {}
    for prefix, observer_key in (
        ("reference", "reference_observer"),
        ("transfer", "transfer_observer"),
    ):
        observer = manifest[observer_key]
        model = _load_sentence_model(observer)
        raw_markdown = _encode_raw(model, markdown_texts)
        raw_plain = _encode_raw(model, plain_texts)
        for view, texts, raw in (
            ("markdown", markdown_texts, raw_markdown),
            ("plain", plain_texts, raw_plain),
        ):
            cached = _cache_view(
                cache_dir / f"{prefix}_observer" / view,
                observer={**observer, "text_view": view},
                source_commit=source_commit,
                paths=paths,
                texts=texts,
                raw=raw,
            )
            matrices[f"{prefix}_{view}"] = cached.pop("matrix")
            cache_refs[f"{prefix}_{view}"] = cached
        del model, raw_markdown, raw_plain

    rows = _pair_rows(matrices, paths, manifest)
    aggregated = aggregate_curve(rows)
    gate = dict(manifest["gate"])
    gate_result = apply_static_gate(aggregated, gate)
    chronology = [
        {
            "path": path,
            "path_sha256": hashlib.sha256(path.encode("utf-8")).hexdigest(),
            "excerpt_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "first_touch_unix": _first_touch_unix(source_commit, path),
        }
        for path, text in zip(paths, markdown_texts, strict=True)
    ]
    result = {
        "schema_version": 1,
        "experiment": manifest["experiment"],
        "executed_at": datetime.now(UTC).isoformat(),
        "source_commit": source_commit,
        "manifest_sha256": _sha256(manifest_path),
        "protocol_sha256": _sha256(protocol_path),
        "corpus": {
            "document_count": len(paths),
            "excerpt_chars": excerpt_chars,
            "first_touch_min": min(row["first_touch_unix"] for row in chronology),
            "first_touch_max": max(row["first_touch_unix"] for row in chronology),
            "documents": chronology,
        },
        "observers": {
            "reference": manifest["reference_observer"],
            "transfer": manifest["transfer_observer"],
        },
        "same_observer_stability": manifest["same_observer_stability"],
        "cache_refs": cache_refs,
        "replicate_rows": rows,
        "aggregated_curve": aggregated,
        "gate": gate_result,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_figure(aggregated, gate_result, figure)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("gallery_scale_v1.json"))
    parser.add_argument("--protocol", type=Path, default=Path("protocol_gallery_scale_v1.md"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/gallery_scale_v1.json"))
    parser.add_argument("--cache-dir", type=Path, default=Path("artifacts/embedding_cache_gallery_scale_v1"))
    parser.add_argument("--figure", type=Path, default=Path("artifacts/gallery_scale_v1.png"))
    args = parser.parse_args()
    result = run(args.manifest, args.protocol, args.output, args.cache_dir, args.figure)
    print(json.dumps(result["gate"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
