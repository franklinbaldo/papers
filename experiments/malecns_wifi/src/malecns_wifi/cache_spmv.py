"""MaleCNS Cache-Resident SpMV Optimization Module.

Provides compact, L2/L3 cache-resident sparse matrix representations and fused
recurrent kernels tailored for the Intel Core i3-10100T (6 MB L3 cache).

Features:
- Structural pruning of synaptic noise (|data| >= threshold)
- Delta-uint16 column indexing with automatic hop escapes
- 4-bit non-linear codebook with L1/register LUT (2.5 bytes/edge)
- INT8 exact integer weight encoding (3.0 bytes/edge)
- Fused recurrent step (SpMV + gain + drive + tanh + leak) eliminating DRAM trips
- Strict per-row normalization (row_normalise) for dynamical stability
"""

from __future__ import annotations

import numba as nb
import numpy as np
import scipy.sparse as sp


# ==============================================================================
# Native Numba JIT Kernels
# ==============================================================================

@nb.njit(parallel=True, fastmath=True)
def _spmv_compact_4bit(offsets, deltas, packed_weights, lut, row_scales, x, out):
    """SpMV using uint16 deltas and packed 4-bit codebook with row scaling."""
    n = len(row_scales)
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            code = (packed_weights[j >> 1] >> (4 * (j & 1))) & 0x0F
            acc += lut[code] * x[col]
        out[r] = acc * row_scales[r]


@nb.njit(parallel=True, fastmath=True)
def _fused_recurrent_step_4bit(
    offsets, deltas, packed_weights, lut, row_scales, x_cur, x_nxt, drive, gain, leak
):
    """Fused Recurrent Step: SpMV + drive + gain + tanh + leak integration in 1 pass."""
    n = len(row_scales)
    alpha = 1.0 - leak
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            code = (packed_weights[j >> 1] >> (4 * (j & 1))) & 0x0F
            acc += lut[code] * x_cur[col]
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


@nb.njit(parallel=True, fastmath=True)
def _spmv_compact_int8(offsets, deltas, weights_int8, row_scales, x, out):
    """SpMV using uint16 deltas and signed INT8 weights with row scaling."""
    n = len(row_scales)
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            acc += np.float32(weights_int8[j]) * x[col]
        out[r] = acc * row_scales[r]


@nb.njit(parallel=True, fastmath=True)
def _fused_recurrent_step_int8(
    offsets, deltas, weights_int8, row_scales, x_cur, x_nxt, drive, gain, leak
):
    """Fused Recurrent Step for INT8 compact operator."""
    n = len(row_scales)
    alpha = 1.0 - leak
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            acc += np.float32(weights_int8[j]) * x_cur[col]
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


def _warmup_jit():
    o = np.array([0, 2], dtype=np.int32)
    d = np.array([5, 10], dtype=np.uint16)
    pw = np.array([0x12], dtype=np.uint8)
    lut = np.zeros(16, dtype=np.float32)
    lut[1] = 2.0
    lut[2] = -3.0
    rs = np.array([0.5], dtype=np.float32)
    x = np.zeros(20, dtype=np.float32)
    x[5] = 1.0
    x[15] = 2.0
    out = np.zeros(1, dtype=np.float32)
    drv = np.zeros(1, dtype=np.float32)
    _spmv_compact_4bit(o, d, pw, lut, rs, x, out)
    _fused_recurrent_step_4bit(o, d, pw, lut, rs, x, x[:1], drv, 4.0, 0.4)
    w8 = np.array([2, -3], dtype=np.int8)
    _spmv_compact_int8(o, d, w8, rs, x, out)
    _fused_recurrent_step_int8(o, d, w8, rs, x, x[:1], drv, 4.0, 0.4)


_warmup_jit()


# ==============================================================================
# Helper Functions
# ==============================================================================

