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
    readouts: tuple[str, ...] = ("descending",)
    step_grid: tuple[int, ...] = (4,)
    # F3 requires each operator to pick its own gain on validation: rho = 1 does
    # not put MaleCNS and a random ESN in the same dynamical regime, because the
    # first has typical gain ~0.295 at unit radius and the second a far flatter
    # spectrum. Running everyone at 0.95 compares operating points, not wirings.
    gain_grid: tuple[float, ...] = (0.25, 0.5, 0.95, 1.5, 2.5, 4.0)
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


def unit_rows(features: np.ndarray) -> np.ndarray:
    """Scale every sensation vector to unit norm before it is projected.

    Without this the current entering the fly depends on the representation's
    dimensionality rather than its content. With ``w ~ N(0, s^2/d)`` the drive RMS
    is ``s * ||x|| / sqrt(d)``, so a 1540-dimensional relation block receives half
    the drive a 384-dimensional embedding block does, and a 1024-dimensional
    encoder receives 1.6x less than a 384-dimensional one. Any difference between
    representations or encoders would then be partly a difference in how hard the
    fly was driven.
    """
    values = np.asarray(features, dtype=np.float32)
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)


def build_readout(
    kind: str,
    descending: np.ndarray,
    neurons: int,
    *,
    seed: int,
    width: int | None = None,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Choose where the state is read from, and how.

    A frozen operator losing to the direct probe has two very different
    explanations: the topology computed nothing, or we are reading the wrong door.
    The descending neurons are the biologically right output, but they are 1,314
    of 165,122, and prior work reads the whole state instead. These ablations
    separate the two explanations.

    Returns ``(indices, projection)``. When ``projection`` is not ``None`` the
    readout is ``projection @ state[indices]`` rather than ``state[indices]``.

    * ``descending``   -- the anatomical output population.
    * ``random``       -- the same number of neurons drawn at random. If this
      matches the descending readout, "descending" was a size, not a place.
    * ``projected``    -- a fixed random projection of the *whole* state down to
      the same width. Same readout budget, no anatomical selection, but nothing
      discarded before the projection.
    * ``full``         -- the entire state, as an upper bound on what any readout
      of this operator could recover. Not a condition to claim, a ceiling to
      measure against.
    """
    rng = np.random.default_rng(seed + 4242)
    size = width or descending.size
    if kind == "descending":
        return descending, None
    if kind == "random":
        return np.sort(rng.choice(neurons, size=size, replace=False)), None
    if kind == "projected":
        # Sparse rather than dense: a dense 1314 x 165122 projection is 868MB and
        # buys nothing. Achlioptas-style sparse projections preserve distances at
        # a density of about 1/sqrt(n), which here is ~0.25% and a few hundred
        # thousand nonzeros.
        density = 1.0 / np.sqrt(neurons)
        projection = sp.random(
            size,
            neurons,
            density=density,
            format="csr",
            dtype=np.float32,
            random_state=np.random.default_rng(seed + 4242),
            data_rvs=lambda count: rng.choice([-1.0, 1.0], size=count).astype(np.float32),
        )
        projection = projection * np.float32(1.0 / np.sqrt(density * neurons))
        return np.arange(neurons), projection
    if kind == "full":
        return np.arange(neurons), None
    raise ValueError(f"unknown readout {kind!r}")


def calibrate_drive(
    projection: np.ndarray,
    features: np.ndarray,
    groups: np.ndarray,
    *,
    target_rms: float = 0.05,
) -> dict:
    """Scale the input projection so every representation delivers the same energy.

    The scalar is measured as ``RMS(P x)`` over the **training** documents of each
    fold and applied unchanged to the held-out one, so the calibration never sees
    held-out statistics.

    Matching on a formula in ``d`` is not enough: ``absolute`` and ``relations``
    have quite different covariance, so equal width would still not mean equal
    current. Measuring the realised RMS fixes the volume while leaving each
    representation's internal structure untouched.

    Returns the per-fold scalars and their spread. On this corpus the spread is
    about 0.03-0.05%, which moves the reservoir states by 0.014% -- so a single
    pass at the mean scalar is numerically indistinguishable from recomputing the
    states seventeen times, and the measurement is reported so that claim is
    checkable rather than assumed.
    """
    unit = unit_rows(features)
    projected = unit @ np.asarray(projection, dtype=np.float32).T
    scalars = {}
    for document in np.unique(groups):
        train = groups != document
        rms = float(np.sqrt(np.mean(projected[train] ** 2)))
        scalars[int(document)] = target_rms / max(rms, 1e-12)
    values = np.asarray(list(scalars.values()))
    return {
        "per_fold": scalars,
        "mean": float(values.mean()),
        "spread": float(values.max() / max(values.min(), 1e-12)),
        "target_rms": target_rms,
    }


def reservoir_states(
    operator,
    sensation: np.ndarray,
    *,
    input_weights: np.ndarray,
    readout_indices: np.ndarray,
    input_indices: np.ndarray,
    spec: MultitagSpec,
    scale: float = 1.0,
    readout_projection: np.ndarray | None = None,
) -> tuple[np.ndarray, float]:
    """Drive the frozen operator with the sensation and read the descending neurons.

    One chunk's state is the reservoir state at the last interpolated step that
    belongs to that chunk, so the readout is aligned with the annotation without
    the fly ever being told where a chunk boundary is.

    Returns the per-chunk states and the measured drive RMS, so the energy
    actually delivered is reported rather than assumed.
    """
    neurons = operator.shape[0]
    path, owners = interpolate(unit_rows(sensation), spec.steps_per_chunk)
    state = np.zeros(neurons, dtype=np.float32)
    width = (
        readout_projection.shape[0] if readout_projection is not None else readout_indices.size
    )
    collected = np.zeros((len(sensation), width), dtype=np.float32)

    # One GEMM for the whole document instead of a small matrix-vector product per
    # step: the projection is the second largest cost after the sparse product and
    # BLAS does it an order of magnitude faster in bulk.
    projected = (np.asarray(input_weights, dtype=np.float32) @ path.T) * np.float32(scale)
    drive = np.zeros(neurons, dtype=np.float32)
    drive_energy = 0.0
    for step in range(len(path)):
        drive[:] = 0.0
        drive[input_indices] = projected[:, step]
        drive_energy += float(np.mean(projected[:, step] ** 2))
        pre = (operator @ state) * np.float32(spec.gain) + drive
        state = ((1.0 - spec.leak) * state + spec.leak * np.tanh(pre)).astype(
            np.float32, copy=False
        )
        probed = state[readout_indices]
        collected[owners[step]] = (
            readout_projection @ probed if readout_projection is not None else probed
        )
    return collected, float(np.sqrt(drive_energy / max(len(path), 1)))


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


def _macro_tag_ap(predictions: np.ndarray, tag_masks: np.ndarray, flavours: np.ndarray) -> float:
    """Macro one-vs-rest AP over tags, the metric the decision rule is written in."""
    scores = []
    for index in range(flavours.shape[0]):
        target = np.asarray(tag_masks)[:, index] > 0
        if target.any() and not target.all():
            scores.append(average_precision(predictions @ flavours[index], target))
    finite = [value for value in scores if np.isfinite(value)]
    return float(np.mean(finite)) if finite else float("nan")


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
            # Selected on the metric the decision rule uses. Choosing the penalty
            # by any-tag AUPRC and then adjudicating F2/F3 on macro per-tag AUPRC
            # optimises one quantity and reports another, and with prevalences
            # from 8 to 18 chunks that can reorder operators.
            score = _macro_tag_ap(scored, tag_masks[train_index][inner_valid], flavours)
            if np.isfinite(score) and score > best:
                best, best_penalty = score, penalty
        chosen_penalties.append(best_penalty)

        weights = ridge_multioutput(features[train_index], targets[train_index], best_penalty)
        predictions[held_out] = (
            np.hstack([features[held_out], np.ones((int(held_out.sum()), 1))]) @ weights
        )

    magnitude, predicted_tag = decode(predictions, flavours)
    correct = predicted_tag[inside] == truth[inside]

    # Per-document scores, so a mean can be checked against its spread. A gain
    # carried by two documents out of seventeen looks identical to a broad one in
    # the average, and with 8-18 positive chunks per tag a single document moving
    # is enough to do that.
    per_document = {}
    for document in np.unique(groups):
        rows = groups == document
        local_inside = inside[rows]
        if not local_inside.any() or local_inside.all():
            continue
        local = {}
        local["inside_auprc"] = float(average_precision(magnitude[rows], local_inside))
        tag_scores = []
        for index in range(flavours.shape[0]):
            target = tag_masks[rows, index] > 0
            if target.any() and not target.all():
                tag_scores.append(
                    float(average_precision(predictions[rows] @ flavours[index], target))
                )
        local["macro_tag_auprc"] = float(np.mean(tag_scores)) if tag_scores else float("nan")
        local["tags_present"] = len(tag_scores)
        per_document[str(int(document))] = local

    # Three axes, because "any-tag AUPRC" alone conflates them and is not
    # comparable across corpora with different positive rates. The union of nine
    # tags covers 24.8% of chunks against a single tag's 5.1%, so a higher any-tag
    # score is partly just a commoner event. Per-tag AP is one-vs-rest at each
    # tag's own prevalence, and its macro average is what "does this representation
    # help identify particular semantic roles" actually means.
    per_tag = {}
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        if not target.any() or target.all():
            per_tag[index] = float("nan")
            continue
        # Score this tag by how much of the predicted food points its way.
        affinity = predictions @ flavours[index]
        per_tag[index] = float(average_precision(affinity, target))
    finite = [value for value in per_tag.values() if np.isfinite(value)]

    return {
        "inside_auprc": float(average_precision(magnitude, inside)),
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "per_tag_prevalence": {
            str(index): float((tag_masks[:, index] > 0).mean())
            for index in range(flavours.shape[0])
        },
        "tag_accuracy_on_true_spans": float(correct.mean()) if correct.size else float("nan"),
        "tag_chance": float(1.0 / flavours.shape[0]),
        "random_auprc": float(inside.mean()),
        "macro_prevalence": float(np.mean([(tag_masks[:, i] > 0).mean()
                                           for i in range(flavours.shape[0])])),
        "per_document": per_document,
        "penalties": [float(p) for p in chosen_penalties],
    }


def evaluate_exact_per_fold(
    operator,
    block: np.ndarray,
    tag_masks: np.ndarray,
    flavours: np.ndarray,
    groups: np.ndarray,
    *,
    input_weights: np.ndarray,
    calibration: dict,
    readout_indices: np.ndarray,
    input_indices: np.ndarray,
    spec: MultitagSpec,
    penalties,
) -> dict:
    """Leave-one-document-out with the drive recalibrated inside every fold.

    The screening path calibrates once at the mean scalar, which on this corpus
    moves the states by 0.014% against recomputing them per fold -- measured, not
    assumed. This is the exact version: each fold gets states built with a scalar
    that saw only that fold's training documents, at seventeen times the cost.

    Use it for the comparisons that reach a paper, not for screening: paying
    2.7 hours to rank conditions that the cheap pass already shows are far apart
    buys nothing, while the number that gets published should carry no shadow of
    leakage at all.
    """
    targets = food_targets(tag_masks, flavours)
    inside = tag_masks.max(axis=1) > 0
    predictions = np.zeros_like(targets)
    documents = np.unique(groups)

    for held_out_document in documents:
        scale = calibration["per_fold"][int(held_out_document)]
        states = np.vstack([
            reservoir_states(
                operator,
                block[groups == document],
                input_weights=input_weights,
                readout_indices=readout_indices,
                input_indices=input_indices,
                spec=spec,
                scale=scale,
            )[0]
            for document in documents
        ])
        held_out = groups == held_out_document
        weights = ridge_multioutput(states[~held_out], targets[~held_out], penalties[0])
        best, best_weights = -np.inf, weights
        inner = groups[~held_out]
        validation = np.unique(inner)[: max(1, len(np.unique(inner)) // 5)]
        inner_valid = np.isin(inner, validation)
        for penalty in penalties:
            candidate = ridge_multioutput(
                states[~held_out][~inner_valid], targets[~held_out][~inner_valid], penalty
            )
            scored = np.hstack([
                states[~held_out][inner_valid], np.ones((int(inner_valid.sum()), 1))
            ]) @ candidate
            magnitude, _ = decode(scored, flavours)
            score = average_precision(magnitude, inside[~held_out][inner_valid])
            if np.isfinite(score) and score > best:
                best = score
                best_weights = ridge_multioutput(
                    states[~held_out], targets[~held_out], penalty
                )
        predictions[held_out] = (
            np.hstack([states[held_out], np.ones((int(held_out.sum()), 1))]) @ best_weights
        )

    magnitude, predicted_tag = decode(predictions, flavours)
    truth = np.argmax(tag_masks, axis=1)
    correct = predicted_tag[inside] == truth[inside]
    per_tag = {}
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        per_tag[index] = (
            float(average_precision(predictions @ flavours[index], target))
            if target.any() and not target.all()
            else float("nan")
        )
    finite = [value for value in per_tag.values() if np.isfinite(value)]
    return {
        "inside_auprc": float(average_precision(magnitude, inside)),
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "tag_accuracy_on_true_spans": float(correct.mean()) if correct.size else float("nan"),
        "tag_chance": float(1.0 / flavours.shape[0]),
        "random_auprc": float(inside.mean()),
        "calibration_mode": "exact_per_fold",
    }


# Bump when the meaning of a cached state changes, so old caches cannot be
# served to new code that computes something different under the same inputs.
CACHE_SCHEMA = 2


def run_fingerprint(**parts) -> str:
    """Hash of everything that changes the states or the scores.

    The cache key used to be ``operator__representation__seed``, which omits
    gain, leak, steps per chunk, the null draw, the populations, the drive
    calibration and the graph itself. Running a gain grid against that cache
    would silently load gain-0.95 states and report them as gain-2.5 -- a wrong
    number with no error, produced by the machinery we had just made central to
    the workflow. Identity has to cover everything that could differ.
    """
    import hashlib
    import json as _json

    payload = _json.dumps(parts, sort_keys=True, default=str).encode("utf-8")
    return hashlib.blake2b(payload, digest_size=10).hexdigest()


def array_fingerprint(array: np.ndarray) -> str:
    """Content hash of a feature block, so a changed corpus invalidates a cache."""
    import hashlib

    values = np.ascontiguousarray(np.asarray(array, dtype=np.float32))
    digest = hashlib.blake2b(values.tobytes(), digest_size=10)
    digest.update(str(values.shape).encode())
    return digest.hexdigest()


def evaluate_nested(
    states_by_gain: dict,
    tag_masks: np.ndarray,
    flavours: np.ndarray,
    groups: np.ndarray,
    *,
    penalties,
) -> dict:
    """Leave-one-document-out with ``(gain, ridge)`` chosen inside each outer fold.

    The previous form picked one gain using a leave-one-out pass over ~80% of the
    documents and then evaluated every document at that gain -- so for any
    document inside that 80%, its own performance had helped choose the gain later
    used to score it. The comment said "never the held-out one"; the code did not.

    Here the outer document is removed first. The remaining sixteen choose both
    the gain and the ridge penalty among themselves, the readout is fitted on
    those sixteen at that setting, and only then is the held-out document
    predicted. The selected gain therefore varies by fold, which is what a nested
    protocol looks like, and the seventeen predictions are pooled once at the end.
    """
    gains = sorted(g for g in states_by_gain if g > 0)
    if not gains:
        raise ValueError("no positive gain available to select from")
    any_states = states_by_gain[gains[0]]
    targets = food_targets(tag_masks, flavours)
    predictions = np.zeros_like(targets)
    inside = tag_masks.max(axis=1) > 0
    chosen: dict[str, dict] = {}

    for document in np.unique(groups):
        outer = groups == document
        inner_groups = groups[~outer]
        inner_documents = np.unique(inner_groups)
        # A split of the sixteen; the seventeenth is not present at all.
        validation = inner_documents[: max(1, len(inner_documents) // 4)]
        inner_valid = np.isin(inner_groups, validation)

        best = (-np.inf, gains[0], penalties[0])
        for gain in gains:
            states = states_by_gain[gain][~outer]
            for penalty in penalties:
                weights = ridge_multioutput(
                    states[~inner_valid], targets[~outer][~inner_valid], penalty
                )
                scored = np.hstack(
                    [states[inner_valid], np.ones((int(inner_valid.sum()), 1))]
                ) @ weights
                score = _macro_tag_ap(
                    scored, tag_masks[~outer][inner_valid], flavours
                )
                if np.isfinite(score) and score > best[0]:
                    best = (score, gain, penalty)

        _, gain, penalty = best
        chosen[str(int(document))] = {"gain": float(gain), "ridge": float(penalty)}
        states = states_by_gain[gain]
        weights = ridge_multioutput(states[~outer], targets[~outer], penalty)
        predictions[outer] = (
            np.hstack([states[outer], np.ones((int(outer.sum()), 1))]) @ weights
        )

    magnitude, predicted_tag = decode(predictions, flavours)
    truth = np.argmax(tag_masks, axis=1)
    correct = predicted_tag[inside] == truth[inside]
    per_tag = {}
    for index in range(flavours.shape[0]):
        target = tag_masks[:, index] > 0
        per_tag[index] = (
            float(average_precision(predictions @ flavours[index], target))
            if target.any() and not target.all()
            else float("nan")
        )
    finite = [v for v in per_tag.values() if np.isfinite(v)]
    return {
        "inside_auprc": float(average_precision(magnitude, inside)),
        "macro_tag_auprc": float(np.mean(finite)) if finite else float("nan"),
        "per_tag_auprc": {str(k): v for k, v in per_tag.items()},
        "tag_accuracy_on_true_spans": float(correct.mean()) if correct.size else float("nan"),
        "random_auprc": float(inside.mean()),
        "selected_by_fold": chosen,
        "selection": "nested: (gain, ridge) chosen inside each outer fold",
    }
