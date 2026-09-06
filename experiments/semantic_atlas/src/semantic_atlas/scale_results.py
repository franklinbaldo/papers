from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def aggregate_random_draws(results: Sequence[dict]) -> list[dict]:
    groups: dict[tuple[int, int], list[dict]] = {}
    for result in results:
        if result["gallery_kind"] != "stratified_random":
            continue
        for row in result["rows"]:
            groups.setdefault((int(row["gallery_n"]), int(row["k"])), []).append(row)
    output = []
    for (n, k), rows in sorted(groups.items()):
        if len(rows) != 32:
            raise RuntimeError(f"expected 32 random draws for N={n},k={k}; found {len(rows)}")

        def summary(values) -> dict[str, float]:
            array = np.asarray(list(values), dtype=np.float64)
            return {
                "median": float(np.median(array)),
                "ci95_gallery_q025": float(np.quantile(array, 0.025)),
                "ci95_gallery_q975": float(np.quantile(array, 0.975)),
                "minimum": float(array.min()),
                "maximum": float(array.max()),
            }

        output.append(
            {
                "gallery_n": n,
                "k": k,
                "draws": len(rows),
                "cross_raw": summary(row["cross_model"]["raw_mknn"] for row in rows),
                "cross_calibrated": summary(
                    row["cross_model"]["calibrated_mknn"] for row in rows
                ),
                "qwen_ceiling_calibrated": summary(
                    row["same_observer_gallery_jackknife"]["qwen"]["calibrated_mknn"]
                    for row in rows
                ),
                "minilm_ceiling_calibrated": summary(
                    row["same_observer_gallery_jackknife"]["minilm"]["calibrated_mknn"]
                    for row in rows
                ),
                "qwen_category_purity": summary(
                    row["category_purity"]["qwen"] for row in rows
                ),
                "minilm_category_purity": summary(
                    row["category_purity"]["minilm"] for row in rows
                ),
                "category_null": summary(
                    row["category_purity"]["shuffled_label_expected"] for row in rows
                ),
            }
        )
    return output


def apply_gate(aggregated: Sequence[dict], manifest: dict) -> dict:
    primary_k = int(manifest["primary_gate"]["k"])
    lookup = {
        (int(row["gallery_n"]), int(row["k"])): row for row in aggregated
    }
    s1k = float(lookup[(1_000, primary_k)]["cross_calibrated"]["median"])
    s100k = float(lookup[(100_000, primary_k)]["cross_calibrated"]["median"])
    retention = s100k / max(s1k, 1e-12)
    primary = manifest["primary_gate"]
    if (
        retention >= float(primary["scale_stable"]["retention_gte"])
        and s100k >= float(primary["scale_stable"]["S100k_gte"])
    ):
        scale = "scale_stable"
    elif (
        retention <= float(primary["collapse"]["retention_lte"])
        or s100k <= float(primary["collapse"]["S100k_lte"])
    ):
        scale = "gallery_size_collapse"
    else:
        scale = "unresolved"

    row100 = lookup[(100_000, primary_k)]
    cross = float(row100["cross_calibrated"]["median"])
    ceiling = min(
        float(row100["qwen_ceiling_calibrated"]["median"]),
        float(row100["minilm_ceiling_calibrated"]["median"]),
    )
    ratio = cross / max(ceiling, 1e-12)
    observer = manifest["observer_specific_gate"]
    if ratio <= float(observer["survives_if_Q_lte"]):
        observer_decision = "observer_specific_gap_survives"
    elif ratio >= float(observer["near_ceiling_if_Q_gte"]):
        observer_decision = "cross_model_near_stability_ceiling"
    else:
        observer_decision = "unresolved"
    released = scale == "scale_stable" and observer_decision == "observer_specific_gap_survives"
    return {
        "scale_gate": scale,
        "observer_specific_gate": observer_decision,
        "static_paper_released": released,
        "S1000": s1k,
        "S100000": s100k,
        "retention": retention,
        "C100000": cross,
        "U100000": ceiling,
        "Q": ratio,
        "frozen_thresholds": {
            "primary": primary,
            "observer_specific": observer,
        },
    }
