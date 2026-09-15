import time
import numpy as np
import scipy.sparse as sp
import torch
from malecns_wifi import load_graph
from malecns_wifi.tagger import row_normalise

print("Loading graph...")
m = row_normalise(load_graph("artifacts/inputs/graph.npz")).tocsr().astype(np.float32)
m_T = m.transpose().tocsr().astype(np.float32)

op = torch.sparse_csr_tensor(
    torch.as_tensor(m.indptr, dtype=torch.int64),
    torch.as_tensor(m.indices, dtype=torch.int64),
    torch.as_tensor(m.data, dtype=torch.float32),
    size=m.shape,
)

op_T = torch.sparse_csr_tensor(
    torch.as_tensor(m_T.indptr, dtype=torch.int64),
    torch.as_tensor(m_T.indices, dtype=torch.int64),
    torch.as_tensor(m_T.data, dtype=torch.float32),
    size=m_T.shape,
)

class FastSpMV(torch.autograd.Function):
    @staticmethod
    def forward(ctx, op, op_T, x):
        ctx.op_T = op_T
        return torch.sparse.mm(op, x)

    @staticmethod
    def backward(ctx, grad_out):
        grad_x = torch.sparse.mm(ctx.op_T, grad_out)
        return None, None, grad_x

def fast_spmv(op, op_T, x):
    return FastSpMV.apply(op, op_T, x)

# Test numerical equality of gradients
x1 = torch.randn(m.shape[0], 1, requires_grad=True)
x2 = x1.clone().detach().requires_grad_(True)

y1 = torch.sparse.mm(op, x1)
y1.sum().backward()

y2 = fast_spmv(op, op_T, x2)
y2.sum().backward()

diff = (x1.grad - x2.grad).abs().max().item()
print(f"Gradient difference between PyTorch and FastSpMV: {diff:.6e}")

# Benchmark 50 steps backward
x_bench = torch.randn(m.shape[0], 1, requires_grad=True)
t0 = time.perf_counter()
state = x_bench
for _ in range(50):
    state = fast_spmv(op, op_T, state)
loss = state.sum()
t1 = time.perf_counter()
loss.backward()
t2 = time.perf_counter()

print(f"50 steps forward: {(t1-t0)*1000:.1f}ms")
print(f"50 steps backward: {(t2-t1)*1000:.1f}ms ({(t2-t1)/50*1000:.2f}ms per step)")
