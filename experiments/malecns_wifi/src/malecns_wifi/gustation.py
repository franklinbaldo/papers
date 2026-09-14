"""Semantic gustation: learning a function that gives text a taste.

Not "feed during training, remove at inference". The flavourizer learns a
transduction from meaning to a small number of taste channels, so that at
inference the text evokes its own flavour with no annotation present:

    training   text -> semantic field -> flavourizer -> predicted flavour
               gold tag                                -> target flavour
               the error between them trains the flavourizer

    inference  text -> semantic field -> flavourizer -> "this passage tastes
               like X" -> MaleCNS -> readout -> tags

That is closer to sensory remapping than to reward conditioning. The fly is not
being paid when it is right; it is being given a new sense.

**Tags are compositions, not papillae.** There is no "lasagna" taste receptor;
there is sweet, salt, sour, and lasagna is a mixture. So the codebook maps each
tag to a blend of ``k`` latent axes with ``k`` well below the number of tags,
which forces tags to share axes. If ``k`` approaches the tag count the codebook
becomes a rotated one-hot, the flavourizer is just a classifier, and the whole
construction is circular -- so that condition is measured and refused rather
than trusted.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .encoder_gate import leave_one_document_out_auprc


@dataclass(frozen=True)
class FlavourSpec:
    """Shape of the gustatory interface."""

    channels: int = 4
    ridge: float = 1.0
    seed: int = 0
    max_channel_fraction: float = 0.6

    def check(self, tags: int) -> None:
        if self.channels >= tags * self.max_channel_fraction:
            raise ValueError(
                f"{self.channels} flavour channels for {tags} tags is not a composition: "
                f"with k close to the tag count the codebook is a rotated one-hot and the "
                f"flavourizer is a classifier. Use k <= {int(tags * self.max_channel_fraction)}."
            )


def flavour_codebook(
    tag_embeddings: np.ndarray, spec: FlavourSpec, *, source: str = "semantic"
) -> tuple[np.ndarray, dict]:
    """Map each tag to a blend of ``k`` latent taste axes.

    ``semantic`` projects the tags' own embeddings, so semantically close tags
    taste similar -- the property that makes this a sense rather than a labelling.
    ``random`` is the matched control.

    The diagnostics say how far the codebook is from being a disguised one-hot.
    ``mean_abs_cosine`` near zero means the tags occupy near-orthogonal axes and
    are individually decodable; a real composition has tags overlapping.
    """
    tags = len(tag_embeddings)
    spec.check(tags)
    rng = np.random.default_rng(spec.seed)

    if source == "semantic":
        source_matrix = np.asarray(tag_embeddings, dtype=np.float32)
        projection = rng.normal(
            scale=1.0 / np.sqrt(source_matrix.shape[1]),
            size=(source_matrix.shape[1], spec.channels),
        ).astype(np.float32)
        codebook = source_matrix @ projection
    elif source == "random":
        codebook = rng.normal(size=(tags, spec.channels)).astype(np.float32)
    else:
        raise ValueError(f"unknown codebook source {source!r}")

    codebook = codebook / np.maximum(np.linalg.norm(codebook, axis=1, keepdims=True), 1e-12)
    gram = codebook @ codebook.T
    off_diagonal = gram[~np.eye(tags, dtype=bool)]
    return codebook.astype(np.float32), {
        "channels": spec.channels,
        "tags": tags,
        "mean_abs_cosine": float(np.abs(off_diagonal).mean()),
        "max_abs_cosine": float(np.abs(off_diagonal).max()),
        "rank": int(np.linalg.matrix_rank(codebook)),
        "note": (
            "tags share axes by construction because k < tags; mean_abs_cosine near "
            "zero would mean the codebook is a rotated one-hot despite that"
        ),
    }


def target_flavour(tag_masks: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """The taste a passage *should* have: the blend of the tags covering it."""
    return (np.asarray(tag_masks, dtype=np.float32) @ codebook).astype(np.float32)


def fit_flavourizer(
    semantics: np.ndarray,
    targets: np.ndarray,
    groups: np.ndarray,
    spec: FlavourSpec,
) -> np.ndarray:
    """Learn semantics -> flavour, held out by document.

    Deliberately linear and heavily regularised. A powerful flavourizer would
    reproduce the tags inside the taste channels, and the interesting claim is
    that a *small, weak* transduction into few channels is enough to make meaning
    usable by the operator.
    """
    design = np.hstack([semantics.astype(np.float64), np.ones((len(semantics), 1))])
    predicted = np.zeros_like(np.asarray(targets, dtype=np.float64))
    for document in np.unique(groups):
        held_out = groups == document
        train = design[~held_out]
        gram = train.T @ train
        penalty = spec.ridge * float(np.trace(gram)) / gram.shape[0]
        weights = np.linalg.solve(
            gram + penalty * np.eye(gram.shape[0]), train.T @ targets[~held_out]
        )
        predicted[held_out] = design[held_out] @ weights
    return predicted.astype(np.float32)


def flavour_only_baseline(
    flavour: np.ndarray, tag_masks: np.ndarray, groups: np.ndarray, *, penalty: float = 1.0
) -> dict:
    """The control that decides whether the fly is doing anything.

    If ``k`` learned taste channels already recover the tags on their own, the
    operator is decoration. For the gustation story to survive we need

        flavour-only direct  <  flavour + MaleCNS

    and ideally ``flavour + MaleCNS > flavour + degree-null``. This is the first
    of those, and it is the cheapest to run, so it should be run first.
    """
    inside = np.asarray(tag_masks).max(axis=1) > 0
    return {
        "flavour_only_auprc": float(
            leave_one_document_out_auprc(flavour, inside, groups, penalty=penalty)
        ),
        "random_auprc": float(inside.mean()),
        "channels": int(flavour.shape[1]),
    }


def gustation_conditions(
    semantics: np.ndarray,
    tag_masks: np.ndarray,
    tag_embeddings: np.ndarray,
    groups: np.ndarray,
    spec: FlavourSpec,
    *,
    source: str = "semantic",
) -> dict:
    """The three flavour streams the experiment compares.

    * ``semantic_only`` — the field goes into the operator unflavoured.
    * ``oracle_flavour`` — the true taste is supplied. A diagnostic ceiling, never
      a result: it tells us what the operator could do if transduction were
      perfect, so a failure of the learned version can be attributed to the
      transduction rather than to the operator.
    * ``learned_flavour`` — the text evokes its own taste, held out by document.

    Reading: oracle works and learned does not means the problem is learning
    text-to-taste. Learned works and semantic-only does not means the
    low-dimensional gustatory interface is what makes meaning usable by the
    topology -- which is the claim worth making.
    """
    codebook, diagnostics = flavour_codebook(tag_embeddings, spec, source=source)
    oracle = target_flavour(tag_masks, codebook)
    learned = fit_flavourizer(semantics, oracle, groups, spec)
    return {
        "codebook": codebook,
        "codebook_diagnostics": diagnostics,
        "streams": {
            "semantic_only": np.asarray(semantics, dtype=np.float32),
            "oracle_flavour": oracle,
            "learned_flavour": learned,
        },
        "transduction_r2": float(
            1.0
            - np.sum((oracle - learned) ** 2) / max(float(np.sum((oracle - oracle.mean(0)) ** 2)), 1e-12)
        ),
    }


def effective_delay_window(leak: float, steps_per_chunk: int, *, floor: float = 0.05) -> int:
    """Chunks of history the recurrence can still be carrying.

    A leaky integrator retains ``(1 - leak)^n`` of a past input after ``n`` steps.
    The window is the number of *chunks* after which that falls below ``floor``,
    so the delay baseline covers roughly the same temporal reach the operator has
    rather than a number chosen by taste.
    """
    if not 0.0 < leak <= 1.0:
        raise ValueError("leak must be in (0, 1]")
    retention = 1.0 - leak
    if retention <= 0:
        return 1
    steps = np.log(floor) / np.log(retention)
    return max(1, int(np.ceil(steps / max(steps_per_chunk, 1))))


def delayed_stack(flavour: np.ndarray, groups: np.ndarray, horizon: int) -> np.ndarray:
    """``[z_t, z_{t-1}, ..., z_{t-h}]`` within each document.

    The control that keeps "what does the topology do that a readout cannot" an
    honest question. Without it the direct probe sees ``f(z_t)`` while the
    operator sees ``f(z_t, z_{t-1}, ...)``, and any win by the fly could simply be
    memory rather than topology.

    History never crosses a document boundary: a document's first chunk has no
    past, and borrowing the previous document's would be leakage dressed as
    context.
    """
    values = np.asarray(flavour, dtype=np.float32)
    stacked = [values]
    for lag in range(1, horizon + 1):
        shifted = np.zeros_like(values)
        for document in np.unique(groups):
            rows = np.flatnonzero(groups == document)
            if len(rows) > lag:
                shifted[rows[lag:]] = values[rows[:-lag]]
        stacked.append(shifted)
    return np.hstack(stacked)


def flavour_delay_baseline(
    flavour: np.ndarray,
    tag_masks: np.ndarray,
    groups: np.ndarray,
    *,
    horizon: int,
    penalty: float = 1.0,
) -> dict:
    """Can plain temporal memory over the taste channels do it, with no operator?"""
    inside = np.asarray(tag_masks).max(axis=1) > 0
    stacked = delayed_stack(flavour, groups, horizon)
    return {
        "flavour_delay_auprc": float(
            leave_one_document_out_auprc(stacked, inside, groups, penalty=penalty)
        ),
        "horizon_chunks": int(horizon),
        "dimensions": int(stacked.shape[1]),
        "random_auprc": float(inside.mean()),
    }


def flavour_expansion_baseline(
    flavour: np.ndarray,
    tag_masks: np.ndarray,
    groups: np.ndarray,
    *,
    hidden: int = 16,
    penalty: float = 1.0,
    seed: int = 0,
) -> dict:
    """Is it just a cheap nonlinear expansion, with no recurrence at all?

    A fixed random ``k -> hidden`` tanh layer read by the same ridge. Deliberately
    tiny: a large MLP would become the system rather than a baseline for it, which
    is the mirror image of the mistake the mixer constraint avoids.
    """
    rng = np.random.default_rng(seed)
    values = np.asarray(flavour, dtype=np.float32)
    projection = rng.normal(scale=1.0 / np.sqrt(values.shape[1]), size=(values.shape[1], hidden))
    expanded = np.tanh(values @ projection.astype(np.float32))
    inside = np.asarray(tag_masks).max(axis=1) > 0
    return {
        "flavour_expansion_auprc": float(
            leave_one_document_out_auprc(expanded, inside, groups, penalty=penalty)
        ),
        "hidden": int(hidden),
        "random_auprc": float(inside.mean()),
    }
