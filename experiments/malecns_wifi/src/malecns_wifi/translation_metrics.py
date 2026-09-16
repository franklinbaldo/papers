"""Scoring for representation translation, including the trajectory metrics.

Mean cosine is the obvious score and the least interesting one here. The claim
under test is about a *loop*, so the metrics that decide it are the ones indexed
by round: ``quality(t)`` and the error contraction ratio. A system whose round-0
answer is already its best answer has a loop that does nothing, whatever its
final cosine.

Retrieval is reported alongside cosine because cosine can be inflated by
collapsing every prediction onto the centroid of the target space: that raises
mean cosine and destroys retrieval. CSLS is included for the same reason, since
it corrects the hubness that plain nearest-neighbour retrieval rewards.

Everything here is numpy so it can be tested without torch and run on the CPU.
"""

from __future__ import annotations

import numpy as np


def unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, 1e-12)


def mean_cosine(predicted: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean(np.sum(unit_rows(predicted) * unit_rows(target), axis=1)))


def mean_squared_error(predicted: np.ndarray, target: np.ndarray) -> float:
    difference = unit_rows(predicted) - unit_rows(target)
    return float(np.mean(difference.astype(np.float64) ** 2))


def error_norms(predicted: np.ndarray, target: np.ndarray) -> np.ndarray:
    return np.linalg.norm(unit_rows(predicted) - unit_rows(target), axis=1)


def retrieval(predicted: np.ndarray, target: np.ndarray, *, ks=(1, 5, 10)) -> dict:
    """Rank the true target among all targets in the evaluation pool.

    The pool is the whole split, so chance level is ``k / n``: a number worth
    printing next to the result, because on a 200-item pool retrieval@10 of 5%
    is exactly nothing.
    """
    predicted = unit_rows(predicted)
    target = unit_rows(target)
    similarity = predicted @ target.T
    truth = np.arange(similarity.shape[0])
    order = np.argsort(-similarity, axis=1)
    ranks = np.argmax(order == truth[:, None], axis=1)
    result = {f"retrieval@{k}": float(np.mean(ranks < k)) for k in ks}
    result["mean_reciprocal_rank"] = float(np.mean(1.0 / (ranks + 1.0)))
    result["median_rank"] = float(np.median(ranks) + 1.0)
    result["pool_size"] = int(similarity.shape[0])
    result["chance_retrieval@1"] = 1.0 / float(similarity.shape[0])
    return result


def csls_retrieval(predicted: np.ndarray, target: np.ndarray, *, k: int = 10) -> dict:
    """Retrieval under cross-domain similarity local scaling (hubness-corrected)."""
    predicted = unit_rows(predicted)
    target = unit_rows(target)
    similarity = predicted @ target.T
    neighbours = min(k, similarity.shape[1])
    r_target = np.mean(np.sort(similarity, axis=0)[-neighbours:, :], axis=0)
    r_source = np.mean(np.sort(similarity, axis=1)[:, -neighbours:], axis=1)
    scaled = 2.0 * similarity - r_source[:, None] - r_target[None, :]
    truth = np.arange(scaled.shape[0])
    order = np.argsort(-scaled, axis=1)
    ranks = np.argmax(order == truth[:, None], axis=1)
    return {
        "csls_retrieval@1": float(np.mean(ranks < 1)),
        "csls_retrieval@10": float(np.mean(ranks < min(10, scaled.shape[1]))),
    }


def knn_preservation(predicted: np.ndarray, target: np.ndarray, *, k: int = 10) -> float:
    """Overlap between each item's k nearest neighbours in both spaces.

    This asks whether the translation preserved local structure, which is a
    different and weaker question than whether it landed on the right point.
    """
    predicted = unit_rows(predicted)
    target = unit_rows(target)
    count = predicted.shape[0]
    neighbours = min(k, count - 1)
    if neighbours < 1:
        return float("nan")

    def top_k(values: np.ndarray) -> np.ndarray:
        similarity = values @ values.T
        np.fill_diagonal(similarity, -np.inf)
        return np.argsort(-similarity, axis=1)[:, :neighbours]

    predicted_neighbours = top_k(predicted)
    target_neighbours = top_k(target)
    overlaps = [
        len(set(predicted_neighbours[index]).intersection(target_neighbours[index]))
        for index in range(count)
    ]
    return float(np.mean(overlaps) / neighbours)


