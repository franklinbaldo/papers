import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from malecns_wifi.fast_spmv import FastSpMV, csr_to_fast_operator, csr_to_torch, fast_sparse_mm


def _make_random_csr(rows=50, cols=50, density=0.1, seed=42):
    rng = np.random.default_rng(seed)
    mat = sp.random(rows, cols, density=density, format="csr", random_state=rng, dtype=np.float32)
    return mat


def test_csr_to_fast_operator_cpu():
    mat = _make_random_csr(100, 100)
    op = csr_to_fast_operator(mat, device="cpu")
    assert hasattr(op, "_T")
    assert op._T is not None
    assert op.shape == (100, 100)
    assert op._T.shape == (100, 100)


def test_fast_sparse_mm_forward_equivalence():
    mat = _make_random_csr(80, 60)
    op = csr_to_fast_operator(mat, device="cpu")
    x = torch.randn(60, 4, dtype=torch.float32)

    y_std = torch.sparse.mm(op, x)
    y_fast = fast_sparse_mm(op, x)

    assert torch.allclose(y_std, y_fast, atol=1e-7)


def test_fast_sparse_mm_backward_gradient_equivalence():
    mat = _make_random_csr(100, 80)
    op = csr_to_fast_operator(mat, device="cpu")

    # 1. Standard backward
    x_std = torch.randn(80, 5, dtype=torch.float32, requires_grad=True)
    out_std = torch.sparse.mm(op, x_std)
    loss_std = (out_std ** 2).sum()
    loss_std.backward()

    # 2. Fast backward with cached transpose
    x_fast = x_std.detach().clone().requires_grad_(True)
    out_fast = fast_sparse_mm(op, x_fast)
    loss_fast = (out_fast ** 2).sum()
    loss_fast.backward()

    assert torch.allclose(out_std, out_fast, atol=1e-7)
    assert torch.allclose(x_std.grad, x_fast.grad, atol=1e-7)


def test_recurrent_reservoir_gradient_equivalence():
    n = 120
    steps = 4
    mat = _make_random_csr(n, n, density=0.08)
    op_std = csr_to_torch(mat, device="cpu")
    op_fast = csr_to_fast_operator(mat, device="cpu")

    u_std = torch.randn(steps, n, dtype=torch.float32, requires_grad=True)
    u_fast = u_std.detach().clone().requires_grad_(True)

    # Reservoir with standard torch.sparse.mm
    state_std = torch.zeros(n, dtype=torch.float32)
    loss_std = 0.0
    for t in range(steps):
        pre = torch.sparse.mm(op_std, state_std[:, None]).squeeze(1) + u_std[t]
        state_std = 0.6 * state_std + 0.4 * torch.tanh(pre)
        loss_std = loss_std + (state_std ** 2).sum()
    loss_std.backward()

    # Reservoir with fast_sparse_mm
    state_fast = torch.zeros(n, dtype=torch.float32)
    loss_fast = 0.0
    for t in range(steps):
        pre = fast_sparse_mm(op_fast, state_fast[:, None]).squeeze(1) + u_fast[t]
        state_fast = 0.6 * state_fast + 0.4 * torch.tanh(pre)
        loss_fast = loss_fast + (state_fast ** 2).sum()
    loss_fast.backward()

    assert torch.allclose(loss_std, loss_fast, atol=1e-6)
    assert torch.allclose(u_std.grad, u_fast.grad, atol=1e-6)
