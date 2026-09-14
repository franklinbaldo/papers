"""CUDA cache warmer for the frozen confirmatory MaleCNS runner.

This module intentionally does *not* implement scoring, model selection or any
scientific decision rule. It computes the same recurrent states as
``multitag.reservoir_states`` while evolving several gains in parallel on a
single sparse-matrix/dense-matrix multiply. The existing CPU runner remains the
arbiter and consumes the resulting ``.npy`` files through its normal cache keys.

Torch is imported lazily so the default CPU experiment keeps its small NumPy /
SciPy dependency set. Kaggle installs the existing ``train`` extra.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from .multitag import interpolate, unit_rows


@dataclass(frozen=True)
class ParityStats:
    max_abs: float
    rmse: float
    reference_rms: float

    @property
    def relative_rmse(self) -> float:
        return self.rmse / max(self.reference_rms, 1e-12)


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - exercised only without train extra
        raise RuntimeError(
            "GPU cache warming needs the optional train dependency: "
            "pip install -e '.[train]'"
        ) from exc
    return torch


def scipy_csr_to_torch(matrix: sp.csr_matrix, *, device: str):
    """Copy one SciPy CSR operator to a Torch sparse CSR tensor."""
    torch = _torch()
    csr = matrix.tocsr().astype(np.float32, copy=False)
    crow = torch.from_numpy(csr.indptr.astype(np.int64, copy=False)).to(device)
    col = torch.from_numpy(csr.indices.astype(np.int64, copy=False)).to(device)
    values = torch.from_numpy(csr.data.astype(np.float32, copy=False)).to(device)
    return torch.sparse_csr_tensor(
        crow,
        col,
        values,
        size=csr.shape,
        dtype=torch.float32,
        device=device,
    )


def reservoir_states_multi_gain(
    operator: sp.csr_matrix,
    sensation: np.ndarray,
    *,
    input_weights: np.ndarray,
    readout_indices: np.ndarray,
    input_indices: np.ndarray,
    gains: tuple[float, ...] | list[float],
    leak: float,
    steps_per_chunk: int,
    scale: float,
    device: str = "cuda",
    torch_operator=None,
) -> dict[float, np.ndarray]:
    """Run one document for every gain with one ``W @ X`` per timestep.

    The columns of ``state`` are independent trajectories. Sharing the sparse
    matrix read does not couple them: each column is multiplied by its own gain,
    receives the same sensory drive, and applies tanh independently.
    """
    torch = _torch()
    gain_values = tuple(float(g) for g in gains)
    if not gain_values:
        raise ValueError("at least one gain is required")

    path, owners = interpolate(unit_rows(sensation), steps_per_chunk)
    projected = (
        np.asarray(input_weights, dtype=np.float32) @ path.T
    ) * np.float32(scale)

    sparse = (
        torch_operator
        if torch_operator is not None
        else scipy_csr_to_torch(operator, device=device)
    )
    neurons = operator.shape[0]
    width = len(gain_values)
    chunks = len(sensation)
    readout_indices = np.asarray(readout_indices, dtype=np.int64)
    input_indices = np.asarray(input_indices, dtype=np.int64)

    state = torch.zeros((neurons, width), dtype=torch.float32, device=device)
    drive = torch.zeros(neurons, dtype=torch.float32, device=device)
    gains_t = torch.tensor(gain_values, dtype=torch.float32, device=device)[None, :]
    input_idx_t = torch.from_numpy(input_indices).to(device)
    readout_idx_t = torch.from_numpy(readout_indices).to(device)
    projected_t = torch.from_numpy(projected).to(device)

    # [gain, chunk, readout]. owners can revisit a chunk during interpolation;
    # assignment deliberately keeps the last step exactly like reservoir_states.
    collected = torch.zeros(
        (width, chunks, readout_indices.size), dtype=torch.float32, device=device
    )

    with torch.no_grad():
        for step, owner in enumerate(owners):
            drive.zero_()
            drive[input_idx_t] = projected_t[:, step]
            recurrent = torch.sparse.mm(sparse, state)
            pre = recurrent * gains_t + drive[:, None]
            state = (1.0 - float(leak)) * state + float(leak) * torch.tanh(pre)
            # state[readout] is [R,G]; transpose to [G,R].
            collected[:, int(owner), :] = state.index_select(0, readout_idx_t).T

    result = collected.cpu().numpy()
    return {gain: result[index] for index, gain in enumerate(gain_values)}


def compare_states(reference: np.ndarray, candidate: np.ndarray) -> ParityStats:
    """Numerical parity diagnostics; no pass/fail threshold is hidden here."""
    left = np.asarray(reference, dtype=np.float64)
    right = np.asarray(candidate, dtype=np.float64)
    if left.shape != right.shape:
        raise ValueError(f"shape mismatch: {left.shape} != {right.shape}")
    error = right - left
    return ParityStats(
        max_abs=float(np.max(np.abs(error))) if error.size else 0.0,
        rmse=float(np.sqrt(np.mean(error * error))) if error.size else 0.0,
        reference_rms=float(np.sqrt(np.mean(left * left))) if left.size else 0.0,
    )
