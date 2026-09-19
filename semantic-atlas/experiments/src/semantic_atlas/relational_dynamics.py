from __future__ import annotations

from typing import Mapping

import numpy as np


def l2_normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, 1e-12)


def cosine_scores(embeddings: np.ndarray) -> np.ndarray:
    values = l2_normalize(embeddings)
    scores = values @ values.T
    np.fill_diagonal(scores, -np.inf)
    return scores


def csls_scores(scores: np.ndarray, neighborhood: int = 10) -> np.ndarray:
    """Symmetric CSLS on one corpus, using the final frozen corpus as the bank."""
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 2 or scores.shape[0] != scores.shape[1]:
        raise ValueError("scores must be square")
    n = len(scores)
    q = min(int(neighborhood), n - 1)
    if q < 1:
        raise ValueError("need at least two points")
    finite = scores.copy()
    np.fill_diagonal(finite, -np.inf)
    local = np.partition(finite, n - q, axis=1)[:, n - q :]
    row_mean = np.mean(local, axis=1)
    adjusted = 2.0 * finite - row_mean[:, None] - row_mean[None, :]
    np.fill_diagonal(adjusted, -np.inf)
    return adjusted


def empirical_mutual_proximity_scores(scores: np.ndarray) -> np.ndarray:
    """Exact empirical Mutual Proximity on a symmetric final-corpus distance matrix.

    The returned value is a similarity: larger means that a pair is unusually close
    from both points' distance distributions. Hubness control is fitted once on the
    final frozen corpus; insertion replay only changes candidate availability.
    """
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 2 or scores.shape[0] != scores.shape[1]:
        raise ValueError("scores must be square")
    n = len(scores)
    if n < 3:
        raise ValueError("mutual proximity needs at least three points")
    distances = 1.0 - scores
    np.fill_diagonal(distances, np.inf)
    mp = np.full((n, n), -np.inf, dtype=np.float64)
    denom = float(n - 2)
    all_ids = np.arange(n)
    for i in range(n):
        for j in range(i + 1, n):
            keep = (all_ids != i) & (all_ids != j)
            threshold = distances[i, j]
            count = np.count_nonzero(
                (distances[i, keep] > threshold) & (distances[j, keep] > threshold)
            )
            value = count / denom
            mp[i, j] = value
            mp[j, i] = value
    return mp


