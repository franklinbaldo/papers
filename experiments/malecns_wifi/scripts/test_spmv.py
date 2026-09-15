import time
import numpy as np
import scipy.sparse as sp
import torch
from malecns_wifi import load_graph
from malecns_wifi.tagger import row_normalise

print("Loading graph...")
m = row_normalise(load_graph("artifacts/inputs/graph.npz")).tocsr().astype(np.float32)
indptr = torch.as_tensor(m.indptr, dtype=torch.int64)
indices = torch.as_tensor(m.indices, dtype=torch.int64)
data = torch.as_tensor(m.data, dtype=torch.float32)
op = torch.sparse_csr_tensor(indptr, indices, data, size=m.shape)

x = torch.randn(m.shape[0], 1, requires_grad=True)

# Warmup
for _ in range(3):
    y = torch.sparse.mm(op, x)

t0 = time.perf_counter()
for _ in range(50):
    y = torch.sparse.mm(op, x)
t1 = time.perf_counter()
print(f"50 SpMV forward steps: {(t1-t0)*1000:.1f}ms ({(t1-t0)/50*1000:.2f}ms per step)")

t0 = time.perf_counter()
loss = y.sum()
loss.backward()
t1 = time.perf_counter()
print(f"1 backward step of SpMV: {(t1-t0)*1000:.1f}ms")
