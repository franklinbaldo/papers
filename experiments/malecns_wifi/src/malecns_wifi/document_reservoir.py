"""Frozen MaleCNS document reservoir: staged, backend-switchable, label-free.

The logical representation is fixed and shared by every backend::

    document -> text windows -> frozen MiniLM/E5 -> fused semantic vector
             -> fixed Gaussian sensory projection (RMS-normalised per document)
             -> row-normalised MaleCNS recurrent step (gain, leak, tanh)
             -> fixed sparse whole-brain readout -> unit 256-d embedding

``canonical`` reproduces the original ``FrozenMaleCNSEncoder`` arithmetic step
for step. ``fast`` keeps the same arithmetic but (a) skips the recurrent SpMM at
the first step, where the state is exactly zero, (b) adds the sensory drive in
place on the recurrent term instead of materialising a dense drive tensor, and
(c) is meant to be fed batches grouped by window count so no masked steps are
wasted. Every fast-path change is exact in IEEE arithmetic (``0 * gain + d ==
d``; adding zero to a float is the identity), so the two backends are expected to
agree to floating-point noise, and the benchmark scripts verify that.

Label-free controls share the same fused semantic inputs so the benchmark can
ask how much the connectome adds on top of the frozen encoders.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import scipy.sparse as sp

BACKENDS = ("canonical", "fast")
CONTROL_VARIANTS = ("fused-mean", "fused-mean-proj", "sensory-only")
VARIANTS = ("malecns",) + CONTROL_VARIANTS


def sample_windows(text: str, *, max_chunks: int, chunk_chars: int) -> list[str]:
    """Deterministic text windows spread across the document (official policy)."""
    text = str(text or "").strip()
    if not text:
        return [" "]
    if len(text) <= chunk_chars:
        return [text]
    count = min(max_chunks, max(2, math.ceil(len(text) / chunk_chars)))
    max_start = max(0, len(text) - chunk_chars)
    starts = np.linspace(0, max_start, num=count, dtype=np.int64)
    return [text[int(start): int(start) + chunk_chars] for start in starts]


def unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    if values.ndim == 1:
        values = values[None, :]
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)


def sensory_input_weights(sensory_neurons: int, semantic_dim: int, *, seed: int) -> np.ndarray:
    """Fixed Gaussian projection from the fused semantic space onto sensory neurons."""
    rng = np.random.default_rng(seed)
    weights = rng.normal(size=(sensory_neurons, semantic_dim)).astype(np.float32)
    return weights / np.float32(math.sqrt(semantic_dim))


def fixed_sparse_projection_arrays(rows: int, cols: int, *, seed: int):
    """Sparse signed readout: ``sqrt(cols)`` entries per row, seed-determined."""
    rng = np.random.default_rng(seed)
    per_row = max(1, int(round(math.sqrt(cols))))
    row = np.repeat(np.arange(rows, dtype=np.int64), per_row)
    col = np.concatenate([
        rng.choice(cols, size=per_row, replace=False).astype(np.int64)
        for _ in range(rows)
    ])
    sign = rng.choice([-1.0, 1.0], size=len(row)).astype(np.float32)
    value = sign / np.float32(math.sqrt(per_row))
    return row, col, value


def control_projection(semantic_dim: int, width: int, *, seed: int) -> np.ndarray:
    """Fixed Gaussian projection used by the ``fused-mean-proj`` control."""
    rng = np.random.default_rng(seed)
    weights = rng.normal(size=(width, semantic_dim)).astype(np.float32)
    return weights / np.float32(math.sqrt(semantic_dim))


def csr_to_torch(matrix: sp.csr_matrix, *, device, index_dtype=None):
    import torch

    matrix = matrix.tocsr().astype(np.float32)
    if index_dtype is None:
        index_dtype = torch.int64
    return torch.sparse_csr_tensor(
        torch.as_tensor(matrix.indptr, dtype=index_dtype, device=device),
        torch.as_tensor(matrix.indices, dtype=index_dtype, device=device),
        torch.as_tensor(matrix.data, dtype=torch.float32, device=device),
        size=matrix.shape,
        device=device,
    )


def fixed_sparse_projection(rows: int, cols: int, *, seed: int, device):
    import torch

    row, col, value = fixed_sparse_projection_arrays(rows, cols, seed=seed)
    indices = torch.as_tensor(np.vstack([row, col]), dtype=torch.int64, device=device)
    values = torch.as_tensor(value, dtype=torch.float32, device=device)
    return torch.sparse_coo_tensor(indices, values, (rows, cols), device=device).coalesce()


@dataclass(frozen=True)
class DocumentReservoirConfig:
    readout_width: int = 256
    seed: int = 20260915
    max_chunks: int = 4
    chunk_chars: int = 3000
    gain: float = 4.0
    leak: float = 0.4
    target_rms: float = 0.05

    def as_dict(self) -> dict[str, Any]:
        return {
            "readout_width": self.readout_width,
            "seed": self.seed,
            "max_chunks": self.max_chunks,
            "chunk_chars": self.chunk_chars,
            "gain": self.gain,
            "leak": self.leak,
            "target_rms": self.target_rms,
        }


@dataclass
class ReservoirStats:
    documents: int = 0
    chunks: int = 0
    batches: int = 0
    spmm_calls: int = 0
    spmm_columns: int = 0  # column-SpMV equivalents
    spmm_seconds: float = 0.0
    forward_seconds: float = 0.0
    masked_column_steps: int = 0  # wasted (doc, step) pairs due to ragged batches

    def as_dict(self) -> dict[str, Any]:
        return {
            "documents": self.documents,
            "chunks": self.chunks,
            "batches": self.batches,
            "spmm_calls": self.spmm_calls,
            "spmm_columns": self.spmm_columns,
            "spmm_seconds": self.spmm_seconds,
            "spmm_mean_ms": (1000.0 * self.spmm_seconds / self.spmm_calls) if self.spmm_calls else None,
            "forward_seconds": self.forward_seconds,
            "masked_column_steps": self.masked_column_steps,
            "docs_per_second": (self.documents / self.forward_seconds) if self.forward_seconds else None,
            "chunks_per_second": (self.chunks / self.forward_seconds) if self.forward_seconds else None,
        }


def pack_cube(fused: np.ndarray, offsets: np.ndarray, doc_indices) -> tuple[np.ndarray, np.ndarray]:
    """Gather ``[batch, steps, dim]`` cube and active mask from flat chunk rows."""
    doc_indices = np.asarray(doc_indices, dtype=np.int64)
    counts = offsets[doc_indices + 1] - offsets[doc_indices]
    steps = int(counts.max()) if counts.size else 0
    dim = int(fused.shape[1])
    cube = np.zeros((len(doc_indices), steps, dim), dtype=np.float32)
    active = np.zeros((len(doc_indices), steps), dtype=np.bool_)
    for row, doc in enumerate(doc_indices):
        start, stop = int(offsets[doc]), int(offsets[doc + 1])
        cube[row, : stop - start] = fused[start:stop]
        active[row, : stop - start] = True
    return cube, active


def iter_batches(
    offsets: np.ndarray,
    *,
    batch_size: int,
    group_by_length: bool,
) -> Iterator[np.ndarray]:
    """Yield document index batches; grouped batches share one window count."""
    n_docs = int(len(offsets) - 1)
    counts = np.diff(offsets)
    if not group_by_length:
        for start in range(0, n_docs, batch_size):
            yield np.arange(start, min(start + batch_size, n_docs), dtype=np.int64)
        return
    for length in np.unique(counts):
        members = np.flatnonzero(counts == length)
        for start in range(0, len(members), batch_size):
            yield members[start:start + batch_size]


class DocumentReservoir:
    """Frozen MaleCNS recurrent document encoder over a torch device."""

    def __init__(
        self,
        matrix: sp.csr_matrix,
        input_indices: np.ndarray,
        *,
        semantic_dim: int,
        config: DocumentReservoirConfig,
        device,
        backend: str = "canonical",
        index_dtype: str = "int64",
    ):
        import torch

        if backend not in BACKENDS:
            raise ValueError(f"unknown backend {backend!r}; expected one of {BACKENDS}")
        self.config = config
        self.backend = backend
        self.device = torch.device(device)
        self.neurons = int(matrix.shape[0])
        self.edges = int(matrix.nnz)
        self.semantic_dim = int(semantic_dim)
        self.index_dtype = index_dtype
        torch_index = {"int64": torch.int64, "int32": torch.int32}[index_dtype]
        self.operator = csr_to_torch(matrix, device=self.device, index_dtype=torch_index)
        self.input_indices = torch.as_tensor(
            np.asarray(input_indices, dtype=np.int64), dtype=torch.int64, device=self.device
        )
        self.sensory_neurons = int(self.input_indices.numel())
        self.input_weights = torch.as_tensor(
            sensory_input_weights(self.sensory_neurons, self.semantic_dim, seed=config.seed),
            dtype=torch.float32,
            device=self.device,
        )
        self.readout_projection = fixed_sparse_projection(
            config.readout_width, self.neurons, seed=config.seed + 17, device=self.device
        )
        self.stats = ReservoirStats()

    # -- timing helpers -----------------------------------------------------
    def _sync(self) -> None:
        import torch

        if self.device.type == "cuda":
            torch.cuda.synchronize(self.device)

    def _spmm(self, state, *, columns: int):
        import torch

        self._sync()
        t0 = time.perf_counter()
        out = torch.sparse.mm(self.operator, state)
        self._sync()
        self.stats.spmm_seconds += time.perf_counter() - t0
        self.stats.spmm_calls += 1
        self.stats.spmm_columns += columns
        return out

    # -- forward ------------------------------------------------------------
    def forward(self, cube: np.ndarray, active: np.ndarray, *, gain: float | None = None) -> np.ndarray:
        """Return unit-normalised ``[batch, readout_width]`` embeddings."""
        import torch

        gain = self.config.gain if gain is None else float(gain)
        leak = self.config.leak
        target_rms = self.config.target_rms
        batch, steps, _ = cube.shape
        active = np.asarray(active, dtype=np.bool_)
        self._sync()
        t0 = time.perf_counter()

        features = torch.as_tensor(cube, dtype=torch.float32, device=self.device)
        active_t = torch.as_tensor(active, dtype=torch.bool, device=self.device)
        state = torch.zeros((self.neurons, batch), dtype=torch.float32, device=self.device)
        full_mask = bool(active.all())

        for step in range(steps):
            local = features[:, step, :]
            projected = self.input_weights @ local.T
            rms = torch.sqrt(torch.mean(projected.square(), dim=0, keepdim=True)).clamp_min(1e-12)
            projected = projected * (target_rms / rms)

            if self.backend == "canonical":
                drive = torch.zeros_like(state)
                drive.index_copy_(0, self.input_indices, projected)
                pre = self._spmm(state, columns=batch) * gain + drive
            else:
                if step == 0:
                    # state is exactly zero: W @ 0 == 0 and 0 * gain + drive == drive.
                    pre = torch.zeros_like(state)
                    pre.index_copy_(0, self.input_indices, projected)
                else:
                    pre = self._spmm(state, columns=batch) * gain
                    # Non-sensory rows: pre + 0 == pre. Sensory rows: pre + drive.
                    pre.index_add_(0, self.input_indices, projected)

            updated = (1.0 - leak) * state + leak * torch.tanh(pre)
            if full_mask:
                state = updated
            else:
                mask = active_t[:, step][None, :]
                self.stats.masked_column_steps += int((~active[:, step]).sum())
                state = torch.where(mask, updated, state)

        readout = torch.sparse.mm(self.readout_projection, state).T
        readout = readout / torch.linalg.vector_norm(readout, dim=1, keepdim=True).clamp_min(1e-12)
        result = readout.detach().cpu().numpy().astype(np.float32)
        self._sync()
        self.stats.forward_seconds += time.perf_counter() - t0
        self.stats.documents += batch
        self.stats.chunks += int(active.sum())
        self.stats.batches += 1
        return result

    def encode_cached(
        self,
        fused: np.ndarray,
        offsets: np.ndarray,
        *,
        batch_size: int,
        group_by_length: bool | None = None,
        gain: float | None = None,
        progress=None,
    ) -> np.ndarray:
        """Encode every document of a semantic cache; output follows cache order."""
        if group_by_length is None:
            group_by_length = self.backend == "fast"
        n_docs = int(len(offsets) - 1)
        output = np.zeros((n_docs, self.config.readout_width), dtype=np.float32)
        done = 0
        for docs in iter_batches(offsets, batch_size=batch_size, group_by_length=group_by_length):
            cube, active = pack_cube(fused, offsets, docs)
            output[docs] = self.forward(cube, active, gain=gain)
            done += len(docs)
            if progress is not None:
                progress(done, n_docs, self.stats)
        return output


# -- label-free controls ----------------------------------------------------

def control_embeddings(
    variant: str,
    fused: np.ndarray,
    offsets: np.ndarray,
    *,
    config: DocumentReservoirConfig,
    reservoir: DocumentReservoir | None = None,
    batch_size: int = 256,
) -> np.ndarray:
    """Controls sharing the exact same fused semantic inputs as MaleCNS.

    ``fused-mean``: unit mean of the fused chunk vectors (no projection).
    ``fused-mean-proj``: the same mean pushed through a fixed Gaussian projection
    to ``readout_width`` dimensions (seeded, label-free).
    ``sensory-only``: the full MaleCNS pipeline with the recurrent operator
    removed (``gain = 0``): sensory projection + leaky tanh + sparse readout, so
    whatever the real graph adds is isolated from the projection scaffolding.
    """
    n_docs = int(len(offsets) - 1)
    if variant == "sensory-only":
        if reservoir is None:
            raise ValueError("sensory-only control needs a DocumentReservoir")
        return reservoir.encode_cached(fused, offsets, batch_size=batch_size, gain=0.0)
    means = np.zeros((n_docs, fused.shape[1]), dtype=np.float32)
    for doc in range(n_docs):
        means[doc] = fused[offsets[doc]:offsets[doc + 1]].mean(axis=0)
    if variant == "fused-mean":
        return unit_rows(means)
    if variant == "fused-mean-proj":
        weights = control_projection(fused.shape[1], config.readout_width, seed=config.seed + 29)
        return unit_rows(means @ weights.T)
    raise ValueError(f"unknown control variant {variant!r}; expected one of {CONTROL_VARIANTS}")


# -- equivalence ----------------------------------------------------------

def equivalence_report(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    reference = np.asarray(reference, dtype=np.float64)
    candidate = np.asarray(candidate, dtype=np.float64)
    if reference.shape != candidate.shape:
        raise ValueError(f"shape mismatch: {reference.shape} vs {candidate.shape}")
    diff = np.abs(reference - candidate)
    cos = np.sum(unit_rows(reference) * unit_rows(candidate), axis=1)
    return {
        "max_abs_error": float(diff.max()) if diff.size else 0.0,
        "mean_abs_error": float(diff.mean()) if diff.size else 0.0,
        "min_cosine": float(cos.min()) if cos.size else 1.0,
        "mean_cosine": float(cos.mean()) if cos.size else 1.0,
        "bit_exact": bool(np.array_equal(reference, candidate)),
        "documents": int(reference.shape[0]),
    }


def passes_gate(report: dict[str, Any], *, max_abs_error: float = 1e-5, min_cosine: float = 0.999999) -> bool:
    return report["max_abs_error"] <= max_abs_error and report["min_cosine"] >= min_cosine


def load_reservoir_inputs(graph: Path):
    """Row-normalised operator plus sensory population, as in the MTEB encoder."""
    from malecns_wifi import load_graph
    from malecns_wifi.tagger import row_normalise, select_populations

    matrix = row_normalise(load_graph(graph))
    archive = np.load(graph, allow_pickle=False)
    populations = select_populations(archive["superclass"])
    return matrix, populations.input_indices