def rankings_from_scores(scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(scores, dtype=np.float64)
    return np.argsort(-scores, axis=1, kind="stable")


def hubness_summary(rankings: np.ndarray, k: int) -> dict[str, float | int]:
    rankings = np.asarray(rankings, dtype=np.int64)
    n = len(rankings)
    if not 1 <= k < n:
        raise ValueError("k must be in [1, n)")
    top = rankings[:, :k]
    counts = np.bincount(top.ravel(), minlength=n).astype(np.float64)
    mean = float(np.mean(counts))
    std = float(np.std(counts))
    skew = 0.0 if std <= 1e-12 else float(np.mean(((counts - mean) / std) ** 3))
    robinhood = 0.0 if mean <= 1e-12 else float(0.5 * np.sum(np.abs(counts - mean)) / (n * mean))
    return {
        "k": int(k),
        "k_occurrence_skewness": skew,
        "robinhood": robinhood,
        "max_k_occurrence": int(np.max(counts)),
        "anti_hub_fraction": float(np.mean(counts == 0)),
    }


def _prefix_neighbors(
    rankings: np.ndarray,
    scores: np.ndarray,
    prefix_mask: np.ndarray,
    anchors: np.ndarray,
    k: int,
) -> tuple[dict[int, tuple[int, ...]], dict[int, tuple[float, float]]]:
    neighbors: dict[int, tuple[int, ...]] = {}
    gaps: dict[int, tuple[float, float]] = {}
    for anchor in anchors:
        row = rankings[anchor]
        available = row[prefix_mask[row] & (row != anchor)]
        if len(available) < k:
            raise ValueError("prefix is too small for k")
        chosen = available[:k]
        neighbors[int(anchor)] = tuple(int(x) for x in chosen)
        top1_gap = float("nan")
        boundary_gap = float("nan")
        if len(available) >= 2:
            top1_gap = float(scores[anchor, available[0]] - scores[anchor, available[1]])
        if len(available) >= k + 1:
            boundary_gap = float(scores[anchor, available[k - 1]] - scores[anchor, available[k]])
        gaps[int(anchor)] = (top1_gap, boundary_gap)
    return neighbors, gaps


def churn_trace(
    scores: np.ndarray,
    order: np.ndarray,
    *,
    k: int = 5,
    initial_n: int = 24,
    batch_size: int = 4,
    region_labels: np.ndarray | None = None,
) -> dict:
    scores = np.asarray(scores, dtype=np.float64)
    order = np.asarray(order, dtype=np.int64)
    n = len(scores)
    if scores.shape != (n, n) or sorted(order.tolist()) != list(range(n)):
        raise ValueError("scores/order mismatch")
    if initial_n <= k or initial_n >= n:
        raise ValueError("initial_n must be > k and < n")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if region_labels is not None and len(region_labels) != n:
        raise ValueError("region label count mismatch")

    rankings = rankings_from_scores(scores)
    prefix_mask = np.zeros(n, dtype=bool)
    prefix_mask[order[:initial_n]] = True
    prev_ids = order[:initial_n].copy()
    prev_neighbors, prev_gaps = _prefix_neighbors(rankings, scores, prefix_mask, prev_ids, k)
    first_churn_added_docs: dict[int, int | None] = {int(i): None for i in prev_ids}
    transitions: list[dict] = []
    records: list[dict] = []

    prev_n = initial_n
    while prev_n < n:
        cur_n = min(prev_n + batch_size, n)
        new_ids = order[prev_n:cur_n]
        prefix_mask[new_ids] = True
        old_ids = order[:prev_n]
        current_neighbors, current_gaps = _prefix_neighbors(
            rankings, scores, prefix_mask, old_ids, k
        )
        added = cur_n - prev_n
        exchangeable_expected = added / (prev_n - 1 + added)
        churn_values = []
        region_values: dict[int, list[float]] = {}
        for anchor in old_ids:
            anchor_i = int(anchor)
            old = set(prev_neighbors[anchor_i])
            new = set(current_neighbors[anchor_i])
            churn = 1.0 - len(old & new) / k
            churn_values.append(churn)
            top1_gap, boundary_gap = prev_gaps[anchor_i]
            record = {
                "anchor": anchor_i,
                "prev_n": int(prev_n),
                "cur_n": int(cur_n),
                "added": int(added),
                "churn": float(churn),
                "changed": bool(churn > 0),
                "top1_gap": top1_gap,
                "boundary_gap": boundary_gap,
            }
            if region_labels is not None:
                region = int(region_labels[anchor_i])
                record["region"] = region
                region_values.setdefault(region, []).append(float(churn))
            records.append(record)
            if (
                anchor_i in first_churn_added_docs
                and first_churn_added_docs[anchor_i] is None
                and churn > 0
            ):
                first_churn_added_docs[anchor_i] = int(cur_n - initial_n)

        mean_churn = float(np.mean(churn_values))
        step = {
            "prev_n": int(prev_n),
            "cur_n": int(cur_n),
            "added": int(added),
            "exchangeable_expected_churn": float(exchangeable_expected),
            "mean_churn": mean_churn,
            "normalized_hazard": float(mean_churn / max(exchangeable_expected, 1e-12)),
            "changed_anchor_fraction": float(np.mean(np.asarray(churn_values) > 0)),
        }
        if region_labels is not None:
            step["regions"] = {
                str(region): {
                    "anchor_count": len(values),
                    "mean_churn": float(np.mean(values)),
                    "normalized_hazard": float(
                        np.mean(values) / max(exchangeable_expected, 1e-12)
                    ),
                }
                for region, values in sorted(region_values.items())
            }
        transitions.append(step)

        all_current = order[:cur_n]
        prev_neighbors, prev_gaps = _prefix_neighbors(
            rankings, scores, prefix_mask, all_current, k
        )
        prev_n = cur_n

    return {
        "k": int(k),
        "initial_n": int(initial_n),
        "batch_size": int(batch_size),
        "transitions": transitions,
        "records": records,
        "first_churn_added_docs": {
            str(key): value for key, value in first_churn_added_docs.items()
        },
    }


def trace_divergence(a: Mapping, b: Mapping, *, regional: bool = False) -> float:
    ta = a["transitions"]
    tb = b["transitions"]
    if len(ta) != len(tb):
        raise ValueError("trace length mismatch")
    if not regional:
        return float(
            np.mean(
                [
                    abs(x["normalized_hazard"] - y["normalized_hazard"])
                    for x, y in zip(ta, tb, strict=True)
                ]
            )
        )
    values = []
    for x, y in zip(ta, tb, strict=True):
        rx = x.get("regions", {})
        ry = y.get("regions", {})
        for key in sorted(set(rx) & set(ry)):
            values.append(abs(rx[key]["normalized_hazard"] - ry[key]["normalized_hazard"]))
    return float(np.mean(values)) if values else float("nan")


def trace_correlation(a: Mapping, b: Mapping) -> float:
    xa = np.asarray([x["normalized_hazard"] for x in a["transitions"]], dtype=np.float64)
    xb = np.asarray([x["normalized_hazard"] for x in b["transitions"]], dtype=np.float64)
    if len(xa) < 2 or np.std(xa) <= 1e-12 or np.std(xb) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(xa, xb)[0, 1])


