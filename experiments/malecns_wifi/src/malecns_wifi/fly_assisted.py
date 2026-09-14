"""Fly-assisted training for a tagger that does not need the fly at inference.

This is deliberately a different question from Run 1 and Run 2.

Run 1 asks whether a frozen MaleCNS state is a better representation than direct
features. Run 2 asks whether a trainable interface around a frozen MaleCNS can tag
at inference. This module asks a third question:

    can MaleCNS be useful *during training* even when the deployed tagger contains
    no connectome at all?

The final path is always::

    semantic features -> low-rank residual flavourizer -> tag head

The assisted arm temporarily adds::

    flavourized features -> frozen recurrent operator -> taste head -> food target

The tag head and flavourizer are shared. The auxiliary weight is annealed to zero,
and the entire recurrent/taste branch is skipped at held-out evaluation. A positive
therefore means "the substrate helped us learn the tagger", not "the substrate is
required to run the tagger".

Torch is imported lazily so the CPU-only experiment remains installable without it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .encoder_gate import average_precision


@dataclass(frozen=True)
class FlyAssistSpec:
    """Training geometry for fly-assisted distillation.

    ``rank`` intentionally keeps the final transformation weak: it is a residual
    low-rank map, not an attention model. ``assist_fraction`` says how much of
    training may use the fly. After that point lambda is exactly zero and the fly
    branch is not evaluated, forcing the standalone tagger to finish on its own.
    """

    rank: int = 32
    steps_per_chunk: int = 4
    leak: float = 0.4
    gain: float = 0.95
    target_drive_rms: float = 0.05
    assist_weight: float = 1.0
    assist_fraction: float = 0.7
    residual_penalty: float = 1e-4

    def assist_lambda(self, epoch: int, max_epochs: int) -> float:
        """Linearly anneal fly assistance to zero, then keep it off."""
        if max_epochs <= 0:
            raise ValueError("max_epochs must be positive")
        cutoff = max(1, int(np.ceil(max_epochs * self.assist_fraction)))
        if epoch >= cutoff:
            return 0.0
        if cutoff == 1:
            return 0.0
        return float(self.assist_weight * (1.0 - epoch / (cutoff - 1)))


def _torch():
    try:
        import torch
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "fly-assisted training needs PyTorch; install the experiment with the "
            "`train` extra"
        ) from error
    return torch


def make_model(input_dim: int, tag_count: int, taste_dim: int, spec: FlyAssistSpec):
    """Create the shared final tagger plus its disposable taste head.

    The up-projection starts at zero, so every arm begins as the identity
    transformation and differences cannot be blamed on a different initial
    semantic representation.
    """
    torch = _torch()
    nn = torch.nn

    class FlyAssistedTagger(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.down = nn.Linear(input_dim, spec.rank, bias=False)
            self.up = nn.Linear(spec.rank, input_dim, bias=False)
            self.tag_head = nn.Linear(input_dim, tag_count)
            self.taste_head = nn.Linear(taste_dim, taste_dim)
            nn.init.zeros_(self.up.weight)

        def transform(self, features):
            residual = self.up(torch.tanh(self.down(features)))
            return features + residual, residual

        def standalone_logits(self, features):
            transformed, residual = self.transform(features)
            return self.tag_head(transformed), residual

    return FlyAssistedTagger()


def unit_rows_torch(values):
    torch = _torch()
    return values / torch.linalg.vector_norm(values, dim=1, keepdim=True).clamp_min(1e-12)


def interpolate_torch(features, steps: int):
    """Differentiable counterpart of :func:`multitag.interpolate`."""
    torch = _torch()
    if steps < 1:
        raise ValueError("steps_per_chunk must be >= 1")
    if features.shape[0] <= 1 or steps == 1:
        return features
    pieces = [features[:1]]
    alpha = torch.linspace(
        1.0 / steps,
        1.0,
        steps,
        dtype=features.dtype,
        device=features.device,
    )[:, None]
    for index in range(1, features.shape[0]):
        pieces.append(features[index - 1] + alpha * (features[index] - features[index - 1]))
    return torch.cat(pieces, dim=0)


def semantic_reservoir_states(
    operator,
    transformed,
    *,
    input_weights,
    input_indices,
    readout_indices,
    spec: FlyAssistSpec,
):
    """Run a differentiable semantic trajectory through a frozen sparse operator.

    Drive RMS is matched *inside each training document* after the flavourizer.
    That matters here because a trainable upstream map could otherwise improve the
    auxiliary loss merely by increasing current. Normalising the semantic rows and
    re-scaling the realised projection makes the flavourizer change direction, not
    volume.

    Returns one readout state per original chunk plus the realised drive RMS.
    The sparse operator is a tensor/buffer, never a parameter.
    """
    torch = _torch()
    features = unit_rows_torch(transformed)
    path = interpolate_torch(features, spec.steps_per_chunk)
    projected = input_weights @ path.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (spec.target_drive_rms / rms)

    neurons = int(operator.shape[0])
    state = torch.zeros(neurons, dtype=transformed.dtype, device=transformed.device)
    outputs = []
    for step in range(path.shape[0]):
        drive = torch.zeros_like(state).index_add(0, input_indices, projected[:, step])
        pre = torch.sparse.mm(operator, state[:, None]).squeeze(1) * spec.gain + drive
        state = (1.0 - spec.leak) * state + spec.leak * torch.tanh(pre)
        # Path positions 0, steps, 2*steps, ... are the last state for each
        # original chunk. This mirrors the CPU Run-1 alignment exactly.
        if step == 0 or step % spec.steps_per_chunk == 0:
            outputs.append(state[readout_indices])

    stacked = torch.stack(outputs, dim=0)
    realised = torch.sqrt(torch.mean(projected.square()))
    return stacked, realised


def food_target_torch(tag_masks, flavours):
    """Training-only food target: overlap is a mixture of tag flavours."""
    return tag_masks @ flavours


def training_loss(
    model,
    features,
    tag_masks,
    *,
    spec: FlyAssistSpec,
    assist_lambda: float,
    operator=None,
    input_weights=None,
    input_indices=None,
    readout_indices=None,
    flavours=None,
):
    """Compute standalone tag loss plus optional fly-teacher loss.

    The returned main logits never depend on the reservoir branch. When
    ``assist_lambda == 0`` the branch is skipped entirely, which makes the final
    phase of training identical to deployment.
    """
    torch = _torch()
    transformed, residual = model.transform(features)
    logits = model.tag_head(transformed)
    tag_loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, tag_masks)
    residual_ratio = (
        torch.linalg.vector_norm(residual, dim=1)
        / torch.linalg.vector_norm(features, dim=1).clamp_min(1e-12)
    ).mean()
    total = tag_loss + spec.residual_penalty * residual_ratio.square()

    fly_loss = torch.zeros((), dtype=features.dtype, device=features.device)
    drive_rms = torch.zeros((), dtype=features.dtype, device=features.device)
    if assist_lambda > 0.0:
        required = {
            "operator": operator,
            "input_weights": input_weights,
            "input_indices": input_indices,
            "readout_indices": readout_indices,
            "flavours": flavours,
        }
        missing = [name for name, value in required.items() if value is None]
        if missing:
            raise ValueError(f"assisted loss missing: {', '.join(missing)}")
        states, drive_rms = semantic_reservoir_states(
            operator,
            transformed,
            input_weights=input_weights,
            input_indices=input_indices,
            readout_indices=readout_indices,
            spec=spec,
        )
        # A disposable linear map turns the chosen fly state into the same flavour
        # space used by the food target. The flavourizer receives this gradient
        # through the frozen recurrence; the taste head is thrown away later.
        if states.shape[1] != model.taste_head.in_features:
            raise ValueError(
                f"taste head expects {model.taste_head.in_features} fly features, "
                f"got {states.shape[1]}"
            )
        predicted_taste = model.taste_head(states)
        targets = food_target_torch(tag_masks, flavours)
        fly_loss = torch.nn.functional.mse_loss(predicted_taste, targets)
        total = total + float(assist_lambda) * fly_loss

    return {
        "loss": total,
        "tag_loss": tag_loss,
        "fly_loss": fly_loss,
        "residual_ratio": residual_ratio,
        "drive_rms": drive_rms,
        "logits": logits,
    }


def score_standalone(logits: np.ndarray, tag_masks: np.ndarray) -> dict:
    """Score only the deployable tagger; no fly-derived quantity enters here."""
    scores = 1.0 / (1.0 + np.exp(-np.asarray(logits, dtype=np.float64)))
    masks = np.asarray(tag_masks, dtype=np.float32)
    inside = masks.max(axis=1) > 0
    any_score = scores.max(axis=1)
    per_tag = []
    for index in range(masks.shape[1]):
        target = masks[:, index] > 0
        if target.any() and not target.all():
            per_tag.append(float(average_precision(scores[:, index], target)))
    if inside.any():
        truth = np.argmax(masks[inside], axis=1)
        predicted = np.argmax(scores[inside], axis=1)
        tag_accuracy = float(np.mean(predicted == truth))
    else:
        tag_accuracy = float("nan")
    return {
        "inside_auprc": float(average_precision(any_score, inside)),
        "macro_tag_auprc": float(np.mean(per_tag)) if per_tag else float("nan"),
        "tag_accuracy_on_true_spans": tag_accuracy,
    }


def protocol_dict(spec: FlyAssistSpec) -> dict:
    """Stable serialisable description for result JSONs."""
    return {
        "name": "fly-assisted-standalone-tagger",
        "inference_path": "semantic -> flavourizer -> tag_head (no fly, no food, no mask)",
        "training_auxiliary": "flavourizer -> frozen operator -> taste_head -> food target",
        "spec": asdict(spec),
        "claim_boundary": (
            "A positive means the training-time substrate improved the final standalone "
            "tagger. It does not mean the connectome is required at inference. A topology "
            "claim additionally requires MaleCNS assistance to beat tag-only, degree-null "
            "assistance and random-ESN assistance under the same final architecture."
        ),
    }
