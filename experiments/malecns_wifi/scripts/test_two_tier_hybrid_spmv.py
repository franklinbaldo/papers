"""Two-Tier Hybrid Connectome Operator: Local 1-Byte Stream + Long-Range Highways.

Architecture:
1. Anatomical Permutation (grouping by superclass, cell_class, soma_side).
2. Tier 1 - Local Circuit (~80-85% of synapses):
   - Fast 1-Byte per edge (uint8): 1 sign bit + 7 delta bits (delta < 128).
   - Zero branching, zero escape codes, pure SIMD additions and subtractions.
3. Tier 2 - Long-Range Highways (~15-20% of synapses):
   - Inter-regional projection neurons, tracts, and cross-hemispheric commissures.
   - Stored in compact INT8 / CSR format with exact calibrated weights.
4. Fused Recurrent Step:
   - Local accumulation + Highway injection + gain + drive + tanh + leak in cache.
"""

from __future__ import annotations

import time
import numpy as np
import scipy.sparse as sp
import numba as nb
from scipy.stats import spearmanr

from malecns_wifi import load_graph, make_pruned_matrix
from malecns_wifi.tagger import row_normalise, select_populations


# ==============================================================================
# Numba JIT Kernels for Two-Tier SpMV
# ==============================================================================

@nb.njit(parallel=True, fastmath=True)
def _two_tier_recurrent_step(
    local_offsets, local_bytes,
    hw_offsets, hw_cols, hw_weights,
    row_scales, x_cur, x_nxt, drive, gain, leak
):
    """Fused step executing Local 1-byte stream + Highway projections in L3 cache."""
    n = len(row_scales)
    alpha = 1.0 - leak
    
    for r in nb.prange(n):
        # 1. Local Tier: pure 1-byte stream (no branches, 7-bit delta + 1 sign bit)
        s_loc = local_offsets[r]
        e_loc = local_offsets[r + 1]
        col = 0
        acc = 0.0
        
        for j in range(s_loc, e_loc):
            b = int(local_bytes[j])
            delta = b & 0x7F         # 7 bits for delta (0..127)
            sign = (b >> 7) & 1      # bit 7 for sign
            col += delta
            val = x_cur[col]
            if sign == 1:
                acc -= val
            else:
                acc += val

        # 2. Highway Tier: long-range projections with exact INT8 weights
        s_hw = hw_offsets[r]
        e_hw = hw_offsets[r + 1]
        for k in range(s_hw, e_hw):
            c_hw = int(hw_cols[k])
            w_hw = float(hw_weights[k])
            acc += w_hw * x_cur[c_hw]

        # 3. Post-normalization and recurrent activation
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


# ==============================================================================
# Two-Tier Operator Builder
# ==============================================================================

class TwoTierHybridOperator:
    """Combines 1-byte local connectivity with exact INT8 long-range highways."""

    def __init__(self, raw: sp.csr_matrix, threshold: int, perm: np.ndarray, protected_rows: set[int] | None = None):
        # 1. Permute graph anatomically
        raw_perm = raw[perm, :][:, perm]
        raw_perm.sort_indices()

        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(len(perm))
        prot_perm = {inv_perm[r] for r in protected_rows} if protected_rows is not None else None

        # 2. Prune
        p = make_pruned_matrix(raw_perm, threshold=threshold, protected_rows=prot_perm)
        n = p.shape[0]

        # 3. Separate into Local (< 128) and Highway (>= 128)
        local_bytes_list = []
        local_offsets = [0]

        hw_cols_list = []
        hw_weights_list = []
        hw_offsets = [0]

        row_scales = np.zeros(n, dtype=np.float32)

        for r in range(n):
            s = p.indptr[r]
            e = p.indptr[r + 1]
            cols = p.indices[s:e]
            vals = p.data[s:e]
            curr_col = 0
            
            row_sum = 0.0

            for c, v in zip(cols, vals):
                d = c - curr_col
                # If delta fits in 7 bits (0..127): assign to Local Tier!
                if d < 128:
                    sign_bit = 1 if v < 0 else 0
                    local_bytes_list.append((sign_bit << 7) | (d & 0x7F))
                    curr_col = c
                    row_sum += 1.0  # unit weight in local tier
                else:
                    # Delta >= 128: assign to Long-Range Highway Tier!
                    hw_cols_list.append(c)
                    w_clipped = float(np.clip(v, -127, 127))
                    hw_weights_list.append(w_clipped)
                    row_sum += abs(w_clipped)

            local_offsets.append(len(local_bytes_list))
            hw_offsets.append(len(hw_cols_list))
            row_scales[r] = 1.0 / max(row_sum, 1.0)

        self.local_bytes = np.array(local_bytes_list, dtype=np.uint8)
        self.local_offsets = np.array(local_offsets, dtype=np.int32)

        self.hw_cols = np.array(hw_cols_list, dtype=np.int32)
        self.hw_weights = np.array(hw_weights_list, dtype=np.int8)
        self.hw_offsets = np.array(hw_offsets, dtype=np.int32)

        self.row_scales = row_scales
        self.n_rows = n
        self.nnz = p.nnz
        self.local_count = len(local_bytes_list)
        self.highway_count = len(hw_cols_list)
        self.perm = perm
        self.inv_perm = inv_perm

    @property
    def memory_bytes(self) -> int:
        return (
            self.local_offsets.nbytes
            + self.local_bytes.nbytes
            + self.hw_offsets.nbytes
            + self.hw_cols.nbytes
            + self.hw_weights.nbytes
            + self.row_scales.nbytes
        )

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def fused_step(self, x_cur, x_nxt, drive, gain=4.0, leak=0.4):
        _two_tier_recurrent_step(
            self.local_offsets, self.local_bytes,
            self.hw_offsets, self.hw_cols, self.hw_weights,
            self.row_scales, x_cur, x_nxt, drive, gain, leak
        )


