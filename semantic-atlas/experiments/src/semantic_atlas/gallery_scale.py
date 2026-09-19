from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence

import numpy as np

from semantic_atlas.relational_dynamics import cosine_scores, rankings_from_scores


def markdown_format_view(text: str) -> str:
    """Remove Markdown syntax while preserving the excerpt's lexical content.

    The input must already be truncated to the frozen excerpt length.  This keeps
    the content window identical between views; the operator is a formatting
    perturbation, not a second sample from the document.
    """

    value = text
    value = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"\1 \2", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", value)
    value = re.sub(r"(?m)^\s{0,3}(?:#{1,6}|>|[-+*]|\d+[.)])\s+", "", value)
    value = re.sub(r"(?m)^\s*```[^\n]*$", "", value)
    value = re.sub(r"[`*_~]+", "", value)
    value = re.sub(r"(?m)^---\s*$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def deterministic_subset(
    paths: Sequence[str], size: int, replicate: int, seed: int
) -> np.ndarray:
    """Select a subset without depending on RNG implementation details."""

    if not 1 <= size <= len(paths):
        raise ValueError("subset size must be between 1 and corpus size")
    if replicate < 0:
        raise ValueError("replicate must be non-negative")
    keyed = []
    for index, path in enumerate(paths):
        digest = hashlib.sha256(
            f"{seed}:{size}:{replicate}:{path}".encode("utf-8")
        ).digest()
        keyed.append((digest, index))
    return np.asarray(sorted(index for _, index in sorted(keyed)[:size]), dtype=np.int64)


def local_rankings(matrix: np.ndarray, subset: np.ndarray) -> np.ndarray:
    values = np.asarray(matrix, dtype=np.float64)[np.asarray(subset, dtype=np.int64)]
    return rankings_from_scores(cosine_scores(values))


def mknn_for_correspondence(
    rank_a: np.ndarray,
    rank_b: np.ndarray,
    correspondence: np.ndarray,
    ks: Sequence[int],
) -> np.ndarray:
    """Compute mKNN after permuting B's document correspondence.

    ``correspondence[i]`` is the B-document paired to A-document ``i``.  B
    neighbor identities are mapped back into A labels before set overlap.
    """

    rank_a = np.asarray(rank_a, dtype=np.int64)
    rank_b = np.asarray(rank_b, dtype=np.int64)
    correspondence = np.asarray(correspondence, dtype=np.int64)
    n = len(correspondence)
    if rank_a.shape != (n, n) or rank_b.shape != (n, n):
        raise ValueError("ranking/correspondence size mismatch")
    if sorted(correspondence.tolist()) != list(range(n)):
        raise ValueError("correspondence must be a permutation")
    ks_array = np.asarray(list(ks), dtype=np.int64)
    if len(ks_array) == 0 or np.any(ks_array < 1) or np.any(ks_array >= n):
        raise ValueError("every k must satisfy 1 <= k < n")

    inverse = np.empty(n, dtype=np.int64)
    inverse[correspondence] = np.arange(n, dtype=np.int64)
    max_k = int(np.max(ks_array))
    b_neighbors = inverse[rank_b[correspondence, :max_k]]
    out = np.empty(len(ks_array), dtype=np.float64)
    for offset, k in enumerate(ks_array):
        left = rank_a[:, :k]
        right = b_neighbors[:, :k]
        overlap = (left[:, :, None] == right[:, None, :]).any(axis=2).sum(axis=1)
        out[offset] = float(np.mean(overlap / k))
    return out


def permutation_calibration(
    rank_a: np.ndarray,
    rank_b: np.ndarray,
    *,
    ks: Sequence[int],
    permutations: Iterable[np.ndarray],
) -> dict[str, dict[str, float]]:
    n = len(rank_a)
    observed = mknn_for_correspondence(rank_a, rank_b, np.arange(n), ks)
    null_rows = [
        mknn_for_correspondence(rank_a, rank_b, permutation, ks)
        for permutation in permutations
    ]
    if not null_rows:
        raise ValueError("at least one null permutation is required")
    null = np.vstack(null_rows)
    result: dict[str, dict[str, float]] = {}
    for offset, k in enumerate(ks):
        values = null[:, offset]
        tau95 = float(np.quantile(np.concatenate(([observed[offset]], values)), 0.95))
        result[str(int(k))] = {
            "raw_mknn": float(observed[offset]),
            "null_mean": float(np.mean(values)),
            "null_q95": tau95,
            "p_upper_plus1": float(
                (1 + np.count_nonzero(values >= observed[offset])) / (len(values) + 1)
            ),
            "calibrated_mknn": float(
                max((observed[offset] - tau95) / max(1.0 - tau95, 1e-12), 0.0)
            ),
        }
    return result


