"""Microbenchmark for PyTorch CPU vs DirectML on Intel UHD Graphics 630."""

from __future__ import annotations

import time
import torch
import torch_directml as dml

print("=" * 60)
print(f"DirectML Device: {dml.device_name(0)}")
print("=" * 60)

cpu_dev = torch.device("cpu")
dml_dev = dml.device(0)

# -------------------------------------------------------------
# 1. Synthetic Matmul + Backward
# -------------------------------------------------------------
print("\n[Level 1] Synthetic Matmul + Backward (1024x1024, 200 iterations)")

def bench_matmul(device, name):
    x = torch.randn(1024, 1024, device=device, requires_grad=True)
    w = torch.randn(1024, 1024, device=device, requires_grad=True)
    # warmup
    for _ in range(10):
        y = (x @ w).sum()
        y.backward()
        x.grad = None
        w.grad = None

    t0 = time.perf_counter()
    for _ in range(200):
        y = (x @ w).sum()
        y.backward()
        x.grad = None
        w.grad = None
    t1 = time.perf_counter()
    dt = t1 - t0
    print(f"  {name:12s}: {dt*1000:.1f}ms ({200/dt:.1f} iters/s)")
    return dt

t_cpu_1 = bench_matmul(cpu_dev, "PyTorch CPU")
t_dml_1 = bench_matmul(dml_dev, "DirectML GPU")
print(f"  Level 1 Speedup (DML vs CPU): {t_cpu_1 / t_dml_1:.2f}x")

# -------------------------------------------------------------
# 2. Real Adapter: A(x) = unit(x + 0.1 * up(tanh(down(unit(x)))))
# -------------------------------------------------------------
print("\n[Level 2] Real Channel Adapter Forward + Backward + Optimizer step")
# Adapter details: dim=384, rank=16, batch size = sequence of tokens / chunks (e.g., 50 chunks, dim 384)
class ChannelAdapter(torch.nn.Module):
    def __init__(self, dim: int = 384, rank: int = 16):
        super().__init__()
        self.down = torch.nn.Linear(dim, rank, bias=False)
        self.up = torch.nn.Linear(rank, dim, bias=False)
        torch.nn.init.zeros_(self.up.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        u = x / torch.linalg.vector_norm(x, dim=-1, keepdim=True).clamp_min(1e-12)
        delta = self.up(torch.tanh(self.down(u)))
        out = x + 0.1 * delta
        return out / torch.linalg.vector_norm(out, dim=-1, keepdim=True).clamp_min(1e-12)

def bench_adapter(device, name, batch_size=64, num_steps=500):
    model = ChannelAdapter(dim=384, rank=16).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    x = torch.randn(batch_size, 384, device=device)
    target = torch.randn(batch_size, 384, device=device)

    # warmup
    for _ in range(20):
        optimizer.zero_grad()
        out = model(x)
        loss = ((out - target) ** 2).mean()
        loss.backward()
        optimizer.step()

    t0 = time.perf_counter()
    for _ in range(num_steps):
        optimizer.zero_grad()
        out = model(x)
        loss = ((out - target) ** 2).mean()
        loss.backward()
        optimizer.step()
    t1 = time.perf_counter()
    dt = t1 - t0
    print(f"  {name:12s} (batch={batch_size}, steps={num_steps}): {dt*1000:.1f}ms ({num_steps/dt:.1f} steps/s)")
    return dt

t_cpu_ad_64 = bench_adapter(cpu_dev, "PyTorch CPU", batch_size=64)
t_dml_ad_64 = bench_adapter(dml_dev, "DirectML GPU", batch_size=64)
print(f"  Adapter (batch 64) Speedup: {t_cpu_ad_64 / t_dml_ad_64:.2f}x")

t_cpu_ad_256 = bench_adapter(cpu_dev, "PyTorch CPU", batch_size=256)
t_dml_ad_256 = bench_adapter(dml_dev, "DirectML GPU", batch_size=256)
print(f"  Adapter (batch 256) Speedup: {t_cpu_ad_256 / t_dml_ad_256:.2f}x")