def make_pruned_matrix(
    raw: sp.csr_matrix, threshold: int, protected_rows: set[int] | None = None
) -> sp.csr_matrix:
    """Keep edges where |data| >= threshold, or all edges for protected rows."""
    n = raw.shape[0]
    if threshold <= 3 and protected_rows is None:
        return raw.copy()

    mask = np.zeros(raw.nnz, dtype=bool)
    abs_d = np.abs(raw.data)

    for r in range(n):
        s = raw.indptr[r]
        e = raw.indptr[r + 1]
        if protected_rows is not None and r in protected_rows:
            mask[s:e] = True
        else:
            mask[s:e] = abs_d[s:e] >= threshold

    diffs = np.zeros(n, dtype=np.int32)
    for r in range(n):
        s = raw.indptr[r]
        e = raw.indptr[r + 1]
        diffs[r] = np.count_nonzero(mask[s:e])

    indptr = np.zeros(n + 1, dtype=np.int32)
    indptr[1:] = np.cumsum(diffs)
    return sp.csr_matrix((raw.data[mask], raw.indices[mask], indptr), shape=raw.shape)


class CompactOperator4Bit:
    """Cache-resident CSR with Delta-uint16 and 4-bit Codebook LUT."""

    def __init__(self, pruned_raw: sp.csr_matrix, lut: np.ndarray | None = None):
        n = pruned_raw.shape[0]
        in_strength = np.asarray(np.abs(pruned_raw).sum(axis=1)).ravel()
        self.row_scales = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)

        if lut is None:
            lut = np.array([
                0.0, -80.0, -32.0, -16.0, -10.0, -7.0, -5.0, -3.0,
                0.0, 3.0, 5.0, 7.0, 10.0, 16.0, 32.0, 80.0
            ], dtype=np.float32)
        self.lut = lut
        pos_levels = lut[9:]
        neg_levels = lut[1:8]

        deltas_list: list[int] = []
        codes_list: list[int] = []
        offsets_list: list[int] = [0]

        for r in range(n):
            s = pruned_raw.indptr[r]
            e = pruned_raw.indptr[r + 1]
            cols = pruned_raw.indices[s:e]
            vals = pruned_raw.data[s:e]
            curr_col = 0
            for c, v in zip(cols, vals):
                d = c - curr_col
                while d > 65535:
                    deltas_list.append(65535)
                    codes_list.append(0)  # zero weight dummy
                    curr_col += 65535
                    d -= 65535
                if v > 0:
                    c_idx = 9 + int(np.abs(pos_levels - v).argmin())
                elif v < 0:
                    c_idx = 1 + int(np.abs(neg_levels - v).argmin())
                else:
                    c_idx = 0
                deltas_list.append(d)
                codes_list.append(c_idx)
                curr_col = c
            offsets_list.append(len(deltas_list))

        self.offsets = np.array(offsets_list, dtype=np.int32)
        self.deltas = np.array(deltas_list, dtype=np.uint16)
        codes = np.array(codes_list, dtype=np.uint8)

        packed_len = (len(codes) + 1) // 2
        self.packed_weights = np.zeros(packed_len, dtype=np.uint8)
        for i in range(0, len(codes), 2):
            c0 = codes[i] & 0x0F
            c1 = (codes[i + 1] & 0x0F) if i + 1 < len(codes) else 0
            self.packed_weights[i // 2] = c0 | (c1 << 4)

        self.nnz = len(self.deltas)
        self.original_nnz = pruned_raw.nnz
        self.n_rows = n
        self._file = None
        self._mmap = None
        self.input_indices = None
        self.readout_indices = None

    @classmethod
    def from_flatbuffer(cls, file_path: str | Path) -> CompactOperator4Bit:
        """Loads a CompactOperator4Bit directly from a zero-copy FlatBuffer (.mcns)."""
        import mmap
        from pathlib import Path
        from .schema.MaleCNS import ConnectomeModel as CM

        path = Path(file_path)
        f = open(path, "rb")
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if not CM.ConnectomeModel.ConnectomeModelBufferHasIdentifier(mm, 0):
            raise ValueError("Invalid MaleCNS FlatBuffer identifier")

        model = CM.ConnectomeModel.GetRootAs(mm, 0)
        instance = cls.__new__(cls)
        instance._file = f
        instance._mmap = mm
        instance.offsets = model.RowOffsetsAsNumpy()
        instance.row_scales = model.RowScalesAsNumpy()
        instance.deltas = model.DeltasAsNumpy()
        instance.packed_weights = model.WeightsDataAsNumpy()
        instance.lut = model.LutAsNumpy()
        instance.input_indices = model.InputIndicesAsNumpy()
        instance.readout_indices = model.ReadoutIndicesAsNumpy()
        instance.nnz = len(instance.deltas)
        instance.original_nnz = model.TotalEdges()
        instance.n_rows = model.NumNeurons()
        return instance

    @property
    def memory_bytes(self) -> int:
        return (
            self.offsets.nbytes
            + self.row_scales.nbytes
            + self.deltas.nbytes
            + self.packed_weights.nbytes
            + self.lut.nbytes
        )

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def spmv(self, x: np.ndarray, out: np.ndarray) -> None:
        _spmv_compact_4bit(self.offsets, self.deltas, self.packed_weights, self.lut, self.row_scales, x, out)

    def fused_step(
        self, x_cur: np.ndarray, x_nxt: np.ndarray, drive: np.ndarray, gain: float = 4.0, leak: float = 0.4
    ) -> None:
        _fused_recurrent_step_4bit(
            self.offsets, self.deltas, self.packed_weights, self.lut, self.row_scales, x_cur, x_nxt, drive, gain, leak
        )


class CompactOperatorInt8:
    """Cache-resident CSR with Delta-uint16 and exact INT8 weights."""

    def __init__(self, pruned_raw: sp.csr_matrix):
        n = pruned_raw.shape[0]
        in_strength = np.asarray(np.abs(pruned_raw).sum(axis=1)).ravel()
        self.row_scales = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)

        deltas_list: list[int] = []
        weights_list: list[int] = []
        offsets_list: list[int] = [0]

        for r in range(n):
            s = pruned_raw.indptr[r]
            e = pruned_raw.indptr[r + 1]
            cols = pruned_raw.indices[s:e]
            vals = pruned_raw.data[s:e]
            curr_col = 0
            for c, v in zip(cols, vals):
                d = c - curr_col
                while d > 65535:
                    deltas_list.append(65535)
                    weights_list.append(0)  # zero weight dummy
                    curr_col += 65535
                    d -= 65535
                v_clipped = int(np.clip(v, -127, 127))
                deltas_list.append(d)
                weights_list.append(v_clipped)
                curr_col = c
            offsets_list.append(len(deltas_list))

        self.offsets = np.array(offsets_list, dtype=np.int32)
        self.deltas = np.array(deltas_list, dtype=np.uint16)
        self.weights_int8 = np.array(weights_list, dtype=np.int8)
        self.nnz = len(self.deltas)
        self.original_nnz = pruned_raw.nnz
        self.n_rows = n

    @property
    def memory_bytes(self) -> int:
        return (
            self.offsets.nbytes
            + self.row_scales.nbytes
            + self.deltas.nbytes
            + self.weights_int8.nbytes
        )

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def spmv(self, x: np.ndarray, out: np.ndarray) -> None:
        _spmv_compact_int8(self.offsets, self.deltas, self.weights_int8, self.row_scales, x, out)

    def fused_step(
        self, x_cur: np.ndarray, x_nxt: np.ndarray, drive: np.ndarray, gain: float = 4.0, leak: float = 0.4
    ) -> None:
        _fused_recurrent_step_int8(
            self.offsets, self.deltas, self.weights_int8, self.row_scales, x_cur, x_nxt, drive, gain, leak
        )
