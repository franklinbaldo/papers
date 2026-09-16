"""Closed-loop representation translation through a frozen MaleCNS operator.

The question is not whether a fly "knows" embeddings. It is whether a large fixed
recurrent dynamical substrate, wrapped in small trainable interfaces and run in a
closed loop, supplies useful computation to an external task::

    embedding A -> adapter_in -> [ frozen substrate h_t ] -> adapter_out -> embedding B_hat_t
                                        ^                                        |
                                        |                                        v
                                   adapter_feedback <------------- error / consequence

Three things in this module are load-bearing and are kept explicit rather than
buried in a training script.

**The substrate is frozen.** The recurrent operator is a buffer, never a
parameter, and :class:`FrozenSpMM` propagates gradient through it by multiplying
with the precomputed transpose. The operator therefore has no ``.grad`` path at
all: no optimiser can touch it even by accident, and the backward pass costs one
extra sparse product instead of materialising a dense 165k x 165k Jacobian.

**The state persists across rounds.** ``h`` is reset once per example, never
between the rounds of one example. A round that resets the state is open-loop
computation dressed up as a loop, and is not what this file implements.

**The feedback channel is budgeted.** ``FeedbackMode`` decides what the loop is
allowed to see about its own error. ``FULL`` hands the loop the target vector,
which makes the arm a supervised recurrent *correction*, not autonomous
inference: a sufficiently expressive feedback adapter could route the target
around the substrate entirely. ``SCALAR`` hands it only the cosine, the error
norm and the round index -- two scalars that cannot reconstruct a 768-dimensional
target. Progress under ``SCALAR`` is progress the loop had to compute.

Nothing here is a claim about fly neuroanatomy. The input and feedback ports are
synthetic interfaces: fixed random projections onto neuron populations selected
by annotation. The connectome supplies the recurrent topology and the synaptic
weight multiset. The temporal dynamics -- leak, gain, tanh, drive normalisation --
are modelling choices made here, and MaleCNS ``connectome-weights`` are measured
connection strengths, not trained network weights.

Torch is imported lazily so the CPU-only parts of this experiment stay
installable without it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum

import numpy as np
import scipy.sparse as sp


def _torch():
    try:
        import torch
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "closed-loop translation needs PyTorch; install the experiment with the "
            "`train` extra"
        ) from error
    return torch


class FeedbackMode(str, Enum):
    """What the loop may observe about its own error.

    The distinction is the whole experiment, not a hyperparameter.

    ``NONE``
        Open loop. The substrate never sees a consequence of its own output.
    ``SCALAR``
        Cosine to target, error norm, round index. Three numbers. The target is
        not recoverable from them, so any improvement across rounds is computed
        by the loop rather than copied into it.
    ``RESIDUAL``
        The raw error vector ``b_target - b_hat``. Recoverable in principle
        (``b_target = b_hat + e``), so this is an oracle-grade channel.
    ``FULL``
        Prediction, target, error and the scalars. Maximal teacher signal, and
        the most leak-prone arm. Report it as an upper bound, never as inference.
    """

    NONE = "none"
    SCALAR = "scalar"
    RESIDUAL = "residual"
    FULL = "full"

    def feature_dim(self, target_dim: int) -> int:
        if self is FeedbackMode.NONE:
            return 0
        if self is FeedbackMode.SCALAR:
            return 3
        if self is FeedbackMode.RESIDUAL:
            return target_dim + 3
        return 3 * target_dim + 3

    @property
    def can_reconstruct_target(self) -> bool:
        """True when the channel is wide enough to carry the target itself."""
        return self in (FeedbackMode.RESIDUAL, FeedbackMode.FULL)


@dataclass(frozen=True)
class TranslationSpec:
    """Geometry of one closed-loop translation run.

    ``rank`` keeps every trainable interface small on purpose. The hypothesis is
    that the *substrate* supplies the computation; a wide adapter would make the
    result uninterpretable because the adapter could do the translation alone.

    ``rounds`` is the closed-loop depth T. ``inner_steps`` is how many recurrent
    updates happen inside one round before the state is read out, so the
    recurrent depth of a run is ``rounds * inner_steps``.
    """

    rank: int = 16
    rounds: int = 4
    inner_steps: int = 2
    drive_dim: int = 128
    readout_width: int = 512
    leak: float = 0.4
    gain: float = 0.95
    target_drive_rms: float = 0.05
    feedback_drive_rms: float = 0.05
    feedback_mode: FeedbackMode = FeedbackMode.SCALAR
    input_persistence: str = "every_round"
    round_loss_weighting: str = "linear"
    adapter_nonlinearity: str = "tanh"
    objective: str = "infonce"
    temperature: float = 0.05

    def __post_init__(self) -> None:
        if self.rounds < 1:
            raise ValueError("rounds must be >= 1")
        if self.inner_steps < 1:
            raise ValueError("inner_steps must be >= 1")
        if not 0.0 < self.leak <= 1.0:
            raise ValueError("leak must be in (0, 1]")
        if self.input_persistence not in ("every_round", "first_only"):
            raise ValueError("input_persistence must be 'every_round' or 'first_only'")
        if self.round_loss_weighting not in ("linear", "uniform", "final"):
            raise ValueError("round_loss_weighting must be linear, uniform or final")
        if self.objective not in ("infonce", "cosine"):
            raise ValueError("objective must be 'infonce' or 'cosine'")
        if self.temperature <= 0.0:
            raise ValueError("temperature must be positive")

    def round_weights(self) -> np.ndarray:
        """Per-round loss weights, normalised to sum to one.

        ``linear`` supervises every round but leans on the later ones, which is
        what makes the trajectory ``quality(t)`` interpretable: the loop is asked
        to *improve*, not merely to be right once.
        """
        if self.round_loss_weighting == "uniform":
            weights = np.ones(self.rounds, dtype=np.float64)
        elif self.round_loss_weighting == "final":
            weights = np.zeros(self.rounds, dtype=np.float64)
            weights[-1] = 1.0
        else:
            weights = np.arange(1, self.rounds + 1, dtype=np.float64)
        return weights / weights.sum()


# --- frozen sparse recurrence ----------------------------------------------


class FrozenSpMM:
    """``W @ x`` with gradient only for ``x``, using a precomputed ``W.T``.

    Built lazily because it has to subclass ``torch.autograd.Function``.
    """

    _impl = None

    @classmethod
    def impl(cls):
        if cls._impl is None:
            torch = _torch()

            class _FrozenSpMM(torch.autograd.Function):
                @staticmethod
                def forward(ctx, dense, operator, operator_t):
                    ctx.operator_t = operator_t
                    return torch.sparse.mm(operator, dense)

                @staticmethod
                def backward(ctx, grad_output):
                    grad = torch.sparse.mm(ctx.operator_t, grad_output.contiguous())
                    return grad, None, None

            cls._impl = _FrozenSpMM
        return cls._impl

    @classmethod
    def apply(cls, dense, operator, operator_t):
        return cls.impl().apply(dense, operator, operator_t)


def csr_to_torch(matrix: sp.csr_matrix, *, device):
    torch = _torch()
    matrix = sp.csr_matrix(matrix).astype(np.float32)
    return torch.sparse_csr_tensor(
        torch.as_tensor(matrix.indptr, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.indices, dtype=torch.int64, device=device),
        torch.as_tensor(matrix.data, dtype=torch.float32, device=device),
        size=matrix.shape,
        device=device,
    )


def fixed_sparse_projection(rows: int, cols: int, *, seed: int, device):
    """Fixed sparse sign projection, the same construction Run 1/2 already use."""
    torch = _torch()
    rng = np.random.default_rng(seed)
    per_row = max(1, int(round(np.sqrt(cols))))
    row = np.repeat(np.arange(rows, dtype=np.int64), per_row)
    col = np.concatenate(
        [rng.choice(cols, size=per_row, replace=False).astype(np.int64) for _ in range(rows)]
    )
    sign = rng.choice([-1.0, 1.0], size=len(row)).astype(np.float32)
    value = sign / np.float32(np.sqrt(per_row))
    indices = torch.as_tensor(np.vstack([row, col]), dtype=torch.int64, device=device)
    values = torch.as_tensor(value, dtype=torch.float32, device=device)
    return torch.sparse_coo_tensor(indices, values, (rows, cols), device=device).coalesce()


@dataclass
class Substrate:
    """A frozen recurrent operator plus its fixed, untrained interfaces.

    Everything in here is either measured (the connectome) or fixed
    infrastructure (random ports and readout). No field is optimised. Swapping
    ``operator`` for a degree-preserving null or a random ESN, with every other
    field byte-identical, is exactly the control this experiment needs.
    """

    name: str
    operator: object
    operator_t: object
    input_indices: object
    input_weights: object
    feedback_indices: object
    feedback_weights: object
    readout_projection: object
    neurons: int
    edges: int
    gain: float = 1.0
    gain_report: dict = field(default_factory=dict)
    stats: dict = field(default_factory=dict)

    def describe(self) -> dict:
        return {
            "name": self.name,
            "neurons": int(self.neurons),
            "edges": int(self.edges),
            "input_port_neurons": int(self.input_indices.shape[0]),
            "feedback_port_neurons": int(self.feedback_indices.shape[0]),
            "readout_width": int(self.readout_projection.shape[0]),
            "effective_gain": float(self.gain),
            "gain_calibration": self.gain_report,
            "trainable_parameters_in_substrate": 0,
            "stats": self.stats,
        }


def bulk_gain(matrix: sp.csr_matrix, *, seed: int = 0, probes: int = 3) -> float:
    """Mean ``||Wv|| / ||v||`` on random unit vectors: what the bulk state feels.

    Not the spectral radius, which is what the single slowest mode feels. On a
    spectrally concentrated operator like MaleCNS the two differ by more than an
    order of magnitude, and the bulk is what does the computing.
    """
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(probes):
        vector = rng.normal(size=matrix.shape[0]).astype(np.float32)
        vector /= np.linalg.norm(vector)
        values.append(float(np.linalg.norm(matrix @ vector)))
    return float(np.mean(values))


def build_substrate(
    matrix: sp.csr_matrix,
    *,
    name: str,
    spec: TranslationSpec,
    input_indices: np.ndarray,
    feedback_indices: np.ndarray,
    seed: int,
    device,
    stats: dict | None = None,
    gain_mode: str = "matched_bulk",
    bulk_target: float = 0.9,
) -> Substrate:
    """Wrap a sparse operator in fixed input, feedback and readout interfaces.

    ``input_indices`` and ``feedback_indices`` must be disjoint. A shared port
    would let the loop's own feedback overwrite its sensory drive, which would
    confound "the loop helped" with "the input was suppressed".

    ``gain_mode="matched_bulk"`` rescales the gain so that every operator runs at
    the same bulk operating point ``bulk_target``. This matters more than it
    looks: MaleCNS, a degree-preserving null and a random ESN have different bulk
    gains, so a fixed scalar gain would put them in different dynamical regimes
    and an arm difference would report *dynamic range*, not topology. Matching the
    operating point makes topology the only thing left varying.
    """
    torch = _torch()
    matrix = sp.csr_matrix(matrix).astype(np.float32)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    neurons = int(matrix.shape[0])
    input_indices = np.asarray(input_indices, dtype=np.int64).reshape(-1)
    feedback_indices = np.asarray(feedback_indices, dtype=np.int64).reshape(-1)
    if np.intersect1d(input_indices, feedback_indices).size:
        raise ValueError("input and feedback ports must be disjoint neuron populations")
    for population, label in ((input_indices, "input"), (feedback_indices, "feedback")):
        if population.size == 0:
            raise ValueError(f"{label} port is empty")
        if population.min() < 0 or population.max() >= neurons:
            raise ValueError(f"{label} port index outside the operator")

    measured = bulk_gain(matrix, seed=seed)
    if gain_mode == "matched_bulk":
        effective_gain = float(bulk_target / max(measured, 1e-6))
    elif gain_mode == "fixed":
        effective_gain = float(spec.gain)
    else:
        raise ValueError("gain_mode must be 'matched_bulk' or 'fixed'")
    gain_report = {
        "mode": gain_mode,
        "measured_bulk_gain": measured,
        "bulk_target": float(bulk_target) if gain_mode == "matched_bulk" else None,
        "effective_gain": effective_gain,
        "realised_bulk_operating_point": effective_gain * measured,
    }

    rng = np.random.default_rng(seed)
    operator = csr_to_torch(matrix, device=device)
    operator_t = csr_to_torch(sp.csr_matrix(matrix.T), device=device)

    def port_weights(size: int) -> object:
        values = rng.normal(size=(size, spec.drive_dim)).astype(np.float32)
        values /= np.float32(np.sqrt(spec.drive_dim))
        return torch.as_tensor(values, dtype=torch.float32, device=device)

    return Substrate(
        name=name,
        operator=operator,
        operator_t=operator_t,
        input_indices=torch.as_tensor(input_indices, dtype=torch.int64, device=device),
        input_weights=port_weights(input_indices.size),
        feedback_indices=torch.as_tensor(feedback_indices, dtype=torch.int64, device=device),
        feedback_weights=port_weights(feedback_indices.size),
        readout_projection=fixed_sparse_projection(
            spec.readout_width, neurons, seed=seed + 17, device=device
        ),
        neurons=neurons,
        edges=int(matrix.nnz),
        gain=effective_gain,
        gain_report=gain_report,
        stats=dict(stats or {}),
    )


def select_ports(
    superclass: np.ndarray,
    *,
    neurons: int,
    seed: int,
    input_selector: tuple[str, ...] = ("cb_sensory", "ol_sensory"),
    feedback_size: int | None = None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Annotation-selected sensory input port, plus a synthetic feedback port.

    The input port reuses the anatomical selection the tagging runs already use.
    The feedback port is drawn uniformly at random from the remaining neurons and
    is labelled synthetic: the fly has no "your embedding was wrong" afferent, and
    pretending otherwise would be inventing neurobiology to justify an interface.
    """
    superclass = np.asarray(superclass)
    inputs = np.flatnonzero(np.isin(superclass, input_selector))
    if inputs.size == 0:
        raise ValueError(
            f"empty input port for {input_selector!r}; available superclasses include "
            f"{sorted(set(superclass.tolist()))[:10]}"
        )
    size = int(feedback_size if feedback_size is not None else inputs.size)
    remaining = np.setdiff1d(np.arange(neurons, dtype=np.int64), inputs, assume_unique=False)
    if size > remaining.size:
        raise ValueError("feedback port larger than the non-sensory population")
    rng = np.random.default_rng(seed)
    feedback = np.sort(rng.choice(remaining, size=size, replace=False))
    report = {
        "input_selector": list(input_selector),
        "input_port_neurons": int(inputs.size),
        "feedback_port_neurons": int(feedback.size),
        "feedback_port_kind": "synthetic: uniform random non-sensory neurons",
        "feedback_port_note": (
            "There is no biological error afferent being modelled here. The port is a "
            "synthetic interface for delivering a consequence signal to the substrate."
        ),
    }
    return inputs, feedback, report


