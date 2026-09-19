from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Sequence

import numpy as np


def _hash_key(*parts: object) -> bytes:
    return hashlib.sha256(":".join(map(str, parts)).encode("utf-8")).digest()


def stratified_gallery(
    ids: Sequence[str],
    categories: Sequence[str],
    size: int,
    *,
    draw: int,
    seed: int,
) -> np.ndarray:
    if len(ids) != len(categories) or not 1 <= size <= len(ids):
        raise ValueError("invalid gallery inputs")
    counts = Counter(map(str, categories))
    exact = {category: size * count / len(ids) for category, count in counts.items()}
    quotas = {category: int(math.floor(value)) for category, value in exact.items()}
    remaining = size - sum(quotas.values())
    order = sorted(
        counts,
        key=lambda category: (-(exact[category] - quotas[category]), category),
    )
    for category in order[:remaining]:
        quotas[category] += 1

    by_category: dict[str, list[tuple[bytes, int]]] = {category: [] for category in counts}
    for index, (arxiv_id, category) in enumerate(zip(ids, categories, strict=True)):
        by_category[str(category)].append(
            (_hash_key(seed, draw, size, arxiv_id), index)
        )
    selected = []
    for category in sorted(by_category):
        chosen = sorted(by_category[category])[: quotas[category]]
        selected.extend((key, index) for key, index in chosen)
    selected.sort()
    result = np.asarray([index for _, index in selected], dtype=np.int64)
    if len(result) != size or len(np.unique(result)) != size:
        raise RuntimeError("stratified gallery did not produce the requested unique size")
    return result


def exact_topk(
    matrix: np.ndarray,
    gallery: np.ndarray,
    *,
    k: int,
    queries: np.ndarray | None = None,
    candidate_mask: np.ndarray | None = None,
    query_block: int = 256,
    candidate_block: int = 8192,
) -> np.ndarray:
    values = np.asarray(matrix, dtype=np.float32)
    gallery = np.asarray(gallery, dtype=np.int64)
    if queries is None:
        queries = np.arange(len(gallery), dtype=np.int64)
    else:
        queries = np.asarray(queries, dtype=np.int64)
    if candidate_mask is None:
        candidate_mask = np.ones(len(gallery), dtype=bool)
    else:
        candidate_mask = np.asarray(candidate_mask, dtype=bool)
    candidates = np.flatnonzero(candidate_mask)
    if len(candidates) <= k:
        raise ValueError("not enough candidates for requested k after self exclusion")

    output = np.empty((len(queries), k), dtype=np.int32)
    gallery_values = values[gallery]
    for q_start in range(0, len(queries), query_block):
        q_pos = queries[q_start : q_start + query_block]
        q_values = gallery_values[q_pos]
        best_scores = np.full((len(q_pos), k), -np.inf, dtype=np.float32)
        best_ids = np.full((len(q_pos), k), -1, dtype=np.int32)
        for c_start in range(0, len(candidates), candidate_block):
            c_pos = candidates[c_start : c_start + candidate_block]
            scores = q_values @ gallery_values[c_pos].T
            same = q_pos[:, None] == c_pos[None, :]
            scores[same] = -np.inf
            ids = np.broadcast_to(c_pos.astype(np.int32), scores.shape)
            joined_scores = np.concatenate((best_scores, scores), axis=1)
            joined_ids = np.concatenate((best_ids, ids), axis=1)
            keep = np.argpartition(joined_scores, -k, axis=1)[:, -k:]
            best_scores = np.take_along_axis(joined_scores, keep, axis=1)
            best_ids = np.take_along_axis(joined_ids, keep, axis=1)
        order = np.argsort(-best_scores, axis=1, kind="stable")
        output[q_start : q_start + len(q_pos)] = np.take_along_axis(
            best_ids, order, axis=1
        )
    if np.any(output < 0):
        raise RuntimeError("exact top-k search exhausted candidates")
    return output


def mknn(left: np.ndarray, right: np.ndarray, k: int) -> float:
    a = np.asarray(left, dtype=np.int64)[:, :k]
    b = np.asarray(right, dtype=np.int64)[:, :k]
    if a.shape != b.shape:
        raise ValueError("neighbor arrays differ in shape")
    overlap = (a[:, :, None] == b[:, None, :]).any(axis=2).sum(axis=1)
    return float(np.mean(overlap / k))


def category_purity(neighbors: np.ndarray, gallery_categories: Sequence[str], k: int) -> float:
    categories = np.asarray(gallery_categories, dtype=object)
    query_categories = categories[: len(neighbors)]
    same = categories[np.asarray(neighbors[:, :k], dtype=np.int64)] == query_categories[:, None]
    return float(np.mean(same))


