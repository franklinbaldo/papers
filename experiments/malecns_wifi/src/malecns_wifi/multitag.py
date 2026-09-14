"""Run 1: frozen-state decoding of multiple tags from a tag-free sensation.

The claim this run can support is deliberately narrower than the goal. It asks
whether the state MaleCNS produces from a tag-free sensation contains enough
information to place several tags better than the controls do. It does **not**
show that the fly learned anything: with the recurrent weights frozen and a ridge
readout, the association lives entirely in the readout.

    Run 1  frozen-state decoding      "is there a useful representation in the state?"
    Run 2  conditioned interface      "does training the interface with reward make
                                       the fly tag without reward at inference?"

Training uses the human mask to decide *when* there is food and the tag identity
to decide *which flavour*. At inference nothing of that exists: no tag, no mask,
no food, only the sensation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from .encoder_gate import average_precision
from .semantic_food import conditioned_food, tag_flavour


@dataclass(frozen=True)
class MultitagSpec:
    """Grid for the first CPU run."""

    flavour_dimension: int = 32
    leak: float = 0.4
    gain: float = 0.95
    steps_per_chunk: int = 4
    ridge_penalties: tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0)
    seeds: tuple[int, ...] = (0, 1, 2)
    input_scale: float = 1.0
    representations: tuple[str, ...] = ("absolute", "relations", "absolute_plus_relations")
    flavour_sources: tuple[str, ...] = ("semantic", "random_codebook")
    reservoirs: tuple[str, ...] = field(default=("direct", "malecns"))


def build_flavours(
    tag_embeddings: np.ndarray, spec: MultitagSpec, *, seed: int, source: str
) -> np.ndarray:
    """One flavour vector per tag, matched in energy.

    ``semantic`` projects the tag's own embedding, so the geometry of the tag set
    is carried into the food. ``random_codebook`` replaces it with matched random
    vectors: if semantic flavours decode better than random ones, the tags'
    geometry is contributing something beyond being distinguishable labels.
    """
    count = len(tag_embeddings)
    if source == "semantic":
        rows = [
            tag_flavour(tag_embeddings[index], spec.flavour_dimension, seed=seed)
            for index in range(count)
        ]
    elif source == "random_codebook":
        rng = np.random.default_rng(seed + 9001)
        rows = [rng.normal(size=spec.flavour_dimension).astype(np.float32) for _ in range(count)]
    else:
        raise ValueError(f"unknown flavour source {source!r}")
    flavours = np.stack(rows).astype(np.float32)
    return flavours / np.maximum(np.linalg.norm(flavours, axis=1, keepdims=True), 1e-12)


def food_targets(tag_masks: np.ndarray, flavours: np.ndarray) -> np.ndarray:
    """``food_t = sum_T M_t^T * flavour(T)``: where and, by direction, which.

    Summing over tags is what makes this a multi-tag problem rather than several
    independent ones: a chunk covered by two tags tastes of both, and the readout
    has to resolve the mixture.
    """
    return (np.asarray(tag_masks, dtype=np.float32) @ flavours).astype(np.float32)


def interpolate(features: np.ndarray, steps: int) -> tuple[np.ndarray, np.ndarray]:
    """Smooth the chunk sequence and return the index of the chunk each step serves."""
    values = np.asarray(features, dtype=np.float32)
    if steps < 1:
        raise ValueError("steps_per_chunk must be >= 1")
    if len(values) == 1 or steps == 1:
        return values, np.arange(len(values))
    pieces, owners = [values[:1]], [np.zeros(1, dtype=np.int64)]
    for index in range(1, len(values)):
        alpha = np.linspace(1.0 / steps, 1.0, steps, dtype=np.float32)[:, None]
        pieces.append(values[index - 1] + alpha * (values[index] - values[index - 1]))
        owners.append(np.full(steps, index, dtype=np.int64))
    return np.vstack(pieces), np.concatenate(owners)


def reservoir_states(
    operator,
    sensation: np.ndarray,
    *,
    input_weights: np.ndarray,
    readout_indices: np.ndarray,
    input_indices: np.ndarray,
    spec: MultitagSpec,
) -> np.ndarray:
    """Drive the frozen operator with the sensation and read the descending neurons.

    One chunk's state is the reservoir state at the last interpolated step that
    belongs to that chunk, so the readout is aligned with the annotation without
    the fly ever being told where a chunk boundary is.
    """
    neurons = operator.shape[0]
    path, owners = interpolate(sensation, spec.steps_per_chunk)
    state = np.zeros(neurons, dtype=np.float32)
    collected = np.zeros((len(sensation), readout_indices.size), dtype=np.float32)

    drive = np.zeros(neurons, dtype=np.float32)
    for step in range(len(path)):
        drive[:] = 0.0
        drive[input_indices] = input_weights @ path[step]
        pre = (operator @ state) * np.float32(spec.gain) + drive
        state = ((1.0 - spec.leak) * state + spec.leak * np.tanh(pre)).astype(
            np.float32, copy=False
        )
        collected[owners[step]] = state[readout_indices]
    return collected


def ridge_multioutput(features: np.ndarray, targets: np.ndarray, penalty: float) -> np.ndarray:
    samples, dimensions = features.shape
    design = np.hstack([features, np.ones((samples, 1))]).astype(np.float64)
    if dimensions + 1 <= samples:
        gram = design.T @ design
        scale = penalty * float(np.trace(gram)) / gram.shape[0]
        return np.linalg.solve(gram + scale * np.eye(gram.shape[0]), design.T @ targets)
    gram = design @ design.T
    scale = penalty * float(np.trace(gram)) / gram.shape[0]
    return design.T @ np.linalg.solve(gram + scale * np.eye(samples), targets)


def decode(predictions: np.ndarray, flavours: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Predicted food -> (how much food, which tag).

    Magnitude answers "is there a tag here", direction answers "which one". The
    two are read from the same predicted vector, which is the point of making
    flavour a direction rather than a label.
    """
    magnitude = np.linalg.norm(predictions, axis=1)
    unit = predictions / np.maximum(magnitude[:, None], 1e-12)
    return magnitude, np.argmax(unit @ flavours.T, axis=1)


