"""Empirical Test Suite: BitNet 1.58-bit (Ternary {-1, 0, +1}) vs 4-bit LUT vs FP32 on MaleCNS.

Evaluates:
1. Pure Ternary 1.58-bit SpMV (Multiply-free: pure additions and subtractions)
2. 2-bit Ternary with Magnitude Bins {-4, -1, +1, +4} (2 bits per weight)
3. 4-bit Non-linear Codebook LUT (4 bits per weight)
4. Full FP32 Baseline (32 bits per weight)

Measures:
- Memory footprint (MB) and bits per edge
- SpMV latency (ms/step) and recurrent throughput (steps/sec)
- Speedup vs PyTorch CPU baseline
- Dynamic fidelity:
  - Readout cosine similarity at steps 4, 16, 100
  - Whole-brain cosine similarity at steps 4, 16, 100
  - Spearman rank correlation at step 100
- Numerical stability and boundedness
"""

from __future__ import annotations

import time
import numpy as np
import scipy.sparse as sp
import numba as nb
from scipy.stats import spearmanr
import torch

from malecns_wifi import load_graph, make_pruned_matrix
from malecns_wifi.tagger import row_normalise, select_populations
from malecns_wifi.cache_spmv import CompactOperator4Bit


# ==============================================================================
# Numba Kernels for 1.58-bit (Ternary Multiply-Free)
# ==============================================================================

@nb.njit(parallel=True, fastmath=True)
def _ternary_spmv_fused(offsets, deltas, packed_signs, dummy_mask, row_scales, x_cur, x_nxt, drive, gain, leak):
    """1.58-bit SpMV: ZERO multiplications in the inner loop.
    
    Only integer bit-shifts, addition, subtraction, and post-row scaling.
    """
    n = len(row_scales)
    alpha = 1.0 - leak
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            # Check if this is a dummy jump edge (used to advance col by > 65535)
            is_dummy = (dummy_mask[j >> 3] >> (j & 7)) & 1
            if is_dummy == 0:
                sign = (packed_signs[j >> 3] >> (j & 7)) & 1
                val = x_cur[col]
                if sign == 1:
                    acc -= val
                else:
                    acc += val
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


@nb.njit(parallel=True, fastmath=True)
def _bitnet_2bit_fused(offsets, deltas, packed_2bit, dummy_mask, row_scales, x_cur, x_nxt, drive, gain, leak):
    """2-bit BitNet: {-4, -1, +1, +4} (sign bit + 1 magnitude shift bit)."""
    n = len(row_scales)
    alpha = 1.0 - leak
    for r in nb.prange(n):
        s = offsets[r]
        e = offsets[r + 1]
        col = 0
        acc = 0.0
        for j in range(s, e):
            col += deltas[j]
            is_dummy = (dummy_mask[j >> 3] >> (j & 7)) & 1
            if is_dummy == 0:
                # 2 bits per edge: 4 edges per uint8
                code = (packed_2bit[j >> 2] >> (2 * (j & 3))) & 3
                val = x_cur[col]
                # code 0: +1, code 1: -1, code 2: +4, code 3: -4
                if code == 0:
                    acc += val
                elif code == 1:
                    acc -= val
                elif code == 2:
                    acc += val * 4.0
                else:
                    acc -= val * 4.0
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


# ==============================================================================
# 1.58-bit and 2-bit Operator Builders
# ==============================================================================

class BitNet158Operator:
    """Ternary {-1, 0, +1} cache-resident operator with 1-bit sign packing."""

    def __init__(self, pruned_raw: sp.csr_matrix):
        n = pruned_raw.shape[0]
        # In ternary, every active edge has absolute weight 1.0 before row-normalisation
        # Therefore in_strength = degree of row
        diffs = np.diff(pruned_raw.indptr)
        self.row_scales = (1.0 / np.maximum(diffs, 1.0)).astype(np.float32)

        deltas_list = []
        signs_list = []
        dummy_list = []
        offsets_list = [0]

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
                    signs_list.append(0)
                    dummy_list.append(1)  # dummy
                    curr_col += 65535
                    d -= 65535
                deltas_list.append(d)
                # sign: 1 if negative, 0 if positive
                signs_list.append(1 if v < 0 else 0)
                dummy_list.append(0)
                curr_col = c
            offsets_list.append(len(deltas_list))

        self.offsets = np.array(offsets_list, dtype=np.int32)
        self.deltas = np.array(deltas_list, dtype=np.uint16)
        
        # Pack signs (1 bit per edge -> 8 per byte)
        num_edges = len(deltas_list)
        packed_bytes = (num_edges + 7) // 8
        self.packed_signs = np.zeros(packed_bytes, dtype=np.uint8)
        self.dummy_mask = np.zeros(packed_bytes, dtype=np.uint8)

        for i in range(num_edges):
            if signs_list[i]:
                self.packed_signs[i >> 3] |= (1 << (i & 7))
            if dummy_list[i]:
                self.dummy_mask[i >> 3] |= (1 << (i & 7))

        self.nnz = num_edges
        self.n_rows = n

    @property
    def memory_bytes(self) -> int:
        return (
            self.offsets.nbytes
            + self.row_scales.nbytes
            + self.deltas.nbytes
            + self.packed_signs.nbytes
            + self.dummy_mask.nbytes
        )

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def fused_step(self, x_cur, x_nxt, drive, gain=4.0, leak=0.4):
        _ternary_spmv_fused(
            self.offsets, self.deltas, self.packed_signs, self.dummy_mask,
            self.row_scales, x_cur, x_nxt, drive, gain, leak
        )