def analytic_null(n: int, k: int, query_count: int | None = None) -> dict[str, float]:
    if n <= k + 1:
        raise ValueError("n must exceed k+1")
    queries = n if query_count is None else int(query_count)
    population = n - 1
    p = k / population
    expected_overlap = k * p
    variance_overlap = k * p * (1.0 - p) * ((population - k) / (population - 1))
    mean = expected_overlap / k
    sd_mean = math.sqrt(variance_overlap / queries) / k
    q95 = min(mean + 1.6448536269514722 * sd_mean, 1.0)
    return {"mean": float(mean), "q95_independent_query_approx": float(q95)}


def calibrated(raw: float, null_q95: float) -> float:
    return float(max((raw - null_q95) / max(1.0 - null_q95, 1e-12), 0.0))


def jackknife_masks(
    ids: Sequence[str], *, draw: int, seed: int, anchor_fraction: float, retention: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = len(ids)
    anchor_n = max(1, int(math.floor(anchor_fraction * n)))
    ranked = sorted((_hash_key(seed, draw, "anchor", arxiv_id), idx) for idx, arxiv_id in enumerate(ids))
    anchors = np.asarray(sorted(idx for _, idx in ranked[:anchor_n]), dtype=np.int64)
    is_anchor = np.zeros(n, dtype=bool)
    is_anchor[anchors] = True
    masks = []
    threshold = int(retention * (1 << 64))
    for view in ("A", "B"):
        mask = is_anchor.copy()
        for index, arxiv_id in enumerate(ids):
            if is_anchor[index]:
                continue
            value = int.from_bytes(_hash_key(seed, draw, view, arxiv_id)[:8], "big")
            mask[index] = value < threshold
        masks.append(mask)
    return anchors, masks[0], masks[1]


def permutation_null(
    left: np.ndarray,
    right: np.ndarray,
    *,
    ks: Sequence[int],
    permutations: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    ks_array = np.asarray(sorted(set(map(int, ks))), dtype=np.int64)
    max_k = int(ks_array[-1])
    a = np.asarray(left[:, :max_k], dtype=np.int64)
    b = np.asarray(right[:, :max_k], dtype=np.int64)
    n = len(a)
    try:
        from numba import njit

        @njit(cache=True)
        def overlap_counts(
            a_: np.ndarray,
            b_: np.ndarray,
            permutation: np.ndarray,
            ks_: np.ndarray,
        ) -> np.ndarray:
            inverse = np.empty(len(permutation), dtype=np.int64)
            for i in range(len(permutation)):
                inverse[permutation[i]] = i
            stamp = np.zeros(len(permutation), dtype=np.int64)
            rank = np.zeros(len(permutation), dtype=np.int64)
            counts = np.zeros(len(ks_), dtype=np.int64)
            for i in range(len(permutation)):
                marker = i + 1
                for y in range(a_.shape[1]):
                    neighbor = a_[i, y]
                    stamp[neighbor] = marker
                    rank[neighbor] = y
                b_row = permutation[i]
                for x in range(b_.shape[1]):
                    mapped = inverse[b_[b_row, x]]
                    if stamp[mapped] != marker:
                        continue
                    y = rank[mapped]
                    for offset in range(len(ks_)):
                        if x < ks_[offset] and y < ks_[offset]:
                            counts[offset] += 1
            return counts

    except ImportError:
        def overlap_counts(
            a_: np.ndarray,
            b_: np.ndarray,
            permutation: np.ndarray,
            ks_: np.ndarray,
        ) -> np.ndarray:
            inverse = np.empty(len(permutation), dtype=np.int64)
            inverse[permutation] = np.arange(len(permutation))
            mapped = inverse[b_[permutation]]
            return np.asarray(
                [
                    (a_[:, :k, None] == mapped[:, None, :k]).any(axis=2).sum()
                    for k in ks_
                ],
                dtype=np.int64,
            )

    rng = np.random.default_rng(seed)
    values = np.empty((permutations, len(ks_array)), dtype=np.float64)
    for index in range(permutations):
        permutation = rng.permutation(n).astype(np.int64)
        counts = overlap_counts(a, b, permutation, ks_array)
        values[index] = counts / (n * ks_array)
    return {
        str(k): {
            "permutations": int(permutations),
            "seed": int(seed),
            "mean": float(values[:, offset].mean()),
            "q95": float(np.quantile(values[:, offset], 0.95)),
            "minimum": float(values[:, offset].min()),
            "maximum": float(values[:, offset].max()),
        }
        for offset, k in enumerate(ks_array)
    }