def evaluate(
    features: np.ndarray,
    tag_masks: np.ndarray,
    flavours: np.ndarray,
    groups: np.ndarray,
    *,
    penalties,
) -> dict:
    """Leave-one-document-out decode of food from a representation.

    The ridge penalty is selected inside the training folds only -- on a split of
    the training documents -- so the held-out documents never influence it. A
    penalty chosen on held-out performance would be the selection leak this whole
    protocol exists to avoid.
    """
    targets = food_targets(tag_masks, flavours)
    inside = tag_masks.max(axis=1) > 0
    truth = np.argmax(tag_masks, axis=1)
    predictions = np.zeros_like(targets)
    chosen_penalties = []

    for document in np.unique(groups):
        held_out = groups == document
        train_index = np.flatnonzero(~held_out)
        inner_groups = groups[train_index]
        inner_documents = np.unique(inner_groups)
        validation = inner_documents[: max(1, len(inner_documents) // 5)]
        inner_valid = np.isin(inner_groups, validation)

        best, best_penalty = -np.inf, penalties[0]
        for penalty in penalties:
            weights = ridge_multioutput(
                features[train_index][~inner_valid], targets[train_index][~inner_valid], penalty
            )
            scored = np.hstack(
                [features[train_index][inner_valid], np.ones((int(inner_valid.sum()), 1))]
            ) @ weights
            magnitude, _ = decode(scored, flavours)
            score = average_precision(magnitude, inside[train_index][inner_valid])
            if np.isfinite(score) and score > best:
                best, best_penalty = score, penalty
        chosen_penalties.append(best_penalty)

        weights = ridge_multioutput(features[train_index], targets[train_index], best_penalty)
        predictions[held_out] = (
            np.hstack([features[held_out], np.ones((int(held_out.sum()), 1))]) @ weights
        )

    magnitude, predicted_tag = decode(predictions, flavours)
    correct = predicted_tag[inside] == truth[inside]
    return {
        "inside_auprc": float(average_precision(magnitude, inside)),
        "tag_accuracy_on_true_spans": float(correct.mean()) if correct.size else float("nan"),
        "tag_chance": float(1.0 / flavours.shape[0]),
        "random_auprc": float(inside.mean()),
        "penalties": [float(p) for p in chosen_penalties],
    }
