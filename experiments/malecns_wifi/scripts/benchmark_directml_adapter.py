"""Benchmark the real MaleCNS channel adapter on CPU vs DirectML.

This is an operational benchmark, not scientific evidence.  It uses the exact
ChannelAdapter implementation from the v3 semantic-channel experiment and a
small flavour/readout objective so forward, backward and AdamW are exercised.

The sparse MaleCNS reservoir is intentionally out of scope here; the purpose is
to determine whether Intel UHD-class DirectML acceleration is worthwhile for
the dense trainable modules before wiring a hybrid runner.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from copy import deepcopy
from pathlib import Path

import torch

from local_dense_backend import barrier, resolve_dense_backend
from smoke_coupled_flavour_translation_gpu_v3 import ChannelAdapter


class AdapterProbe(torch.nn.Module):
    def __init__(self, dim: int, rank: int, *, device):
        super().__init__()
        self.adapter = ChannelAdapter(dim, rank=rank, residual_scale=0.1, device=device)
        flavour = torch.randn(dim, dtype=torch.float32, device=device)
        self.flavour = torch.nn.Parameter(flavour / flavour.norm().clamp_min(1e-12))
        self.readout = torch.nn.Linear(dim, 1, device=device)

    def forward(self, values):
        adapted = self.adapter(values)
        flavour = self.flavour / self.flavour.norm().clamp_min(1e-12)
        flavour_logits = 6.0 * (adapted @ flavour)
        readout_logits = self.readout(adapted).squeeze(1)
        return flavour_logits + readout_logits


def _initial_state(dim: int, rank: int, seed: int):
    torch.manual_seed(seed)
    model = AdapterProbe(dim, rank, device=torch.device("cpu"))
    return deepcopy(model.state_dict())


def _run(*, backend_name: str, state, inputs, targets, dim: int, rank: int,
         warmup: int, steps: int, lr: float):
    backend = resolve_dense_backend(backend_name)
    device = backend.device
    model = AdapterProbe(dim, rank, device=torch.device("cpu"))
    model.load_state_dict(state)
    model = model.to(device)
    x = inputs.to(device)
    y = targets.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

    def step():
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, y)
        loss.backward()
        optimizer.step()
        return loss

    last = None
    for _ in range(warmup):
        last = step()
    if last is not None:
        barrier(last)

    start = time.perf_counter()
    for _ in range(steps):
        last = step()
    assert last is not None
    barrier(last)
    elapsed = time.perf_counter() - start

    return {
        "backend": backend.name,
        "device_name": backend.device_name,
        "steps": steps,
        "elapsed_seconds": elapsed,
        "milliseconds_per_step": 1000.0 * elapsed / steps,
        "examples_per_second": steps * len(inputs) / elapsed,
        "final_loss": float(last.detach().cpu()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["cpu", "directml", "auto", "both"], default="both")
    parser.add_argument("--dim", type=int, default=384)
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    torch.manual_seed(args.seed + 1)
    inputs = torch.randn(args.batch, args.dim, dtype=torch.float32)
    targets = torch.randint(0, 2, (args.batch,), dtype=torch.float32)
    state = _initial_state(args.dim, args.rank, args.seed)

    requested = ["cpu", "directml"] if args.device == "both" else [args.device]
    results = []
    failures = []
    for name in requested:
        try:
            results.append(_run(
                backend_name=name,
                state=state,
                inputs=inputs,
                targets=targets,
                dim=args.dim,
                rank=args.rank,
                warmup=args.warmup,
                steps=args.steps,
                lr=args.lr,
            ))
        except Exception as exc:
            failures.append({"backend": name, "error": f"{type(exc).__name__}: {exc}"})
            if args.device != "both":
                raise

    by_name = {row["backend"]: row for row in results}
    speedup = None
    if "cpu" in by_name and "directml" in by_name:
        speedup = by_name["cpu"]["milliseconds_per_step"] / by_name["directml"]["milliseconds_per_step"]

    payload = {
        "schema": "papers/malecns-directml-adapter-benchmark-v1",
        "claim_status": "operational benchmark only; not scientific evidence",
        "python": platform.python_version(),
        "torch": torch.__version__,
        "platform": platform.platform(),
        "dim": args.dim,
        "rank": args.rank,
        "batch": args.batch,
        "warmup": args.warmup,
        "steps": args.steps,
        "lr": args.lr,
        "seed": args.seed,
        "results": results,
        "failures": failures,
        "directml_speedup_over_cpu": speedup,
    }
    text = json.dumps(payload, indent=2) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
