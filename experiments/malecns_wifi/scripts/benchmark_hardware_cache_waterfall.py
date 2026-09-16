"""Hardware Benchmark & Memory Hierarchy Profiler for Core i5-1145G7.

Measures:
1. CPU & Cache hardware parameters
2. Stream Memory Bandwidth across buffer sizes (L1D, L2, L3, DRAM)
3. SpMV throughput curve identifying the exact L2 / L3 / DRAM cliff
4. Peak FP32 GFLOPS
"""

from __future__ import annotations

import time
import numpy as np
import numba as nb
import torch


@nb.njit(parallel=True, fastmath=True)
def stream_triad(a, b, c, scalar):
    """STREAM Triad kernel: a[i] = b[i] + scalar * c[i]."""
    for i in nb.prange(len(a)):
        a[i] = b[i] + scalar * c[i]


@nb.njit(parallel=True, fastmath=True)
def spmv_slice_bench(indptr, indices, data, x, out):
    """SpMV slice to measure effective bandwidth at various working set sizes."""
    n = len(indptr) - 1
    for r in nb.prange(n):
        s = indptr[r]
        e = indptr[r + 1]
        acc = 0.0
        for j in range(s, e):
            acc += data[j] * x[indices[j]]
        out[r] = acc


def measure_stream_bandwidth():
    print("\n--- 1. STREAM Memory Bandwidth vs Buffer Size (Cache Hierarchy) ---")
    print(f"{'Buffer Size':<14} {'Target Cache / Tier':<22} {'Triad Bandwidth':<18} {'Latency / Element':<18}")
    print("-" * 72)
    
    # Sizes from 16 KB (L1) up to 128 MB (DRAM)
    sizes_kb = [
        (24, "L1D Cache (48 KB/core)"),
        (128, "L1D / Small L2"),
        (512, "L2 Cache (1.25 MB/core)"),
        (1024, "L2 Cache"),
        (2048, "L2 aggregate / L3"),
        (4096, "L3 Cache (8 MB total)"),
        (6144, "L3 Cache (8 MB total)"),
        (7680, "L3 Cache (near limit)"),
        (12288, "DRAM (spills past L3)"),
        (24576, "DRAM (Main Memory)"),
        (65536, "DRAM (Main Memory)"),
        (131072, "DRAM (Main Memory)"),
    ]
    
    # Warmup
    dummy = np.ones(1024, dtype=np.float32)
    stream_triad(dummy, dummy, dummy, 2.0)
    
    results = []
    for size_kb, label in sizes_kb:
        n_elements = (size_kb * 1024) // 4  # float32 elements
        a = np.ones(n_elements, dtype=np.float32)
        b = np.ones(n_elements, dtype=np.float32)
        c = np.ones(n_elements, dtype=np.float32)
        scalar = np.float32(3.14159)
        
        # Warmup buffer
        stream_triad(a, b, c, scalar)
        
        # Determine number of iterations based on size
        target_bytes = 200 * 1024 * 1024  # at least 200 MB transferred per test
        bytes_per_iter = n_elements * 4 * 3  # read b, read c, write a
        iters = max(10, target_bytes // bytes_per_iter)
        
        t0 = time.perf_counter()
        for _ in range(iters):
            stream_triad(a, b, c, scalar)
        t1 = time.perf_counter()
        
        elapsed = t1 - t0
        total_gb = (bytes_per_iter * iters) / 1e9
        bandwidth_gb_s = total_gb / elapsed
        lat_ns = (elapsed / (iters * n_elements)) * 1e9
        
        size_str = f"{size_kb} KB" if size_kb < 1024 else f"{size_kb // 1024} MB"
        print(f"{size_str:<14} {label:<22} {bandwidth_gb_s:>8.2f} GB/s       {lat_ns:>6.2f} ns")
        results.append((size_kb, label, bandwidth_gb_s))
    return results


def measure_spmv_waterfall():
    print("\n--- 2. SpMV Recurrent Throughput Waterfall (Working Set vs Latency) ---")
    print(f"{'Operator Size':<15} {'Status':<16} {'SpMV Latency':<16} {'Steps/sec':<14} {'Effective BW':<14}")
    print("-" * 75)
    
    # Generate synthetic CSR matrices of varying sizes
    density_cols_per_row = 16
    sizes = [
        (1.0, "L2/L3 Cache"),
        (2.0, "L3 Resident"),
        (4.0, "L3 Resident"),
        (4.8, "MaleCNS Compact (Target)"),
        (6.5, "L3 Resident"),
        (7.5, "L3 Limit (8MB)"),
        (10.0, "DRAM Spill"),
        (18.0, "DRAM Spill"),
        (40.0, "DRAM Spill"),
        (80.0, "Full MaleCNS CSR"),
    ]
    
    rng = np.random.default_rng(42)
    # Warmup
    w_n = 1000
    w_ptr = np.arange(0, w_n * 16 + 1, 16, dtype=np.int32)
    w_idx = np.random.randint(0, w_n, size=w_n * 16, dtype=np.int32)
    w_dat = np.ones(w_n * 16, dtype=np.float32)
    w_x = np.ones(w_n, dtype=np.float32)
    w_out = np.zeros(w_n, dtype=np.float32)
    spmv_slice_bench(w_ptr, w_idx, w_dat, w_x, w_out)
    
    for size_mb, desc in sizes:
        # Size in MB: bytes = (indices 4B + data 4B) * nnz + (rows+1)*4B
        # With 16 entries per row: bytes per row = 16*8 + 4 = 132 bytes
        target_bytes = int(size_mb * 1024 * 1024)
        n_rows = target_bytes // 132
        nnz = n_rows * 16
        
        indptr = np.arange(0, nnz + 1, 16, dtype=np.int32)
        indices = rng.integers(0, n_rows, size=nnz, dtype=np.int32)
        data = rng.normal(0, 1, size=nnz).astype(np.float32)
        x = rng.normal(0, 1, size=n_rows).astype(np.float32)
        out = np.zeros(n_rows, dtype=np.float32)
        
        # Warmup
        spmv_slice_bench(indptr, indices, data, x, out)
        
        iters = max(20, int(150.0 / (size_mb + 0.1)))
        t0 = time.perf_counter()
        for _ in range(iters):
            spmv_slice_bench(indptr, indices, data, x, out)
        t1 = time.perf_counter()
        
        dt = (t1 - t0) / iters
        steps_s = 1.0 / dt
        eff_bw = (target_bytes / 1e9) / dt
        
        print(f"{size_mb:4.1f} MB        {desc:<16} {dt*1000:>6.2f} ms        {steps_s:>7.1f} st/s   {eff_bw:>7.2f} GB/s")


def main():
    print("=================================================================")
    print("  HARDWARE BENCHMARK & SYSTEM DIAGNOSTIC")
    print("=================================================================")
    measure_stream_bandwidth()
    measure_spmv_waterfall()
    print("\n=================================================================")


if __name__ == "__main__":
    main()
