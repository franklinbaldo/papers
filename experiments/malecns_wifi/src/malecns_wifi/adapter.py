"""Trainable input/output adapter around a frozen connectome reservoir.

The FLM design with this repository's controls: the recurrent weights never move,
an adapter learns the interface on both sides, and the run that proves anything is
the one where the same adapter, at the same size, is also wired straight from
input to output with no fly in between.

Gradients flow through the frozen sparse recurrence but not across the whole
document. Backpropagating through a 10M-edge product for thousands of bytes does
not fit in memory, so this uses truncated BPTT: the graph is cut at each window
boundary while the *state* carries across detached. The state sees the whole
document; the gradient sees one window.

Torch is imported lazily so the rest of the package stays importable without it.
There is no CUDA-free path worth running: a training pass is roughly 3x the
forward cost and belongs on a GPU.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

import numpy as np
import scipy.sparse as sp

from .tagger import CLASSES, Document, Populations, encode, macro_f1


@dataclass(frozen=True)
class AdapterSpec:
    """Adapter shape and the truncated-BPTT budget.

    ``input_neurons`` subsamples the sensory populations. Projecting 64 dimensions
    into all 8,982 sensory neurons alone costs 575k parameters; 4,096 lands the
    whole adapter near 300k -- the FLM scale, big enough to find the interface and
    small enough not to do the task by itself.

    ``batch_size`` and ``window`` are jointly a memory budget, not a taste. A
    truncated window stores one 165k-by-batch state per byte: 64 documents over
    512 bytes is about 21 GB of activations, which no accelerator here will hold.
    8 documents over 256 bytes is about 1.4 GB.
    """

    embedding_dim: int = 64
    input_neurons: int = 4096
    batch_size: int = 8
    window: int = 256
    leak: float = 0.4
    gain: float = 0.95
    max_bytes: int = 0
    seed: int = 0

    def activation_gigabytes(self, neurons: int) -> float:
        return self.window * neurons * self.batch_size * 4 / 2**30


@dataclass(frozen=True)
class TrainSpec:
    """Training protocol: the v2 schedule, on a validation split worth selecting on."""

    max_epochs: int = 30
    min_epochs: int = 5
    patience: int = 5
    learning_rate: float = 1e-3
    weight_decay: float = 0.0
    seeds: tuple[int, ...] = tuple(range(10))
    adapter: AdapterSpec = field(default_factory=AdapterSpec)


def _torch():
    try:
        import torch
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "training the adapter needs PyTorch and a GPU; the ridge readout in "
            "malecns_wifi.tagger runs on CPU and needs neither"
        ) from error
    return torch


def to_sparse(matrix: sp.csr_matrix, device: str = "cpu"):
    """Frozen recurrent operator as a torch CSR tensor, never a parameter."""
    torch = _torch()
    return torch.sparse_csr_tensor(
        torch.from_numpy(matrix.indptr.astype(np.int64)),
        torch.from_numpy(matrix.indices.astype(np.int64)),
        torch.from_numpy(matrix.data.astype(np.float32)),
        size=matrix.shape,
        device=device,
    )


def make_models(populations: Populations, spec: AdapterSpec, classes: int = len(CLASSES)):
    """The reservoir adapter and its direct-input control, matched in parameters."""
    torch = _torch()
    nn = torch.nn

    rng = np.random.default_rng(spec.seed)
    available = populations.input_indices
    chosen = (
        np.sort(rng.choice(available, size=spec.input_neurons, replace=False))
        if 0 < spec.input_neurons < available.size
        else available
    )
    readout_size = int(populations.readout_indices.size)

    class ReservoirAdapter(nn.Module):
        """Byte embedding -> sensory projection -> frozen recurrence -> descending readout."""

        def __init__(self) -> None:
            super().__init__()
            self.embedding = nn.Embedding(256, spec.embedding_dim)
            self.project = nn.Linear(spec.embedding_dim, chosen.size, bias=False)
            self.readout = nn.Linear(2 * readout_size, classes)
            self.register_buffer("inputs", torch.from_numpy(chosen.astype(np.int64)))
            self.register_buffer(
                "outputs", torch.from_numpy(populations.readout_indices.astype(np.int64))
            )

        def drive(self, byte_step):
            """Input current for one byte, scattered onto the sensory rows."""
            return self.project(self.embedding(byte_step)).T

    class DirectControl(nn.Module):
        """The same adapter with no fly in between.

        Same embedding, same width, same pooling, no recurrence. If this matches
        the reservoir conditions then the adapter did the task and the topology is
        decoration, which is why it is a required control rather than a nicety.
        """

        def __init__(self) -> None:
            super().__init__()
            self.embedding = nn.Embedding(256, spec.embedding_dim)
            self.project = nn.Linear(spec.embedding_dim, chosen.size, bias=False)
            self.readout = nn.Linear(2 * readout_size, classes)
            self.register_buffer(
                "probe",
                torch.from_numpy(
                    np.sort(rng.choice(chosen.size, size=readout_size, replace=False)).astype(
                        np.int64
                    )
                ),
            )

        def forward(self, bytes_batch, lengths):
            hidden = torch.tanh(self.project(self.embedding(bytes_batch)))
            steps = torch.arange(bytes_batch.shape[1], device=bytes_batch.device)
            mask = (steps[None, :] < lengths[:, None]).to(hidden.dtype)
            probed = hidden[:, :, self.probe]
            mean = (probed * mask[:, :, None]).sum(dim=1) / lengths[:, None].clamp(min=1)
            final = probed[torch.arange(probed.shape[0]), (lengths - 1).clamp(min=0)]
            return self.readout(torch.cat([final, mean], dim=1))

    return ReservoirAdapter(), DirectControl(), chosen


def reservoir_forward(model, operator, bytes_batch, lengths, spec: AdapterSpec):
    """Truncated-BPTT forward pass returning class logits.

    The graph is cut at every ``window`` boundary and the state detached, so memory
    costs one window of activations rather than one document. A document that has
    ended stops updating, so its final state is the state at its own last byte.
    """
    torch = _torch()
    device = bytes_batch.device
    count, width = bytes_batch.shape
    neurons = operator.shape[0]

    state = torch.zeros(neurons, count, device=device)
    accumulated = torch.zeros(model.outputs.numel(), count, device=device)
    final = torch.zeros(model.outputs.numel(), count, device=device)

    for step in range(width):
        if step and step % spec.window == 0:
            state = state.detach()
            accumulated = accumulated.detach()
        active = (lengths > step).to(state.dtype)
        if not bool(active.any()):
            break

        drive = torch.zeros(neurons, count, device=device).index_add(
            0, model.inputs, model.drive(bytes_batch[:, step])
        )
        pre = torch.sparse.mm(operator, state) * spec.gain + drive
        updated = (1.0 - spec.leak) * state + spec.leak * torch.tanh(pre)
        state = state + (updated - state) * active[None, :]

        probed = state[model.outputs]
        accumulated = accumulated + probed * active[None, :]
        ending = (lengths == step + 1).to(state.dtype)
        final = final + (probed - final) * ending[None, :]

    mean = accumulated / lengths.clamp(min=1)[None, :].to(accumulated.dtype)
    return model.readout(torch.cat([final.T, mean.T], dim=1))


def parameter_count(model) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def _batches(documents: list[Document], spec: AdapterSpec, device):
    torch = _torch()
    for start in range(0, len(documents), spec.batch_size):
        chunk = documents[start : start + spec.batch_size]
        byte_batch, lengths = encode(chunk, spec)
        targets = np.asarray([CLASSES.index(d.label) for d in chunk])
        yield (
            torch.from_numpy(byte_batch.astype(np.int64)).to(device),
            torch.from_numpy(lengths).to(device),
            torch.from_numpy(targets).to(device),
            chunk,
        )


def train_condition(
    name: str,
    model,
    operator,
    train: list[Document],
    validate: list[Document],
    spec: TrainSpec,
    *,
    device: str = "cuda",
) -> dict:
    """Train one condition, selecting the checkpoint on validation macro-F1.

    Epochs, checkpointing and early stopping are back because there is now a
    validation split worth selecting on -- tens of documents rather than three.
    The ridge readout in :mod:`tagger` still runs the same split with none of
    them, and is reported beside this so the comparison is visible.
    """
    torch = _torch()
    model = model.to(device)
    optimiser = torch.optim.AdamW(
        model.parameters(), lr=spec.learning_rate, weight_decay=spec.weight_decay
    )
    loss_function = torch.nn.CrossEntropyLoss()

    best = {"macro_f1": -1.0, "epoch": 0, "state": None}
    history: list[dict] = []
    started = time.perf_counter()

    for epoch in range(1, spec.max_epochs + 1):
        model.train()
        total = 0.0
        for byte_batch, lengths, targets, _ in _batches(train, spec.adapter, device):
            optimiser.zero_grad(set_to_none=True)
            logits = (
                reservoir_forward(model, operator, byte_batch, lengths, spec.adapter)
                if operator is not None
                else model(byte_batch, lengths)
            )
            loss = loss_function(logits, targets)
            loss.backward()
            optimiser.step()
            total += float(loss.detach()) * targets.numel()

        model.eval()
        predictions, truth = [], []
        with torch.no_grad():
            for byte_batch, lengths, targets, _ in _batches(validate, spec.adapter, device):
                logits = (
                    reservoir_forward(model, operator, byte_batch, lengths, spec.adapter)
                    if operator is not None
                    else model(byte_batch, lengths)
                )
                predictions.append(logits.argmax(dim=1).cpu().numpy())
                truth.append(targets.cpu().numpy())
        scored = macro_f1(np.concatenate(truth), np.concatenate(predictions), CLASSES)
        history.append({"epoch": epoch, "train_loss": total / max(len(train), 1), **scored})

        if scored["macro_f1"] > best["macro_f1"]:
            best = {
                "macro_f1": scored["macro_f1"],
                "epoch": epoch,
                "state": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
            }
        elif epoch >= spec.min_epochs and epoch - best["epoch"] >= spec.patience:
            break

    if best["state"] is not None:
        model.load_state_dict(best["state"])
    return {
        "condition": name,
        "parameters": parameter_count(model),
        "best_epoch": best["epoch"],
        "stopped_epoch": history[-1]["epoch"] if history else 0,
        "validation_macro_f1": best["macro_f1"],
        "history": history,
        "seconds": round(time.perf_counter() - started, 1),
        "spec": {"train": asdict(spec), "adapter": asdict(spec.adapter)},
    }


def evaluate_condition(model, operator, documents: list[Document], spec: AdapterSpec, device: str):
    """Held-out score for a trained condition."""
    torch = _torch()
    model.eval()
    predictions, truth = [], []
    with torch.no_grad():
        for byte_batch, lengths, targets, _ in _batches(documents, spec, device):
            logits = (
                reservoir_forward(model, operator, byte_batch, lengths, spec)
                if operator is not None
                else model(byte_batch, lengths)
            )
            predictions.append(logits.argmax(dim=1).cpu().numpy())
            truth.append(targets.cpu().numpy())
    return macro_f1(np.concatenate(truth), np.concatenate(predictions), CLASSES)
