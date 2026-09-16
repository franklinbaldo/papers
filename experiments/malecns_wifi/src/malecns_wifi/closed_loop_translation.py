"""Closed-loop embedding translation through a frozen recurrent substrate.

The trainable pieces are deliberately small and explicit::

    embedding A -> low-rank input adapter -> frozen recurrent operator
                -> fixed state projection -> low-rank output adapter -> B_hat
                -> supervised error features -> low-rank feedback adapter -> state

The recurrent operator and fixed projections are supplied by the caller and are never
registered as parameters.  That makes the claim boundary inspectable: gradients may
flow *through* MaleCNS, but MaleCNS itself is frozen.

The first protocol uses teacher feedback (the target B embedding is available while
training).  This is supervised recurrent correction, not autonomous inference.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranslationSpec:
    """Geometry and dynamics for the first closed-loop translation smoke."""

    rank: int = 16
    steps: int = 4
    leak: float = 0.4
    gain: float = 0.95
    target_drive_rms: float = 0.05
    feedback_scale: float = 1.0


def _torch():
    try:
        import torch
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "closed-loop translation needs PyTorch; install the experiment with the `train` extra"
        ) from error
    return torch


def _fast_sparse_mm(operator, values):
    """Use the cached-transpose path when available without requiring it."""
    try:
        from .fast_spmv import fast_sparse_mm
    except (ImportError, ModuleNotFoundError):  # pragma: no cover - stacked-branch fallback
        return _torch().sparse.mm(operator, values)
    return fast_sparse_mm(operator, values)


def unit_rows(values):
    torch = _torch()
    return values / torch.linalg.vector_norm(values, dim=-1, keepdim=True).clamp_min(1e-12)


class _LowRankAdapterMixin:
    """Marker mixin used only to make the architecture obvious in inspection."""


def make_low_rank_adapter(input_dim: int, output_dim: int, rank: int):
    """Return B(tanh(Ax)): an explicit trainable low-rank adapter, not full LoRA."""
    torch = _torch()
    nn = torch.nn

    if rank < 1:
        raise ValueError("rank must be positive")

    class LowRankAdapter(nn.Module, _LowRankAdapterMixin):
        def __init__(self) -> None:
            super().__init__()
            self.down = nn.Linear(input_dim, rank, bias=False)
            self.up = nn.Linear(rank, output_dim, bias=False)

        def forward(self, values):
            return self.up(torch.tanh(self.down(values)))

    return LowRankAdapter()


def make_translator(
    input_dim: int,
    target_dim: int,
    sensory_dim: int,
    readout_dim: int,
    spec: TranslationSpec = TranslationSpec(),
):
    """Create the three trainable interfaces around a frozen recurrent operator."""
    torch = _torch()
    nn = torch.nn

    # Feedback features are [prediction, target, error, cosine, ||error||].
    feedback_dim = 3 * target_dim + 2

    class ClosedLoopTranslator(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.adapter_in = make_low_rank_adapter(input_dim, sensory_dim, spec.rank)
            self.adapter_out = make_low_rank_adapter(readout_dim, target_dim, spec.rank)
            self.adapter_feedback = make_low_rank_adapter(feedback_dim, sensory_dim, spec.rank)

        def parameter_groups(self):
            """Expose the only three trainable components for smoke/provenance checks."""
            return {
                "adapter_in": tuple(self.adapter_in.parameters()),
                "adapter_out": tuple(self.adapter_out.parameters()),
                "adapter_feedback": tuple(self.adapter_feedback.parameters()),
            }

    return ClosedLoopTranslator()


def _project_state(state, readout_projection):
    torch = _torch()
    if readout_projection.layout == torch.strided:
        return state @ readout_projection.T
    # sparse projection is [readout_dim, neurons]; state is [batch, neurons]
    return torch.sparse.mm(readout_projection, state.T).T


def _scatter_drive(drive, input_indices, neurons: int):
    """Scatter [batch, sensory] drive into [batch, neurons]."""
    torch = _torch()
    batch = int(drive.shape[0])
    full = torch.zeros(batch, neurons, dtype=drive.dtype, device=drive.device)
    index = input_indices.to(device=drive.device)
    return full.index_add(1, index, drive)


def _match_drive_rms(drive, target_rms: float):
    torch = _torch()
    rms = torch.sqrt(torch.mean(drive.square())).clamp_min(1e-12)
    return drive * (float(target_rms) / rms), rms


def teacher_feedback_features(prediction, target):
    """Features for the explicitly supervised first phase."""
    torch = _torch()
    prediction = unit_rows(prediction)
    target = unit_rows(target)
    error = target - prediction
    cosine = torch.sum(prediction * target, dim=-1, keepdim=True)
    error_norm = torch.linalg.vector_norm(error, dim=-1, keepdim=True)
    return torch.cat([prediction, target, error, cosine, error_norm], dim=-1)


def closed_loop_forward(
    model,
    operator,
    source,
    *,
    target,
    input_indices,
    readout_projection,
    spec: TranslationSpec,
    feedback: bool = True,
    initial_state=None,
):
    """Translate A -> B while preserving one recurrent state across correction steps.

    ``target`` is intentionally required in this first-phase function because the
    feedback adapter consumes teacher error.  Set ``feedback=False`` for the matched
    MaleCNS open-loop arm; everything else remains identical.

    Returns the complete prediction trajectory so quality(t) and error contraction
    can be measured rather than hiding the dynamics behind the final step.
    """
    torch = _torch()

    if spec.steps < 1:
        raise ValueError("steps must be >= 1")
    if source.ndim != 2 or target.ndim != 2:
        raise ValueError("source and target must be [batch, dim]")
    if source.shape[0] != target.shape[0]:
        raise ValueError("source and target batch sizes differ")

    source = unit_rows(source)
    target = unit_rows(target)
    neurons = int(operator.shape[0])
    batch = int(source.shape[0])

    state = (
        torch.zeros(batch, neurons, dtype=source.dtype, device=source.device)
        if initial_state is None
        else initial_state
    )
    if state.shape != (batch, neurons):
        raise ValueError(f"initial_state must have shape {(batch, neurons)}, got {tuple(state.shape)}")

    base_drive = model.adapter_in(source)
    base_drive, raw_input_rms = _match_drive_rms(base_drive, spec.target_drive_rms)

    predictions = []
    states = []
    cosines = []
    error_norms = []
    feedback_norms = []
    feedback_drive = torch.zeros_like(base_drive)

    # t=0..T: expose the initial estimate after one recurrent update, then T
    # correction rounds.  This yields T+1 predictions for a configured T.
    for step in range(spec.steps + 1):
        combined_drive = base_drive + float(spec.feedback_scale) * feedback_drive
        full_drive = _scatter_drive(combined_drive, input_indices, neurons)
        recurrent = _fast_sparse_mm(operator, state.T).T
        pre = float(spec.gain) * recurrent + full_drive
        state = (1.0 - float(spec.leak)) * state + float(spec.leak) * torch.tanh(pre)

        readout = _project_state(state, readout_projection)
        prediction = unit_rows(model.adapter_out(readout))
        error = target - prediction
        cosine = torch.sum(prediction * target, dim=-1)
        error_norm = torch.linalg.vector_norm(error, dim=-1)

        predictions.append(prediction)
        states.append(state)
        cosines.append(cosine)
        error_norms.append(error_norm)

        if step == spec.steps:
            break

        if feedback:
            features = teacher_feedback_features(prediction, target)
            feedback_drive = model.adapter_feedback(features)
            feedback_drive, _ = _match_drive_rms(feedback_drive, spec.target_drive_rms)
        else:
            feedback_drive = torch.zeros_like(base_drive)
        feedback_norms.append(torch.linalg.vector_norm(feedback_drive, dim=-1))

    cosine_path = torch.stack(cosines, dim=1)
    error_path = torch.stack(error_norms, dim=1)
    contraction = error_path[:, 1:] / error_path[:, :-1].clamp_min(1e-12)

    return {
        "prediction_path": torch.stack(predictions, dim=1),
        "state_path": torch.stack(states, dim=1),
        "cosine_path": cosine_path,
        "error_norm_path": error_path,
        "error_contraction": contraction,
        "feedback_norm_path": (
            torch.stack(feedback_norms, dim=1)
            if feedback_norms
            else torch.empty(batch, 0, dtype=source.dtype, device=source.device)
        ),
        "raw_input_rms": raw_input_rms,
        "final_prediction": predictions[-1],
        "final_state": state,
    }


def translation_loss(result, target):
    """Cosine + small MSE objective used by the engineering smoke."""
    torch = _torch()
    target = unit_rows(target)
    prediction = result["final_prediction"]
    cosine_loss = 1.0 - torch.sum(prediction * target, dim=-1).mean()
    mse = torch.nn.functional.mse_loss(prediction, target)
    return cosine_loss + 0.1 * mse


def make_direct_low_rank(input_dim: int, target_dim: int, rank: int = 16):
    """Required no-connectome baseline: A -> low-rank adapter -> B."""
    return make_low_rank_adapter(input_dim, target_dim, rank)