# --- trainable interfaces ---------------------------------------------------


def make_low_rank_adapter(
    in_dim: int,
    out_dim: int,
    *,
    rank: int,
    nonlinearity: str = "tanh",
    base: object | None = None,
    alpha: float | None = None,
):
    """``B(phi(A x))``, optionally as a LoRA residual on a frozen base map.

    Without ``base`` this is a trainable low-rank adapter and is named that way.
    It becomes LoRA only when a frozen ``W0`` is present and the module learns
    ``W = W0 + (alpha / r) B A``; calling every small module "LoRA" would make the
    word mean nothing.
    """
    torch = _torch()
    nn = torch.nn

    activations = {
        "tanh": torch.tanh,
        "none": lambda value: value,
        "gelu": torch.nn.functional.gelu,
    }
    if nonlinearity not in activations:
        raise ValueError(f"unknown adapter nonlinearity: {nonlinearity}")
    activation = activations[nonlinearity]
    scaling = float(alpha if alpha is not None else rank) / float(rank)

    class LowRankAdapter(nn.Module):
        is_lora = base is not None

        def __init__(self) -> None:
            super().__init__()
            self.down = nn.Linear(in_dim, rank, bias=False)
            self.up = nn.Linear(rank, out_dim, bias=False)
            self.bias = nn.Parameter(torch.zeros(out_dim))
            if base is not None:
                if tuple(base.shape) != (out_dim, in_dim):
                    raise ValueError(
                        f"frozen base must be [{out_dim}, {in_dim}], got {tuple(base.shape)}"
                    )
                self.register_buffer("base", base.detach().clone())
                # LoRA convention: the residual starts at exactly zero, so the
                # module begins life as the frozen base map.
                nn.init.zeros_(self.up.weight)
            else:
                self.base = None

        def forward(self, values):
            residual = self.up(activation(self.down(values)))
            if self.base is None:
                return residual + self.bias
            return values @ self.base.T + scaling * residual + self.bias

        def describe(self) -> dict:
            return {
                "kind": "lora" if self.base is not None else "trainable_low_rank_adapter",
                "in_dim": in_dim,
                "out_dim": out_dim,
                "rank": rank,
                "nonlinearity": nonlinearity,
                "lora_scaling": scaling if self.base is not None else None,
                "parameters": sum(p.numel() for p in self.parameters() if p.requires_grad),
            }

    return LowRankAdapter()