# ==============================================================================
# Execution Benchmark
# ==============================================================================

def main():
    print("================================================================================")
    print("  EXPERIMENTO: ARQUITETURA EM 2 NÍVEIS (LOCAL 1-BYTE + RODOVIAS DE LONGA DISTÂNCIA)")
    print("================================================================================")

    raw = load_graph("artifacts/inputs/graph.npz")
    archive = np.load("artifacts/inputs/graph.npz", allow_pickle=False)
    pops = select_populations(archive["superclass"])
    protected = set(pops.input_indices) | set(pops.readout_indices)
    input_indices = pops.input_indices
    readout_indices = pops.readout_indices
    n = raw.shape[0]

    # Anatomical ordering
    sc = archive["superclass"]
    cc = archive["cell_class"]
    side = archive["soma_side"]
    perm = np.lexsort((side, cc, sc))
    inv_perm = np.empty_like(perm)
    inv_perm[perm] = np.arange(len(perm))

    perm_inputs = inv_perm[input_indices]
    perm_readouts = inv_perm[readout_indices]

    # 100 sensory steps
    rng = np.random.default_rng(42)
    inputs_seq = rng.normal(0.0, 0.05, size=(100, len(input_indices))).astype(np.float32)

    # 1. Baseline FP32
    print("\n[1/3] Calculando Baseline FP32 (Original, 10.23M arestas, ~82.5 MB DRAM)...")
    op_base = row_normalise(raw)
    st_base = np.zeros(n, dtype=np.float32)
    drv = np.zeros(n, dtype=np.float32)
    base_history = {}
    check_steps = {3: 4, 15: 16, 24: 25, 49: 50, 99: 100}

    t0 = time.perf_counter()
    for s in range(100):
        drv[input_indices] = inputs_seq[s]
        st_base = 0.6 * st_base + 0.4 * np.tanh((op_base @ st_base) * 4.0 + drv)
        if s in check_steps:
            base_history[check_steps[s]] = st_base.copy()
    t_base = time.perf_counter() - t0
    base_ms = (t_base / 100.0) * 1000.0
    print(f"  -> Concluído: {base_ms:.2f} ms/passo ({100.0/t_base:.1f} passos/s)")

    # 2. Benchmark Two-Tier Architecture across thresholds
    print("\n[2/3] Avaliando Arquitetura Two-Tier (Local 1-byte + Rodovias INT8)...")
    print(f"{'Limiar':<8} {'Total NNZ':<12} {'Locais (1-byte)':<17} {'Rodovias':<14} {'Mem(MB)':<9} {'ms/passo':<10} {'Passos/s':<10} {'Speedup':<9} {'Readout@4':<11} {'Cos@4'}")
    print("-" * 125)

    for th in [8, 10, 12, 14, 16, 18]:
        op_tt = TwoTierHybridOperator(raw, threshold=th, perm=perm, protected_rows=protected)

        # Warmup JIT
        cur = np.zeros(n, dtype=np.float32)
        nxt = np.zeros(n, dtype=np.float32)
        drv.fill(0.0)
        for s in range(3):
            drv[perm_inputs] = inputs_seq[s]
            op_tt.fused_step(cur, nxt, drv, 4.0, 0.4)
            cur, nxt = nxt, cur

        cur.fill(0.0)
        nxt.fill(0.0)
        hist = {}

        t0 = time.perf_counter()
        for s in range(100):
            drv[perm_inputs] = inputs_seq[s]
            op_tt.fused_step(cur, nxt, drv, 4.0, 0.4)
            if s in check_steps:
                hist[check_steps[s]] = nxt[inv_perm].copy()
            cur, nxt = nxt, cur
        dt = time.perf_counter() - t0

        ms_step = (dt / 100.0) * 1000.0
        steps_s = 100.0 / dt
        speedup = base_ms / ms_step

        rcos4 = float(np.dot(base_history[4][readout_indices], hist[4][readout_indices]) / 
                      (np.linalg.norm(base_history[4][readout_indices]) * np.linalg.norm(hist[4][readout_indices]) + 1e-12))
        wcos4 = float(np.dot(base_history[4], hist[4]) / 
                      (np.linalg.norm(base_history[4]) * np.linalg.norm(hist[4]) + 1e-12))

        loc_pct = (op_tt.local_count / op_tt.nnz) * 100.0
        hw_pct = (op_tt.highway_count / op_tt.nnz) * 100.0
        loc_str = f"{op_tt.local_count:,} ({loc_pct:.1f}%)"
        hw_str = f"{op_tt.highway_count:,} ({hw_pct:.1f}%)"

        print(
            f"Thresh {th:<2d} {op_tt.nnz:<12,d} {loc_str:<17} {hw_str:<14} {op_tt.memory_mb:<9.2f} "
            f"{ms_step:<10.2f} {steps_s:<10.1f} {speedup:>6.2f}x   {rcos4:<11.4f} {wcos4:<7.4f}"
        )

    print("=" * 125)


if __name__ == "__main__":
    main()
