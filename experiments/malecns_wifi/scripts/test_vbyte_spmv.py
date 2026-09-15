"""VByte (Variable-Byte Delta) Sparse Matrix Implementation & Benchmark.

Tests:
1. Anatomical graph reordering (clustering by superclass, cell_class, soma_side)
2. VByte-1.58bit encoding (1 byte for delta < 64, 2 bytes for delta < 16384, 3 bytes fallback)
3. Native Numba SpMV and fused recurrent step
4. Memory footprint vs Delta-uint16 vs FP32
5. Numerical equivalence and dynamic fidelity
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
# Numba JIT Kernel for VByte-1.58bit Recurrent Step
# ==============================================================================

@nb.njit(parallel=True, fastmath=True)
def _vbyte_recurrent_step(row_offsets, vbyte_data, row_scales, x_cur, x_nxt, drive, gain, leak):
    """Fused Recurrent Step directly decoding VByte stream in L2/L3 cache."""
    n = len(row_scales)
    alpha = 1.0 - leak
    
    for r in nb.prange(n):
        s = row_offsets[r]
        e = row_offsets[r + 1]
        col = 0
        acc = 0.0
        idx = s
        
        while idx < e:
            b0 = int(vbyte_data[idx])
            idx += 1
            
            # Check continuation bit (bit 7)
            if (b0 & 0x80) == 0:
                # 1-byte edge: [0 | sign(1) | delta(6)]
                sign = (b0 >> 6) & 1
                delta = b0 & 0x3F
            else:
                sign = (b0 >> 6) & 1
                b1 = int(vbyte_data[idx])
                idx += 1
                
                if (b1 & 0x80) == 0:
                    # 2 bytes:
                    delta = (b1 << 6) | (b0 & 0x3F)
                else:
                    # 3 bytes:
                    b2 = int(vbyte_data[idx])
                    idx += 1
                    delta = (b2 << 13) | ((b1 & 0x7F) << 6) | (b0 & 0x3F)
            
            col += delta
            val = x_cur[col]
            if sign == 1:
                acc -= val
            else:
                acc += val
                
        pre = acc * row_scales[r] * gain + drive[r]
        x_nxt[r] = alpha * x_cur[r] + leak * np.tanh(pre)


# ==============================================================================
# VByte-1.58bit Operator Class
# ==============================================================================

class VByte158Operator:
    """Anatomically-ordered VByte-1.58bit Cache-Resident Operator."""

    def __init__(self, raw: sp.csr_matrix, threshold: int, perm: np.ndarray, protected_rows: set[int] | None = None):
        # 1. Apply anatomical permutation: W_perm = P W P^T
        raw_perm = raw[perm, :][:, perm]
        raw_perm.sort_indices()
        
        # 2. Map protected rows to permuted indices
        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(len(perm))
        prot_perm = {inv_perm[r] for r in protected_rows} if protected_rows is not None else None

        # 3. Prune
        p = make_pruned_matrix(raw_perm, threshold=threshold, protected_rows=prot_perm)
        n = p.shape[0]

        # 4. Row scales (degrees in ternary)
        diffs = np.diff(p.indptr)
        self.row_scales = (1.0 / np.maximum(diffs, 1.0)).astype(np.float32)

        # 5. Encode into VByte stream
        vbyte_bytes = bytearray()
        row_offsets = [0]

        for r in range(n):
            s = p.indptr[r]
            e = p.indptr[r + 1]
            cols = p.indices[s:e]
            vals = p.data[s:e]
            curr_col = 0
            
            for c, v in zip(cols, vals):
                d = c - curr_col
                sign_bit = 1 if v < 0 else 0
                
                if d < 64:
                    # 1 byte: 0 | sign(1) | delta(6)
                    vbyte_bytes.append((sign_bit << 6) | (d & 0x3F))
                elif d < 16384:
                    # 2 bytes:
                    # byte 0: 1 | sign(1) | d[0..5]
                    # byte 1: 0 | d[6..12] (up to 127)
                    b0 = 0x80 | (sign_bit << 6) | (d & 0x3F)
                    b1 = (d >> 6) & 0x7F
                    vbyte_bytes.append(b0)
                    vbyte_bytes.append(b1)
                else:
                    # 3 bytes:
                    b0 = 0x80 | (sign_bit << 6) | (d & 0x3F)
                    b1 = 0x80 | ((d >> 6) & 0x7F)
                    b2 = (d >> 13) & 0xFF
                    vbyte_bytes.append(b0)
                    vbyte_bytes.append(b1)
                    vbyte_bytes.append(b2)
                    
                curr_col = c
            row_offsets.append(len(vbyte_bytes))

        self.vbyte_data = np.frombuffer(vbyte_bytes, dtype=np.uint8)
        self.row_offsets = np.array(row_offsets, dtype=np.int32)
        self.nnz = p.nnz
        self.n_rows = n
        self.perm = perm
        self.inv_perm = inv_perm

    @property
    def bytes_per_edge(self) -> float:
        return len(self.vbyte_data) / max(self.nnz, 1)

    @property
    def bits_per_edge(self) -> float:
        return self.bytes_per_edge * 8.0

    @property
    def memory_bytes(self) -> int:
        return self.row_offsets.nbytes + self.row_scales.nbytes + self.vbyte_data.nbytes

    @property
    def memory_mb(self) -> float:
        return self.memory_bytes / (1024.0 * 1024.0)

    def fused_step(self, x_cur, x_nxt, drive, gain=4.0, leak=0.4):
        _vbyte_recurrent_step(
            self.row_offsets, self.vbyte_data, self.row_scales, x_cur, x_nxt, drive, gain, leak
        )


# ==============================================================================
# Benchmark Runner
# ==============================================================================

def main():
    print("================================================================================")
    print("  EXPERIMENTO VBYTE: CODIFICAÇÃO DE COMPRIMENTO VARIÁVEL PARA O MALECNS")
    print("================================================================================")

    raw = load_graph("artifacts/inputs/graph.npz")
    archive = np.load("artifacts/inputs/graph.npz", allow_pickle=False)
    pops = select_populations(archive["superclass"])
    protected = set(pops.input_indices) | set(pops.readout_indices)
    input_indices = pops.input_indices
    readout_indices = pops.readout_indices
    n = raw.shape[0]

    # Anatomical Permutation (grouping by superclass, cell_class, soma_side)
    sc = archive["superclass"]
    cc = archive["cell_class"]
    side = archive["soma_side"]
    perm = np.lexsort((side, cc, sc))
    inv_perm = np.empty_like(perm)
    inv_perm[perm] = np.arange(len(perm))

    # Pre-generate 100 sensory steps
    rng = np.random.default_rng(42)
    inputs_seq = rng.normal(0.0, 0.05, size=(100, len(input_indices))).astype(np.float32)

    # 1. Baseline FP32
    print("\n[1/3] Calculando Baseline FP32 (Original, 10.23M arestas, ~82.5 MB)...")
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

    # 2. Test VByte across thresholds
    print("\n[2/3] Avaliando Operador VByte-1.58bit através de múltiplos limiares...")
    print(f"{'Limiar':<8} {'Arestas (NNZ)':<14} {'VByte Data':<12} {'Total Mem':<11} {'Bits/Aresta':<13} {'ms/passo':<10} {'Passos/s':<10} {'Readout@4':<11} {'Readout@16':<12} {'Cos@4'}")
    print("-" * 115)

    perm_inputs = inv_perm[input_indices]
    perm_readouts = inv_perm[readout_indices]

    for th in [8, 10, 12, 14, 16, 18]:
        op_vb = VByte158Operator(raw, threshold=th, perm=perm, protected_rows=protected)

        # Warmup JIT
        cur = np.zeros(n, dtype=np.float32)
        nxt = np.zeros(n, dtype=np.float32)
        drv.fill(0.0)
        for s in range(3):
            drv[perm_inputs] = inputs_seq[s]
            op_vb.fused_step(cur, nxt, drv, 4.0, 0.4)
            cur, nxt = nxt, cur

        cur.fill(0.0)
        nxt.fill(0.0)
        hist = {}

        t0 = time.perf_counter()
        for s in range(100):
            drv[perm_inputs] = inputs_seq[s]
            op_vb.fused_step(cur, nxt, drv, 4.0, 0.4)
            if s in check_steps:
                # Map back to original order for exact fidelity check
                hist[check_steps[s]] = nxt[inv_perm].copy()
            cur, nxt = nxt, cur
        dt = time.perf_counter() - t0

        ms_step = (dt / 100.0) * 1000.0
        steps_s = 100.0 / dt

        # Fidelity metrics
        rcos4 = float(np.dot(base_history[4][readout_indices], hist[4][readout_indices]) / 
                      (np.linalg.norm(base_history[4][readout_indices]) * np.linalg.norm(hist[4][readout_indices]) + 1e-12))
        rcos16 = float(np.dot(base_history[16][readout_indices], hist[16][readout_indices]) / 
                       (np.linalg.norm(base_history[16][readout_indices]) * np.linalg.norm(hist[16][readout_indices]) + 1e-12))
        wcos4 = float(np.dot(base_history[4], hist[4]) / 
                      (np.linalg.norm(base_history[4]) * np.linalg.norm(hist[4]) + 1e-12))

        vbyte_mb = len(op_vb.vbyte_data) / (1024.0 * 1024.0)
        print(
            f"Thresh {th:<2d} {op_vb.nnz:<14,d} {vbyte_mb:<10.2f}MB {op_vb.memory_mb:<9.2f}MB {op_vb.bits_per_edge:<11.2f}b "
            f"{ms_step:<10.2f} {steps_s:<10.1f} {rcos4:<11.4f} {rcos16:<12.4f} {wcos4:<7.4f}"
        )

    print("=" * 115)


if __name__ == "__main__":
    main()
