from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from semantic_atlas.scale_results import aggregate_random_draws, apply_gate


def write_figure(aggregated: list[dict], gate: dict, output: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), constrained_layout=True)
    for k, color in ((5, "#1f77b4"), (10, "#9467bd"), (20, "#d62728")):
        rows = [row for row in aggregated if int(row["k"]) == k]
        x = [row["gallery_n"] for row in rows]
        y = [row["cross_calibrated"]["median"] for row in rows]
        low = [row["cross_calibrated"]["ci95_gallery_q025"] for row in rows]
        high = [row["cross_calibrated"]["ci95_gallery_q975"] for row in rows]
        axes[0].plot(x, y, marker="o", color=color, label=f"k={k}")
        axes[0].fill_between(x, low, high, color=color, alpha=0.14)
    rows = [row for row in aggregated if int(row["k"]) == 5]
    x = [row["gallery_n"] for row in rows]
    axes[1].plot(
        x,
        [row["cross_calibrated"]["median"] for row in rows],
        marker="o",
        label="cross-model",
    )
    axes[1].plot(
        x,
        [row["qwen_ceiling_calibrated"]["median"] for row in rows],
        marker="o",
        label="Qwen jackknife",
    )
    axes[1].plot(
        x,
        [row["minilm_ceiling_calibrated"]["median"] for row in rows],
        marker="o",
        label="MiniLM jackknife",
    )
    axes[0].set_title("Permutation-calibrated mKNN")
    axes[1].set_title(
        f"Scale: {gate['scale_gate']}\nObserver gap: {gate['observer_specific_gate']}"
    )
    for axis in axes:
        axis.set_xscale("log")
        axis.set_ylim(0, 1)
        axis.set_xlabel("gallery N")
        axis.set_ylabel("mKNN")
        axis.grid(alpha=0.25)
        axis.legend(fontsize=8)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_findings(result: dict, output: Path) -> None:
    gate = result["gate"]
    disposition = (
        "The preregistered static paper gate is released."
        if gate["static_paper_released"]
        else "The preregistered static paper gate is not released."
    )
    rows = [row for row in result["aggregated_random_curve"] if row["k"] == 5]
    table = "\n".join(
        f"| {row['gallery_n']:,} | {row['cross_calibrated']['median']:.4f} | "
        f"[{row['cross_calibrated']['ci95_gallery_q025']:.4f}, "
        f"{row['cross_calibrated']['ci95_gallery_q975']:.4f}] | "
        f"{row['qwen_ceiling_calibrated']['median']:.4f} | "
        f"{row['minilm_ceiling_calibrated']['median']:.4f} |"
        for row in rows
    )
    text = f"""---
type: "Findings Record"
title: "Semantic Atlas — Large-Scale Relational Geometry v1 Results"
description: "Terminal application of the preregistered 100k arXiv gallery gate."
tags: [semantic-atlas, observation, embeddings, mknn, arxiv, exact-knn, scale]
timestamp: {result['executed_at']}
---

# Semantic Atlas — Large-Scale Relational Geometry v1 Results

## Terminal disposition

- scale gate: **`{gate['scale_gate']}`**;
- observer-specific gate: **`{gate['observer_specific_gate']}`**;
- static paper released: **`{str(gate['static_paper_released']).lower()}`**.

{disposition}

## Decision statistics

| Statistic | Value |
|---|---:|
| S(1,000) | {gate['S1000']:.6f} |
| S(100,000) | {gate['S100000']:.6f} |
| Retention R | {gate['retention']:.6f} |
| Cross-model C(100,000) | {gate['C100000']:.6f} |
| Conservative ceiling U(100,000) | {gate['U100000']:.6f} |
| Ceiling ratio Q | {gate['Q']:.6f} |

## Primary k=5 curve

| Gallery N | Calibrated mKNN median | 95% gallery interval | Qwen ceiling | MiniLM ceiling |
|---:|---:|---:|---:|---:|
{table}

## Frozen unit and controls

The unit is the full normalized arXiv abstract. Every included abstract has at most 256 WordPieces under the pinned MiniLM tokenizer and runtime truncation was forbidden, so both primary observers received the same semantic content. All neighbor sets are exact cosine kNN. The curve uses 32 preregistered stratified random galleries per N; chronological prefixes are descriptive only.

The prior Qwen 1024→384 dimensionality diagnostic remains secondary and post-hoc. It cannot change either terminal gate.
"""
    output.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--findings", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    args = parser.parse_args()

    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.input_dir.glob("*.json"))]
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    aggregated = aggregate_random_draws(results)
    gate = apply_gate(aggregated, manifest)
    result = {
        "schema_version": 1,
        "experiment": manifest["experiment"],
        "executed_at": datetime.now(UTC).isoformat(),
        "random_draws": 32,
        "aggregated_random_curve": aggregated,
        "chronological_prefix": next(
            (item for item in results if item["gallery_kind"] == "chronological_prefix"),
            None,
        ),
        "gate": gate,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_findings(result, args.findings)
    write_figure(aggregated, gate, args.figure)
    print(json.dumps(gate, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