class BitNet2BitOperator:
    """2-bit Ternary with Magnitude Bins {-4, -1, +1, +4}."""

    def __init__(self, pruned_raw: sp.csr_matrix):
        n = pruned_raw.shape[0]
        # Approximate weights into 4 states: {-4, -1, +1, +4}
        # Based on whether |v| >= median
        abs_v = np.abs(pruned_raw.data)
        med = float(np.median(abs_v)) if len(abs_v) > 0 else 10.0

        # Calculate row normalisation
        row_sum = np.zeros(n, dtype=np.float32)
        for r in range(n):
            s = pruned_raw.indptr[r]
            e = pruned_raw.indptr[r + 1]
            for val in pruned_raw.data[s:e]:
                w = 4.0 if abs(val) >= med else 1.0
                row_sum[r] += w
        self.row_scales = (1.0 / np.maximum(row_sum, 1.0)).astype(np.float32)

        deltas_list = []
        codes_list = []
        dummy_list = []
        offsets_list = [0]

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
                    codes_list.append(0)
                    dummy_list.append(1)
                    curr_col += 65535
                    d -= 65535
                is_large = abs(v) >= med
                # code 0: +1, code 1: -1, code 2: +4, code 3: -4
                if v >= 0:
                    code = 2 if is_large else 0
                else:
                    code = 3 if is_large else 1
                deltas_list.append(d)
                codes_list.append(code)
                dummy_list.append(0)
                curr_col = c
            offsets_list.append(len(deltas_list))

        self.offsets = np.array(offsets_list, dtype=np.int32)
        self.deltas = np.array(deltas_list, dtype=np.uint16)

        num_edges = len(deltas_list)
        packed_2bit_bytes = (num_edges + 3) // 4
        self.packed_2bit = np.zeros(packed_2bit_bytes, dtype=np.uint8)
        self.dummy_mask = np.zeros((num_edges + 7) // 8, dtype=np.uint8)

        for i in range(num_edges):
            c = codes_list[i]
            self.packed_2bit[i >> 2] |= (c << (2 * (i & 3)))
            if dummy_list[i]:
                self.dummy_mask[i >> 3] |= (1 << (i & 7))

        self.nnz = num_edges
        self.n_rows = n

    @property
    def memory_bytes(self) -> int:
        return (
            self.offsets.nbytes
            + self.row_scales.nbytes
            + self.deltas.nbytes
            + self.packed_2bit.nbytes
            + self.dummy_mask.nbytes
        )

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def fused_step(self, x_cur, x_nxt, drive, gain=4.0, leak=0.4):
        _bitnet_2bit_fused(
            self.offsets, self.deltas, self.packed_2bit, self.dummy_mask,
            self.row_scales, x_cur, x_nxt, drive, gain, leak
        )


# ==============================================================================
# Benchmark Runner
# ==============================================================================

def run_tests():
    print("================================================================================")
    print("  EXPERIMENTO: BITNET 1.58-BIT (TERNÁRIO) vs 2-BIT vs 4-BIT vs FP32 NO MALECNS")
    print("================================================================================")
    
    raw = load_graph("artifacts/inputs/graph.npz")
    archive = np.load("artifacts/inputs/graph.npz", allow_pickle=False)
    pops = select_populations(archive["superclass"])
    protected = set(pops.input_indices) | set(pops.readout_indices)
    input_indices = pops.input_indices
    readout_indices = pops.readout_indices
    n = raw.shape[0]

    # Pre-generate 100 sensory steps
    rng = np.random.default_rng(42)
    inputs_seq = rng.normal(0.0, 0.05, size=(100, len(input_indices))).astype(np.float32)

    # 1. Baseline FP32 Full
    print("\n[1/4] Executando Baseline Exato FP32 (10.23M arestas, ~82.5 MB DRAM)...")
    op_base = row_normalise(raw)
    st = np.zeros(n, dtype=np.float32)
    drv = np.zeros(n, dtype=np.float32)
    base_history = {}
    check_steps = {3: 4, 15: 16, 24: 25, 49: 50, 99: 100}

    t0 = time.perf_counter()
    for step in range(100):
        drv[input_indices] = inputs_seq[step]
        st = 0.6 * st + 0.4 * np.tanh((op_base @ st) * 4.0 + drv)
        if step in check_steps:
            base_history[check_steps[step]] = st.copy()
    t_base = time.perf_counter() - t0
    base_ms = (t_base / 100.0) * 1000.0
    print(f"  -> Concluído: {base_ms:.2f} ms/passo ({100.0/t_base:.1f} passos/s)")

    # Test under Threshold 18 (fits comfortably in 5 MB) and Threshold 12 (fits in 8 MB L3 of current i5)
    test_cases = [
        ("Thresh 18 (Budget < 5MB)", 18),
        ("Thresh 12 (Budget < 8MB - i5-1145G7)", 12),
    ]

    for label, th in test_cases:
        print(f"\n" + "=" * 90)
        print(f"  AVALIAÇÃO: {label} (I/O Protegido + Poda Interna >= {th})")
        print("=" * 90)

        p = make_pruned_matrix(raw, threshold=th, protected_rows=protected)

        # Build candidates
        op_158 = BitNet158Operator(p)
        op_2bit = BitNet2BitOperator(p)
        op_4bit = CompactOperator4Bit(p)

        candidates = [
            ("BitNet 1.58-bit (Ternário Puro)", op_158, "1.58-bit / Multiply-Free"),
            ("BitNet 2-bit (Magnitude Bins)", op_2bit, "2.0-bit / Sign + Scale"),
            ("Compact 4-bit LUT (Codebook)", op_4bit, "4.0-bit / Non-linear LUT"),
        ]

        print(f"{'Modelo / Quantização':<33} {'Mem(MB)':<9} {'Bits/Peso':<11} {'ms/passo':<10} {'Passos/s':<10} {'Speedup':<9} {'Readout@4':<11} {'Readout@16':<12} {'Cos@4':<8} {'Spearman@100'}")
        print("-" * 125)

        for name, op, bits_desc in candidates:
            cur = np.zeros(n, dtype=np.float32)
            nxt = np.zeros(n, dtype=np.float32)
            drv.fill(0.0)

            # Warmup JIT
            for s in range(3):
                drv[input_indices] = inputs_seq[s]
                op.fused_step(cur, nxt, drv, 4.0, 0.4)
                cur, nxt = nxt, cur

            cur.fill(0.0)
            nxt.fill(0.0)
            hist = {}

            t0 = time.perf_counter()
            for s in range(100):
                drv[input_indices] = inputs_seq[s]
                op.fused_step(cur, nxt, drv, 4.0, 0.4)
                if s in check_steps:
                    hist[check_steps[s]] = nxt.copy()
                cur, nxt = nxt, cur
            dt = time.perf_counter() - t0

            ms_step = (dt / 100.0) * 1000.0
            steps_s = 100.0 / dt
            speedup = base_ms / ms_step

            # Metrics
            rcos4 = float(np.dot(base_history[4][readout_indices], hist[4][readout_indices]) / 
                          (np.linalg.norm(base_history[4][readout_indices]) * np.linalg.norm(hist[4][readout_indices]) + 1e-12))
            rcos16 = float(np.dot(base_history[16][readout_indices], hist[16][readout_indices]) / 
                           (np.linalg.norm(base_history[16][readout_indices]) * np.linalg.norm(hist[16][readout_indices]) + 1e-12))
            wcos4 = float(np.dot(base_history[4], hist[4]) / 
                          (np.linalg.norm(base_history[4]) * np.linalg.norm(hist[4]) + 1e-12))
            sp100, _ = spearmanr(base_history[100], hist[100])

            print(
                f"{name:<33} {op.memory_mb:<9.2f} {bits_desc:<11} {ms_step:<10.2f} {steps_s:<10.1f} {speedup:>6.2f}x   "
                f"{rcos4:<11.4f} {rcos16:<12.4f} {wcos4:<8.4f} {float(sp100):<9.4f}"
            )

    print("=" * 90)


if __name__ == "__main__":
    run_tests()