def _rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    return ranks


def distance_spearman(predicted: np.ndarray, target: np.ndarray, *, sample: int = 20000,
                      seed: int = 0) -> float:
    """Spearman correlation between pairwise distances in both spaces."""
    predicted = unit_rows(predicted)
    target = unit_rows(target)
    count = predicted.shape[0]
    if count < 3:
        return float("nan")
    rng = np.random.default_rng(seed)
    pairs = min(sample, count * (count - 1) // 2)
    left = rng.integers(0, count, size=pairs * 2)
    right = rng.integers(0, count, size=pairs * 2)
    keep = left != right
    left, right = left[keep][:pairs], right[keep][:pairs]
    predicted_distance = np.linalg.norm(predicted[left] - predicted[right], axis=1)
    target_distance = np.linalg.norm(target[left] - target[right], axis=1)
    a = _rankdata(predicted_distance)
    b = _rankdata(target_distance)
    a = a - a.mean()
    b = b - b.mean()
    denominator = np.sqrt((a * a).sum() * (b * b).sum())
    if denominator <= 0:
        return float("nan")
    return float((a * b).sum() / denominator)


def centroid_baseline(target: np.ndarray, *, seed: int = 0) -> dict:
    """Score of emitting the pool centroid for every input.

    This is not a formality. In an anisotropic target space the centroid scores a
    higher mean cosine than a working translation while retrieving at chance, so
    a cosine number that is not compared against this one says nothing at all.
    """
    target = unit_rows(target)
    centroid = unit_rows(target.mean(axis=0, keepdims=True))
    predicted = np.repeat(centroid, target.shape[0], axis=0)
    result = score_prediction(predicted, target, seed=seed)
    result["mean_pairwise_cosine_in_target_space"] = float(
        np.mean(target @ target.T) - 1.0 / target.shape[0]
    )
    return result


def score_prediction(predicted: np.ndarray, target: np.ndarray, *, seed: int = 0) -> dict:
    result = {
        "mean_cosine": mean_cosine(predicted, target),
        "mse": mean_squared_error(predicted, target),
        "mean_error_norm": float(np.mean(error_norms(predicted, target))),
        "knn_preservation@10": knn_preservation(predicted, target, k=10),
        "distance_spearman": distance_spearman(predicted, target, seed=seed),
    }
    result.update(retrieval(predicted, target))
    result.update(csls_retrieval(predicted, target))
    return result


def score_trajectory(predictions: list[np.ndarray], target: np.ndarray, *, seed: int = 0) -> dict:
    """Score every round, then say whether the loop actually improved anything.

    ``error_contraction`` is ``||e_{t+1}|| / ||e_t||`` averaged over items. Below
    one means the loop is pulling the estimate toward the target; at one it is
    idling; above one it is drifting away. This is the number the closed-loop
    hypothesis lives or dies on, and it is reported per transition rather than
    summarised away.
    """
    rounds = []
    for index, prediction in enumerate(predictions):
        row = {"round": index}
        row.update(score_prediction(prediction, target, seed=seed))
        rounds.append(row)

    contraction = []
    for index in range(len(predictions) - 1):
        before = error_norms(predictions[index], target)
        after = error_norms(predictions[index + 1], target)
        ratio = after / np.maximum(before, 1e-12)
        contraction.append({
            "from_round": index,
            "to_round": index + 1,
            "mean_ratio": float(np.mean(ratio)),
            "median_ratio": float(np.median(ratio)),
            "fraction_improved": float(np.mean(after < before)),
        })

    first, last = rounds[0], rounds[-1]
    return {
        "rounds": rounds,
        "error_contraction": contraction,
        "final": last,
        "trajectory_gain": {
            "cosine_first_to_last": last["mean_cosine"] - first["mean_cosine"],
            "retrieval@1_first_to_last": last["retrieval@1"] - first["retrieval@1"],
            "best_round_by_cosine": int(max(rounds, key=lambda row: row["mean_cosine"])["round"]),
            "loop_is_idle": bool(
                abs(last["mean_cosine"] - first["mean_cosine"]) < 1e-3 and len(rounds) > 1
            ),
        },
    }