def make_mlp(in_dim: int, out_dim: int, *, hidden: int):
    torch = _torch()
    nn = torch.nn

    class TranslationMLP(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(in_dim, hidden),
                nn.GELU(),
                nn.Linear(hidden, out_dim),
            )

        def forward(self, values):
            return self.net(values)

        def describe(self) -> dict:
            return {
                "kind": "mlp",
                "in_dim": in_dim,
                "out_dim": out_dim,
                "hidden": hidden,
                "parameters": sum(p.numel() for p in self.parameters() if p.requires_grad),
            }

    return TranslationMLP()


def unit_rows(values):
    torch = _torch()
    return values / torch.linalg.vector_norm(values, dim=-1, keepdim=True).clamp_min(1e-12)


def feedback_features(b_hat, b_target, round_index: int, rounds: int, mode: FeedbackMode):
    """Assemble what the loop is allowed to know about its own error.

    ``b_hat`` and ``b_target`` are unit rows, so ``cosine`` is their dot product
    and ``error_norm`` is in ``[0, 2]``. The round index is included because a
    controller that knows how much time is left can behave differently early and
    late; withholding it would make the loop solve a harder problem than the one
    being asked about.
    """
    torch = _torch()
    if mode is FeedbackMode.NONE:
        raise ValueError("FeedbackMode.NONE has no feedback features")
    error = b_target - b_hat
    cosine = (b_hat * b_target).sum(dim=-1, keepdim=True)
    error_norm = torch.linalg.vector_norm(error, dim=-1, keepdim=True)
    phase = torch.full_like(cosine, float(round_index) / float(max(rounds - 1, 1)))
    scalars = [cosine, error_norm, phase]
    if mode is FeedbackMode.SCALAR:
        return torch.cat(scalars, dim=-1)
    if mode is FeedbackMode.RESIDUAL:
        return torch.cat([error, *scalars], dim=-1)
    return torch.cat([b_hat, b_target, error, *scalars], dim=-1)


