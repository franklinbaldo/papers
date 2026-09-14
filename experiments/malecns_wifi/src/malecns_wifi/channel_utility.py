"""Conditional utility of each channel inside the bank, and the gated mixer.

Two separate questions, deliberately not run as one experiment.

**Does the bank carry complementary information?** Asked with a plain regularised
probe and no fly, because a channel that is useless alone can still be the one
that resolves a boundary. The test is not `relations vs absolute`; it is whether
removing a channel costs anything:

    delta_k = score(B) - score(B \\ C_k)

**How should the field be presented to the fly?** With a mixer weak enough that it
cannot do the task: one non-negative scalar per channel, shared across every
document, position and tag, constrained to the simplex. Nine numbers can
calibrate sense organs; they cannot tag.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .encoder_gate import average_precision, leave_one_document_out_auprc


@dataclass(frozen=True)
class Channel:
    """One self-contained channel: an encoder comparing itself at two scales."""

    name: str
    values: np.ndarray
    encoder: str
    scale: int
    parent_scale: int | None = None

    @property
    def is_relational(self) -> bool:
        return self.parent_scale is not None


def channel_utility(
    channels: list[Channel],
    labels: np.ndarray,
    groups: np.ndarray,
    *,
    penalty: float = 1.0,
    order: list[str] | None = None,
) -> dict:
    """Singleton, leave-one-out and nested add-one scores for every channel.

    The three measures disagree systematically when channels are correlated, and
    that is expected rather than a defect:

    * ``singleton`` — what the channel carries alone. A fine channel can be
      near-useless here and still matter in the bank.
    * ``leave_one_out`` — what the bank loses without it. **Understates grouped
      importance under collinearity**: if three adjacent scales carry overlapping
      information, each is individually removable and all three score near zero,
      while removing all three would cost a great deal.
    * ``add_one`` — nested, from coarse to fine, each channel added to the bank of
      everything coarser. This is the measure that maps onto the prediction that
      utility rises as scales descend, because it asks what each resolution adds
      *given* the ones above it, which is the question the pyramid poses.

    Report all three. Where leave-one-out is flat and add-one is not, the channels
    are redundant with each other rather than uninformative.
    """
    truth = np.asarray(labels, dtype=bool)
    names = [channel.name for channel in channels]
    by_name = {channel.name: channel for channel in channels}
    sequence = order or names

    def score(selected: list[str]) -> float:
        if not selected:
            return float("nan")
        block = np.hstack([_unit(by_name[name].values) for name in selected])
        return leave_one_document_out_auprc(block, truth, groups, penalty=penalty)

    whole = score(names)
    singleton = {name: score([name]) for name in names}
    leave_one_out = {name: whole - score([n for n in names if n != name]) for name in names}

    add_one, running = {}, []
    previous = float("nan")
    for name in sequence:
        running.append(name)
        current = score(running)
        add_one[name] = current - previous if running[:-1] else current
        previous = current

    return {
        "bank_auprc": whole,
        "random_auprc": float(truth.mean()),
        "singleton": singleton,
        "leave_one_out": leave_one_out,
        "add_one": add_one,
        "nested_order": sequence,
        "note": (
            "leave_one_out understates grouped importance when channels are "
            "correlated; add_one is nested coarse-to-fine and is the measure the "
            "descending-utility prediction is about."
        ),
    }


def _unit(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float32)
    return array / np.maximum(np.linalg.norm(array, axis=1, keepdims=True), 1e-12)


# --- the gated mixer --------------------------------------------------------


def softmax_simplex(logits: np.ndarray) -> np.ndarray:
    """Map free parameters onto the simplex: non-negative, summing to one."""
    shifted = np.asarray(logits, dtype=np.float64) - np.max(logits)
    weights = np.exp(shifted)
    return weights / weights.sum()


def mix_channels(
    channels: list[Channel],
    projections: dict[str, np.ndarray],
    alpha: np.ndarray,
    *,
    target_rms: float = 0.05,
) -> tuple[np.ndarray, dict]:
    """``z_t = sum_k alpha_k P_k C_k,t``, then calibrated to a fixed drive energy.

    ``alpha`` lives on the simplex and is shared across every document, position
    and tag, so it cannot encode where a tag is -- only how loud each sense organ
    is. The final RMS calibration means a bank of nine channels delivers exactly
    the current a bank of two does.
    """
    weights = np.asarray(alpha, dtype=np.float32)
    if weights.size != len(channels):
        raise ValueError("one weight per channel")
    if weights.min() < -1e-6 or abs(float(weights.sum()) - 1.0) > 1e-4:
        raise ValueError("alpha must be non-negative and sum to one")

    mixed, per_channel = None, {}
    for weight, channel in zip(weights, channels, strict=True):
        if channel.name not in projections:
            raise ValueError(f"missing projection for channel {channel.name!r}")
        drive = np.asarray(projections[channel.name], dtype=np.float32) @ _unit(channel.values).T
        per_channel[channel.name] = float(np.sqrt(np.mean(drive * drive)))
        contribution = drive * np.float32(weight)
        mixed = contribution if mixed is None else mixed + contribution

    realised = float(np.sqrt(np.mean(mixed * mixed)))
    mixed = (mixed * np.float32(target_rms / max(realised, 1e-12))).astype(np.float32)
    return mixed, {
        "alpha": {c.name: float(w) for c, w in zip(channels, weights, strict=True)},
        "channel_rms_before_mix": per_channel,
        "pre_scale_rms": realised,
        "realised_rms": float(np.sqrt(np.mean(mixed * mixed))),
        "parameters": int(weights.size),
    }


def fit_channel_gates(
    channels: list[Channel],
    labels: np.ndarray,
    groups: np.ndarray,
    *,
    penalty: float = 1.0,
    steps: int = 200,
    learning_rate: float = 0.2,
    seed: int = 0,
) -> np.ndarray:
    """Learn one scalar per channel, on training documents only.

    Fitted by coordinate-free finite differences on the training folds' score.
    Crude, and deliberately so: the point is nine numbers that cannot tag, not a
    well-optimised mixer. Anything that selected channels per position would be
    doing the tagger's job.
    """
    rng = np.random.default_rng(seed)
    logits = np.zeros(len(channels))

    def objective(values: np.ndarray) -> float:
        weights = softmax_simplex(values)
        block = np.hstack([
            _unit(channel.values) * weight
            for channel, weight in zip(channels, weights, strict=True)
        ])
        score = leave_one_document_out_auprc(block, labels, groups, penalty=penalty)
        return score if np.isfinite(score) else -1.0

    best, best_score = logits.copy(), objective(logits)
    for _ in range(steps):
        candidate = logits + rng.normal(scale=learning_rate, size=logits.size)
        score = objective(candidate)
        if score > best_score:
            best, best_score, logits = candidate.copy(), score, candidate
    return softmax_simplex(best)
