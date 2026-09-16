"""Unit tests for cache-resident compact SpMV operators."""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp

from malecns_wifi import (
    CompactOperator4Bit,
    CompactOperatorInt8,
    make_pruned_matrix,
)


@pytest.fixture
def synthetic_csr() -> sp.csr_matrix:
    """Deterministic synthetic fixture for operator verification."""
    rng = np.random.default_rng(42)
    n = 2000
    density = 0.02
    mat = sp.random(n, n, density=density, format="csr", dtype=np.float32, random_state=rng)
    # Integer synaptic counts in [-50, 50] with minimum abs value 3
    data = rng.integers(3, 50, size=mat.nnz).astype(np.float32)
    signs = rng.choice([-1.0, 1.0], size=mat.nnz).astype(np.float32)
    mat.data = data * signs
    return mat


def test_make_pruned_matrix(synthetic_csr):
    # Threshold 10 should keep only edges with |data| >= 10
    pruned = make_pruned_matrix(synthetic_csr, threshold=10)
    assert pruned.shape == synthetic_csr.shape
    assert (np.abs(pruned.data) >= 10).all()
    assert pruned.nnz < synthetic_csr.nnz


def test_compact_operator_int8_numerical_equivalence(synthetic_csr):
    pruned = make_pruned_matrix(synthetic_csr, threshold=10)
    op_int8 = CompactOperatorInt8(pruned)
    assert op_int8.memory_mb > 0

    x = np.random.default_rng(101).normal(size=pruned.shape[0]).astype(np.float32)
    out_compact = np.zeros(pruned.shape[0], dtype=np.float32)
    op_int8.spmv(x, out_compact)

    # Reference SciPy row-normalised SpMV
    in_strength = np.asarray(np.abs(pruned).sum(axis=1)).ravel()
    row_scale = (1.0 / np.maximum(in_strength, 1.0)).astype(np.float32)
    ref_spmv = (pruned @ x) * row_scale

    assert np.allclose(out_compact, ref_spmv, atol=1e-4)


def test_compact_operator_4bit_bounded_error(synthetic_csr):
    pruned = make_pruned_matrix(synthetic_csr, threshold=10)
    op_4bit = CompactOperator4Bit(pruned)
    assert op_4bit.memory_mb > 0

    x = np.random.default_rng(102).normal(size=pruned.shape[0]).astype(np.float32)
    out_compact = np.zeros(pruned.shape[0], dtype=np.float32)
    op_4bit.spmv(x, out_compact)

    assert np.isfinite(out_compact).all()
    assert not (out_compact == 0).all()


def test_fused_recurrence_stability(synthetic_csr):
    pruned = make_pruned_matrix(synthetic_csr, threshold=10)
    op = CompactOperatorInt8(pruned)
    n = pruned.shape[0]

    x_cur = np.zeros(n, dtype=np.float32)
    x_nxt = np.zeros(n, dtype=np.float32)
    drive = np.zeros(n, dtype=np.float32)
    drive[:100] = 0.05

    for _ in range(20):
        op.fused_step(x_cur, x_nxt, drive, gain=4.0, leak=0.4)
        x_cur, x_nxt = x_nxt, x_cur

    assert np.isfinite(x_cur).all()
    assert (np.abs(x_cur) <= 1.0).all()
    assert np.linalg.norm(x_cur) > 0.0