def aggregate_curve(rows: Sequence[dict]) -> list[dict]:
    """Aggregate replicate summaries without hiding the individual rows."""

    groups: dict[tuple[int, str, str], list[dict]] = {}
    for row in rows:
        key = (int(row["gallery_n"]), str(row["pair"]), str(row["k"]))
        groups.setdefault(key, []).append(row)

    aggregated = []
    for (gallery_n, pair, k), group in sorted(groups.items()):
        item = {"gallery_n": gallery_n, "pair": pair, "k": int(k), "replicates": len(group)}
        for metric in ("raw_mknn", "null_mean", "null_q95", "calibrated_mknn"):
            values = np.asarray([entry[metric] for entry in group], dtype=np.float64)
            item[metric] = {
                "median": float(np.median(values)),
                "q10": float(np.quantile(values, 0.10)),
                "q90": float(np.quantile(values, 0.90)),
            }
        item["p_upper_plus1_max"] = float(max(entry["p_upper_plus1"] for entry in group))
        aggregated.append(item)
    return aggregated


def apply_static_gate(aggregated: Sequence[dict], gate: dict) -> dict:
    primary_k = int(gate["primary_k"])
    anchor_n = int(gate["anchor_gallery_n"])
    full_n = int(gate["full_gallery_n"])
    final_points = int(gate["observer_gap_final_points"])

    lookup = {
        (int(row["gallery_n"]), str(row["pair"]), int(row["k"])): row
        for row in aggregated
    }

    def score(n: int, pair: str) -> float:
        return float(lookup[(n, pair, primary_k)]["calibrated_mknn"]["median"])

    cross_anchor = score(anchor_n, "cross_model")
    cross_full = score(full_n, "cross_model")
    retention = cross_full / max(cross_anchor, 1e-12)
    sizes = sorted(
        n for n, pair, k in lookup if pair == "cross_model" and k == primary_k
    )
    tail = sizes[-final_points:]
    gaps = []
    for n in tail:
        conservative_same_observer = min(
            score(n, "reference_format_stability"),
            score(n, "transfer_format_stability"),
        )
        gaps.append(
            {
                "gallery_n": n,
                "conservative_same_observer_ceiling": conservative_same_observer,
                "cross_model": score(n, "cross_model"),
                "gap": conservative_same_observer - score(n, "cross_model"),
            }
        )

    alignment_material = cross_full >= float(gate["minimum_full_calibrated_mknn"])
    scale_retained = retention >= float(gate["minimum_retention_vs_anchor"])
    stability_control_valid = all(
        row["conservative_same_observer_ceiling"]
        >= float(gate["minimum_same_observer_ceiling"])
        for row in gaps
    )
    observer_specific = all(
        row["gap"] >= float(gate["minimum_same_observer_gap"]) for row in gaps
    )
    if not alignment_material or not scale_retained:
        decision = "small_gallery_artifact"
    elif not stability_control_valid:
        decision = "invalid_same_observer_stability_control"
    elif observer_specific:
        decision = "static_shared_but_observer_specific_structure"
    else:
        decision = "scale_stable_but_not_separated_from_stability_ceiling"

    return {
        "decision": decision,
        "primary_k": primary_k,
        "anchor_gallery_n": anchor_n,
        "full_gallery_n": full_n,
        "cross_model_calibrated_at_anchor": cross_anchor,
        "cross_model_calibrated_at_full": cross_full,
        "retention_vs_anchor": retention,
        "alignment_material": alignment_material,
        "scale_retained": scale_retained,
        "stability_control_valid": stability_control_valid,
        "observer_specific_tail": observer_specific,
        "tail_gaps": gaps,
        "frozen_thresholds": dict(gate),
    }
