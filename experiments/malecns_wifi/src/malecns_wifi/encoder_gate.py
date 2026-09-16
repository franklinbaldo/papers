"""Real-encoder gate: is there semantically localised food in actual legal text?

The question this answers, before any GPU is spent on the connectome: does the
semantic representation we invented -- multiscale child/parent relations,
contrasted with and without the tag -- actually contain the signal we are asking
the fly to find? If it does not, no reservoir can recover information the input
never carried, and the tagger experiment would be measuring nothing.

The gate runs **without the fly**. It scores each signal against the
hand-annotated spans directly, so a failure here is a cheap failure.

Note the scope difference from the tagger task. The tagger *predicts* the
dispositivo from a document with the dispositivo removed. This gate *localises*
the dispositivo in the whole document, so the text is not truncated: the question
is whether the signal peaks where the span is, not whether the outcome can be
guessed without it.

The encoder is injected. Nothing here commits to a model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

import numpy as np


class Encoder(Protocol):
    """Anything that turns a batch of strings into a matrix of embeddings."""

    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


@dataclass(frozen=True)
class ChunkPlan:
    """Fine chunks and the aligned parent window containing each one, in tokens."""

    fine_spans: tuple[tuple[int, int], ...]
    parent_spans: tuple[tuple[tuple[int, int], ...], ...]
    scales: tuple[int, ...]
    fine_size: int


def plan_chunks(
    token_count: int, *, fine_size: int = 64, scales: Sequence[int] = (256, 1024)
) -> ChunkPlan:
    """Aligned chunk hierarchy over a token sequence.

    Fine chunks are consecutive blocks of ``fine_size`` tokens. The parent of a
    fine chunk at scale ``s`` is the aligned ``s``-token block containing it, so a
    parent is shared by several adjacent children and a parent boundary falls at a
    predictable place. Alignment rather than a sliding window is deliberate: it is
    what makes a boundary crossing visible as a change in the relation.
    """
    if fine_size < 1:
        raise ValueError("fine_size must be >= 1")
    if any(scale < fine_size for scale in scales):
        raise ValueError("every parent scale must be at least the fine chunk size")

    fine = tuple(
        (start, min(start + fine_size, token_count))
        for start in range(0, max(token_count, 1), fine_size)
    )
    parents = []
    for scale in scales:
        spans = tuple(
            (
                (start // scale) * scale,
                min((start // scale) * scale + scale, token_count),
            )
            for start, _ in fine
        )
        parents.append(spans)
    return ChunkPlan(
        fine_spans=fine,
        parent_spans=tuple(parents),
        scales=tuple(scales),
        fine_size=fine_size,
    )


def build_hierarchy(
    text_of: Callable[[tuple[int, int]], str],
    plan: ChunkPlan,
    encoder: Encoder,
    tag: str,
    *,
    tag_template: str = "{text}\n\n{tag}",
) -> dict:
    """Encode every chunk and parent, with and without the tag appended.

    Parents are encoded once per distinct span and then repeated to one row per
    fine chunk, which is both what :func:`multiscale_relations` expects and a
    large saving: at 1024-token scale a single parent covers sixteen children.
    """
    fine_texts = [text_of(span) for span in plan.fine_spans]
    child_plain = encoder.encode(fine_texts)
    child_tagged = encoder.encode([tag_template.format(text=t, tag=tag) for t in fine_texts])

    parents_plain, parents_tagged = [], []
    for spans in plan.parent_spans:
        unique = sorted(set(spans))
        index = {span: position for position, span in enumerate(unique)}
        texts = [text_of(span) for span in unique]
        plain = encoder.encode(texts)
        tagged = encoder.encode([tag_template.format(text=t, tag=tag) for t in texts])
        rows = np.asarray([index[span] for span in spans])
        parents_plain.append(plain[rows])
        parents_tagged.append(tagged[rows])

    return {
        "child_plain": np.asarray(child_plain, dtype=np.float32),
        "child_tagged": np.asarray(child_tagged, dtype=np.float32),
        "parents_plain": parents_plain,
        "parents_tagged": parents_tagged,
        "tag_embedding": np.asarray(encoder.encode([tag])[0], dtype=np.float32),
    }


# --- metrics ---------------------------------------------------------------


def average_precision(scores: np.ndarray, labels: np.ndarray) -> float:
    """Area under the precision-recall curve, computed as average precision.

    AUPRC rather than AUROC because the positives are rare -- a dispositivo is one
    or two chunks out of twenty -- and AUROC is optimistic under that imbalance.
    """
    values = np.asarray(scores, dtype=np.float64).reshape(-1)
    truth = np.asarray(labels, dtype=bool).reshape(-1)
    if values.size != truth.size:
        raise ValueError("scores and labels must share length")
    positives = int(truth.sum())
    if positives == 0 or positives == truth.size:
        return float("nan")

    order = np.argsort(-values)
    hits = truth[order]
    cumulative = np.cumsum(hits)
    precision = cumulative / np.arange(1, hits.size + 1)
    return float(precision[hits].sum() / positives)


def best_f1_threshold(scores: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    """Threshold maximising F1, and that F1. Used to turn a signal into a region.

    Ties go to the *highest* threshold, i.e. the tightest region. Predicting the
    whole document often ties on F1 with a sharp prediction when positives are
    common enough, and calling that a localisation would flatter every signal
    equally.
    """
    values = np.asarray(scores, dtype=np.float64).reshape(-1)
    truth = np.asarray(labels, dtype=bool).reshape(-1)
    best, best_threshold = 0.0, float(values.max()) if values.size else 0.0
    for threshold in np.unique(values):
        predicted = values >= threshold
        true_positives = int((predicted & truth).sum())
        if true_positives == 0:
            continue
        precision = true_positives / max(int(predicted.sum()), 1)
        recall = true_positives / max(int(truth.sum()), 1)
        score = 2 * precision * recall / (precision + recall)
        if score >= best:
            best, best_threshold = score, float(threshold)
    return best_threshold, best


def edge_errors(
    scores: np.ndarray, labels: np.ndarray, *, fine_size: int
) -> dict:
    """START/END error in tokens for the largest run above the best-F1 threshold.

    The signal is turned into a region the simplest defensible way -- threshold at
    the best-F1 point, take the longest contiguous run above it -- and the edges of
    that run are compared with the gold edges. Reported in tokens rather than
    chunks so the number means something independent of the chunk size.
    """
    truth = np.asarray(labels, dtype=bool).reshape(-1)
    if not truth.any():
        return {"start_error_tokens": float("nan"), "end_error_tokens": float("nan")}
    threshold, _ = best_f1_threshold(scores, truth)
    predicted = np.asarray(scores, dtype=np.float64).reshape(-1) >= threshold
    if not predicted.any():
        return {"start_error_tokens": float("nan"), "end_error_tokens": float("nan")}

    runs, start = [], None
    for index, flag in enumerate(predicted):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, predicted.size))
    longest = max(runs, key=lambda run: run[1] - run[0])

    gold = np.flatnonzero(truth)
    return {
        "start_error_tokens": abs(longest[0] - int(gold[0])) * fine_size,
        "end_error_tokens": abs(longest[1] - (int(gold[-1]) + 1)) * fine_size,
        "predicted_chunks": longest[1] - longest[0],
        "gold_chunks": int(truth.sum()),
    }


def score_signal(name: str, values: np.ndarray, labels: np.ndarray, *, fine_size: int) -> dict:
    """Every metric for one candidate food signal."""
    from .semantic_food import intensity_polarity

    truth = np.asarray(labels, dtype=bool)
    polarity = intensity_polarity(values, truth)
    return {
        "signal": name,
        "auprc": average_precision(values, truth),
        "point_biserial": polarity["point_biserial"],
        "inside_mean": polarity["inside_mean"],
        "outside_mean": polarity["outside_mean"],
        "best_f1": best_f1_threshold(values, truth)[1],
        **edge_errors(values, truth, fine_size=fine_size),
    }


def candidate_signals(hierarchy: dict, *, tau: float = 0.5) -> dict[str, np.ndarray]:
    """Every signal the gate compares, from one encoded hierarchy.

    Each is a per-fine-chunk score. They are deliberately not combined into one
    number here: which of them carries the localisation is exactly what the gate
    is for.
    """
    from .semantic_food import tag_contrast
    from .semantic_hierarchy import (
        compose_meal,
        per_scale_intensity,
        redundancy_differential,
        relational_tag_contrast,
    )

    child_plain = hierarchy["child_plain"]
    child_tagged = hierarchy["child_tagged"]
    parents_plain = hierarchy["parents_plain"]
    parents_tagged = hierarchy["parents_tagged"]
    tag_embedding = hierarchy["tag_embedding"]

    flat_similarity = tag_contrast(
        child_plain, child_tagged, tag_embedding, intensity="similarity"
    )
    flat_redundancy = tag_contrast(
        child_plain, child_tagged, tag_embedding, intensity="redundancy", tau=tau
    )
    relational = relational_tag_contrast(
        child_plain, parents_plain, child_tagged, parents_tagged,
        intensity="redundancy", tau=tau,
    )
    differential = redundancy_differential(
        child_plain, child_tagged, parents_plain, parents_tagged
    )
    meal = compose_meal(child_plain, child_tagged, parents_plain, parents_tagged, tau=tau)
    scaled = per_scale_intensity(relational)

    signals: dict[str, np.ndarray] = {
        "similarity": flat_similarity.intensity,
        "flat_redundancy": flat_redundancy.intensity,
        "relational_redundancy": relational.intensity,
        "meal_amount": meal.amount,
        # amount x |A|: redundancy gates, the differential sharpens inside the gate.
        "redundancy_x_differential": meal.amount * np.abs(differential[:, -1]),
    }
    for position, scale in enumerate(relational.scale_slices):
        signals[f"relational_scale_{position}"] = scaled[:, position]
    for position in range(differential.shape[1]):
        signals[f"differential_scale_{position}"] = differential[:, position]
    return signals


# --- sensation vs reward ----------------------------------------------------
#
# Two channels, separated on purpose:
#
#   sensation -- the multiscale relation of the text to its own contexts, with NO
#                tag anywhere. This is what the fly feels walking through the
#                document, and it is ALL that exists at inference.
#   reward    -- the tag-conditioned food signal, available only in training,
#                where the tag of the example is known.
#
# The consequence for this gate is not cosmetic. The tag-conditioned signals
# scored above are the *reward* channel: they say whether the teacher is well
# placed. Whether the fly can find the region at inference is a different
# question, asked of the tag-free sensation alone, and it is supervised -- the
# task fixes one tag, so the fly may simply learn what that region feels like.


def sensation_features(child_plain: np.ndarray, parents_plain) -> np.ndarray:
    """Tag-free multiscale relation plus its local motion: ``[R_i, dR_i]``.

    Exactly what the fly receives at inference. No tag is encoded anywhere in
    this path.
    """
    from .semantic_hierarchy import multiscale_relations

    relations, _ = multiscale_relations(child_plain, parents_plain)
    deltas = np.zeros_like(relations)
    if len(relations) > 1:
        deltas[1:] = relations[1:] - relations[:-1]
    return np.concatenate([relations, deltas], axis=1).astype(np.float32)


def relative_position(count: int) -> np.ndarray:
    """Position in the document, as a fraction.

    The control that matters most here and would otherwise manufacture a false
    positive: a dispositivo sits at the end of a decision, so position alone is a
    strong predictor. Any sensation feature has to beat it to be worth anything.
    """
    if count <= 1:
        return np.zeros(max(count, 0), dtype=np.float32)
    return (np.arange(count, dtype=np.float32) / (count - 1)).astype(np.float32)


def leave_one_document_out_auprc(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    *,
    penalty: float = 1.0,
) -> float:
    """Ridge probe scored on held-out documents.

    Leave-one-document-out rather than a random chunk split: chunks inside one
    document are not independent, and a random split would let the probe see the
    same document's neighbours at training time and report a number that does not
    survive a new document.
    """
    design = np.hstack([features.astype(np.float64), np.ones((len(features), 1))])
    truth = np.asarray(labels, dtype=np.float64)
    predictions = np.zeros(len(truth))
    for document in np.unique(groups):
        held_out = groups == document
        train_x, train_y = design[~held_out], truth[~held_out]
        gram = train_x.T @ train_x
        scale = penalty * float(np.trace(gram)) / gram.shape[0]
        weights = np.linalg.solve(gram + scale * np.eye(gram.shape[0]), train_x.T @ train_y)
        predictions[held_out] = design[held_out] @ weights
    return average_precision(predictions, np.asarray(labels, dtype=bool))