def gap_churn_summary(trace: Mapping) -> dict[str, float | int | None]:
    rows = [r for r in trace["records"] if np.isfinite(r["boundary_gap"])]
    if len(rows) < 8:
        return {"n": len(rows), "low_gap_churn_rate": None, "high_gap_churn_rate": None, "rate_ratio": None}
    gaps = np.asarray([r["boundary_gap"] for r in rows], dtype=np.float64)
    changed = np.asarray([r["changed"] for r in rows], dtype=bool)
    low_cut, high_cut = np.quantile(gaps, [0.25, 0.75])
    low = float(np.mean(changed[gaps <= low_cut]))
    high = float(np.mean(changed[gaps >= high_cut]))
    ratio = float(low / max(high, 1e-12))
    return {
        "n": len(rows),
        "q25_boundary_gap": float(low_cut),
        "q75_boundary_gap": float(high_cut),
        "low_gap_churn_rate": low,
        "high_gap_churn_rate": high,
        "rate_ratio": ratio,
    }


def resolution_summary(trace: Mapping, region_labels: np.ndarray | None, n_total: int) -> dict:
    first = {int(k): v for k, v in trace["first_churn_added_docs"].items()}

    def summarize(ids: list[int]) -> dict:
        observed = [first[i] for i in ids if first[i] is not None]
        return {
            "anchor_count": len(ids),
            "censored_fraction": float(np.mean([first[i] is None for i in ids])) if ids else float("nan"),
            "median_added_docs_to_first_churn": float(np.median(observed)) if observed else None,
            "median_added_mass_to_first_churn": float(np.median(observed) / n_total) if observed else None,
        }

    out = {"global": summarize(sorted(first))}
    if region_labels is not None:
        regions = {}
        for region in sorted(set(int(region_labels[i]) for i in first)):
            ids = [i for i in first if int(region_labels[i]) == region]
            regions[str(region)] = summarize(ids)
        out["regions"] = regions
    return out


def semantic_drift_score(
    embedding_a: np.ndarray,
    embedding_b: np.ndarray,
    order: np.ndarray,
    *,
    initial_n: int,
    batch_size: int,
) -> float:
    a = l2_normalize(embedding_a)
    b = l2_normalize(embedding_b)
    order = np.asarray(order, dtype=np.int64)
    n = len(order)
    values = []
    prev_n = initial_n
    while prev_n < n:
        cur_n = min(prev_n + batch_size, n)
        old = order[:prev_n]
        new = order[prev_n:cur_n]
        model_values = []
        for x in (a, b):
            old_center = np.mean(x[old], axis=0)
            new_center = np.mean(x[new], axis=0)
            old_center /= max(np.linalg.norm(old_center), 1e-12)
            new_center /= max(np.linalg.norm(new_center), 1e-12)
            model_values.append(1.0 - float(old_center @ new_center))
        values.append(float(np.mean(model_values)))
        prev_n = cur_n
    return float(np.mean(values))


def empirical_upper_p(observed: float, null: np.ndarray) -> float:
    null = np.asarray(null, dtype=np.float64)
    return float((1 + np.count_nonzero(null >= observed)) / (len(null) + 1))


def null_summary(observed: float, null: np.ndarray) -> dict[str, float]:
    null = np.asarray(null, dtype=np.float64)
    std = float(np.std(null, ddof=1)) if len(null) > 1 else 0.0
    mean = float(np.mean(null))
    return {
        "observed": float(observed),
        "null_mean": mean,
        "null_sd": std,
        "null_q95": float(np.quantile(null, 0.95)),
        "z": float((observed - mean) / std) if std > 1e-12 else float("nan"),
        "p_upper": empirical_upper_p(observed, null),
    }


def deterministic_kmeans(values: np.ndarray, k: int, iterations: int = 50) -> np.ndarray:
    x = l2_normalize(values)
    n = len(x)
    if not 1 <= k <= n:
        raise ValueError("invalid k")
    chosen = [0]
    min_distance = 1.0 - x @ x[0]
    for _ in range(1, k):
        idx = int(np.argmax(min_distance))
        chosen.append(idx)
        min_distance = np.minimum(min_distance, 1.0 - x @ x[idx])
    centers = x[chosen].copy()
    labels = np.zeros(n, dtype=np.int64)
    for _ in range(iterations):
        next_labels = np.argmax(x @ centers.T, axis=1)
        next_centers = centers.copy()
        for region in range(k):
            members = x[next_labels == region]
            if len(members):
                center = np.mean(members, axis=0)
                next_centers[region] = center / max(np.linalg.norm(center), 1e-12)
        if np.array_equal(next_labels, labels) and np.allclose(next_centers, centers):
            labels = next_labels
            break
        labels, centers = next_labels, next_centers
    return labels