def make_translator(source_dim: int, target_dim: int, spec: TranslationSpec, *, device):
    """The three trainable interfaces around a frozen substrate.

    ``adapter_out`` is a proper LoRA: it learns a low-rank residual on a frozen
    random readout map, so the arm starts from a fixed, untrained decoding of the
    state and has to *earn* any departure from it.
    """
    torch = _torch()
    nn = torch.nn

    generator = torch.Generator(device="cpu").manual_seed(20260916)
    base = torch.randn(
        target_dim, spec.readout_width, generator=generator
    ) / float(np.sqrt(spec.readout_width))
    base = base.to(device)
    feature_dim = spec.feedback_mode.feature_dim(target_dim)

    class ClosedLoopTranslator(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.adapter_in = make_low_rank_adapter(
                source_dim, spec.drive_dim, rank=spec.rank,
                nonlinearity=spec.adapter_nonlinearity,
            )
            self.adapter_out = make_low_rank_adapter(
                spec.readout_width, target_dim, rank=spec.rank,
                nonlinearity=spec.adapter_nonlinearity, base=base,
            )
            self.adapter_feedback = (
                None
                if spec.feedback_mode is FeedbackMode.NONE
                else make_low_rank_adapter(
                    feature_dim, spec.drive_dim, rank=spec.rank,
                    nonlinearity=spec.adapter_nonlinearity,
                )
            )

        def describe(self) -> dict:
            report = {
                "adapter_in": self.adapter_in.describe(),
                "adapter_out": self.adapter_out.describe(),
                "adapter_feedback": (
                    None if self.adapter_feedback is None else self.adapter_feedback.describe()
                ),
                "feedback_mode": spec.feedback_mode.value,
                "feedback_can_reconstruct_target": spec.feedback_mode.can_reconstruct_target,
            }
            report["trainable_parameters"] = sum(
                p.numel() for p in self.parameters() if p.requires_grad
            )
            return report

    return ClosedLoopTranslator().to(device)


def _scatter_drive(state, indices, port_weights, code, target_rms: float):
    """Project a drive code onto a neuron port with its RMS matched.

    Matching the RMS *after* the adapter is what stops a trainable upstream map
    from winning by shouting: it can change the direction and geometry of the
    current it injects, never its magnitude.
    """
    torch = _torch()
    projected = port_weights @ code.T
    rms = torch.sqrt(torch.mean(projected.square())).clamp_min(1e-12)
    projected = projected * (target_rms / rms)
    drive = torch.zeros_like(state).index_add(0, indices, projected)
    return drive, rms


def run_loop(model, substrate: Substrate, source, target, spec: TranslationSpec):
    """One closed-loop translation for a batch of examples.

    Returns the per-round predictions and the diagnostics that make the claim
    checkable: the state is created once here and is never reset between rounds,
    and the feedback drive magnitude is reported per round so an arm that silently
    stops using the loop is visible in the record rather than only in the score.
    """
    torch = _torch()
    source = unit_rows(source)
    target = unit_rows(target)
    batch = source.shape[0]

    state = torch.zeros(
        substrate.neurons, batch, dtype=source.dtype, device=source.device
    )
    input_code = model.adapter_in(source)
    input_drive, input_rms = _scatter_drive(
        state, substrate.input_indices, substrate.input_weights, input_code,
        spec.target_drive_rms,
    )

    predictions = []
    diagnostics = []
    feedback_drive = torch.zeros_like(state)
    feedback_rms = torch.zeros((), dtype=source.dtype, device=source.device)

    for round_index in range(spec.rounds):
        drive = feedback_drive
        if spec.input_persistence == "every_round" or round_index == 0:
            drive = drive + input_drive
        for _ in range(spec.inner_steps):
            recurrent = FrozenSpMM.apply(state, substrate.operator, substrate.operator_t)
            pre = recurrent * substrate.gain + drive
            state = (1.0 - spec.leak) * state + spec.leak * torch.tanh(pre)

        readout = torch.sparse.mm(substrate.readout_projection, state).T
        prediction = unit_rows(model.adapter_out(readout))
        predictions.append(prediction)

        diagnostics.append({
            "round": round_index,
            "state_rms": float(torch.sqrt(state.detach().square().mean()).cpu()),
            "state_saturation": float(
                (state.detach().abs() > 0.99).float().mean().cpu()
            ),
            "recurrent_to_drive_norm_ratio": float(
                (recurrent.detach() * substrate.gain).norm().cpu()
                / max(float(drive.detach().norm().cpu()), 1e-9)
            ),
            "feedback_code_rms_prescale": float(feedback_rms.detach().cpu())
            if torch.is_tensor(feedback_rms) else 0.0,
            "input_code_rms_prescale": float(input_rms.detach().cpu()),
            "realised_feedback_drive_rms": 0.0 if round_index == 0 else spec.feedback_drive_rms,
        })

        if spec.feedback_mode is FeedbackMode.NONE or round_index == spec.rounds - 1:
            continue
        features = feedback_features(
            prediction, target, round_index, spec.rounds, spec.feedback_mode
        )
        code = model.adapter_feedback(features)
        feedback_drive, feedback_rms = _scatter_drive(
            state, substrate.feedback_indices, substrate.feedback_weights, code,
            spec.feedback_drive_rms,
        )

    return predictions, diagnostics


def round_loss(predictions, target, spec: TranslationSpec):
    """Weighted loss over the whole trajectory, not only its endpoint.

    The default objective is InfoNCE with in-batch negatives, and that choice is
    forced by the geometry rather than by fashion. E5 space is strongly
    anisotropic: the mean cosine between two unrelated E5 vectors is about 0.67,
    and a model that emits the target centroid for every input scores a *higher*
    mean cosine than any real translation while retrieving nothing. Training on
    plain cosine walks straight into that collapse. A contrastive loss has to tell
    the targets apart, so it optimises the thing the task is actually about.

    ``objective="cosine"`` is kept for ablation, not because it is a reasonable
    default.
    """
    torch = _torch()
    target = unit_rows(target)
    weights = spec.round_weights()
    total = torch.zeros((), dtype=target.dtype, device=target.device)
    per_round = []
    for index, prediction in enumerate(predictions):
        if spec.objective == "cosine":
            loss = (1.0 - (prediction * target).sum(dim=-1)).mean()
        else:
            logits = (prediction @ target.T) / spec.temperature
            labels = torch.arange(logits.shape[0], device=logits.device)
            loss = torch.nn.functional.cross_entropy(logits, labels)
        per_round.append(loss)
        total = total + float(weights[index]) * loss
    return total, per_round


def protocol_dict(spec: TranslationSpec) -> dict:
    """Stable, serialisable statement of what a run does and does not claim."""
    payload = asdict(spec)
    payload["feedback_mode"] = spec.feedback_mode.value
    return {
        "name": "closed-loop-embedding-translation",
        "architecture": (
            "embedding_A -> adapter_in -> frozen substrate h_t -> fixed readout -> "
            "adapter_out -> embedding_B_hat_t -> error -> adapter_feedback -> same h_t"
        ),
        "spec": payload,
        "recurrent_depth": spec.rounds * spec.inner_steps,
        "frozen": [
            "substrate operator (connectome or null)",
            "input port weights",
            "feedback port weights",
            "readout projection",
            "adapter_out frozen LoRA base",
            "source and target sentence encoders",
        ],
        "trainable": ["adapter_in", "adapter_out residual", "adapter_feedback"],
        "claim_boundary": (
            "A closed-loop arm with a target-carrying feedback mode (residual/full) is "
            "supervised recurrent correction, not autonomous inference: the target is "
            "available at read time. Only the scalar mode is target-free. A MaleCNS-specific "
            "claim additionally requires the connectome arm to beat the degree-preserving "
            "null, the random ESN, the open-loop arm and the direct baselines under an "
            "identical interface budget and identical embeddings."
        ),
        "weights_disambiguation": (
            "MaleCNS connectome-weights are measured synaptic connection strengths from the "
            "v1.0 release, not trained artificial-neural-network weights. Leak, gain, tanh "
            "and drive normalisation are modelling choices made in this module."
        ),
    }
