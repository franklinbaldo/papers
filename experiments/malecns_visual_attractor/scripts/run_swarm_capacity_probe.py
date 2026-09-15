from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import load_screen_geometry
from swarm_transport import apply_transport, compile_static_transport, sample_swarm_poses, to_torch
from visual_attractor import load_graph, load_interface


def _torch():
    import torch
    return torch


def _idx(values, device):
    torch = _torch()
    return torch.from_numpy(np.asarray(values, dtype=np.int64)).to(device)


def _ensure_visible(poses, geometry, *, width, height, physical_width, ambient, seed):
    """Compile a batch, replacing any invisible pose until all see some TV."""
    rng = np.random.default_rng(seed)
    poses = np.asarray(poses, dtype=np.float64).copy()
    resampled = 0
    for attempt in range(8):
        transport = compile_static_transport(
            receptor_x=geometry.x,
            receptor_y=geometry.y,
            resolved=geometry.resolved,
            poses=poses,
            width=width,
            height=height,
            physical_width=physical_width,
            ambient=ambient,
        )
        bad = np.flatnonzero(transport.visible_mass <= 0)
        if not len(bad):
            return transport, resampled
        resampled += int(len(bad))
        x = rng.uniform(0.35, 1.15, size=len(bad))
        y = rng.uniform(-0.35, 0.35, size=len(bad))
        gaze = np.arctan2(-y, -x)
        # progressively narrow the heading offset; final attempts gaze directly at TV
        span = max(0.0, np.deg2rad(25.0 - 4.0 * attempt))
        heading = gaze + rng.uniform(-span, span, size=len(bad))
        poses[bad] = np.stack((x, y, heading), axis=1)
    raise RuntimeError(f"unable to sample fully visible batch after resampling; visible={transport.visible_mass.tolist()}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--graph", type=Path, required=True)
    p.add_argument("--interface", type=Path, required=True)
    p.add_argument("--screen-geometry", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--device", default="cuda")
    p.add_argument("--swarm-size", type=int, default=4096)
    p.add_argument("--microbatch-size", type=int, default=512)
    p.add_argument("--steps", type=int, default=4)
    p.add_argument("--screen-width-px", type=int, default=64)
    p.add_argument("--screen-height-px", type=int, default=36)
    p.add_argument("--physical-width", type=float, default=0.42)
    p.add_argument("--ambient", type=float, default=0.08)
    p.add_argument("--seed", type=int, default=20260915)
    p.add_argument("--spectral-scale", type=float, default=3776.27)
    p.add_argument("--gain", type=float, default=1.0)
    p.add_argument("--leak", type=float, default=0.2)
    p.add_argument("--visual-scale", type=float, default=0.5)
    args = p.parse_args()

    if args.swarm_size < 1 or args.microbatch_size < 1 or args.swarm_size % args.microbatch_size:
        p.error("swarm-size must be a positive multiple of microbatch-size")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    torch = _torch()
    if args.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()

    graph = load_graph(args.graph)
    interface = load_interface(args.interface)
    geometry = load_screen_geometry(args.screen_geometry)
    sparse = scipy_csr_to_torch(graph, device=args.device)
    visual_idx = _idx(interface.visual_indices, args.device)
    desc = torch.unique(torch.cat((_idx(interface.descending_left, args.device), _idx(interface.descending_right, args.device))))

    batches = args.swarm_size // args.microbatch_size
    rows = []
    total_resampled = 0
    all_visible_min = float("inf")
    for bi in range(batches):
        b0 = time.perf_counter()
        poses = sample_swarm_poses(
            flies=args.microbatch_size,
            seed=args.seed + bi,
            max_lateral=0.35,
            max_heading_offset_deg=25.0,
        )
        transport, resampled = _ensure_visible(
            poses,
            geometry,
            width=args.screen_width_px,
            height=args.screen_height_px,
            physical_width=args.physical_width,
            ambient=args.ambient,
            seed=args.seed + 10000 + bi,
        )
        total_resampled += resampled
        all_visible_min = min(all_visible_min, float(transport.visible_mass.min()))
        matrix, baseline = to_torch(transport, device=args.device)

        flies = args.microbatch_size
        receiver_state = torch.zeros((graph.shape[0], 2 * flies), dtype=torch.float32, device=args.device)
        yy, xx = torch.meshgrid(
            torch.linspace(-1.0, 1.0, args.screen_height_px, device=args.device),
            torch.linspace(-1.0, 1.0, args.screen_width_px, device=args.device),
            indexing="ij",
        )
        probe_frame = torch.clamp(0.15 + 0.12 * torch.sin(8.0 * xx + 3.0 * yy), 0.0, 1.0)
        uniform = torch.full_like(probe_frame, float(probe_frame.mean()))
        learned_retina = apply_transport(probe_frame, matrix, baseline, flies=flies, receptors=transport.receptors)
        uniform_retina = apply_transport(uniform, matrix, baseline, flies=flies, receptors=transport.receptors)
        external = torch.cat((learned_retina, uniform_retina), dim=1)

        with torch.no_grad():
            for _ in range(args.steps):
                recurrent = torch.sparse.mm(sparse, receiver_state) / float(args.spectral_scale)
                pre = float(args.gain) * recurrent
                pre.index_add_(0, visual_idx, float(args.visual_scale) * external)
                receiver_state = (1.0 - float(args.leak)) * receiver_state + float(args.leak) * torch.tanh(pre)
        desc_exc = receiver_state.index_select(0, desc).abs().mean(dim=0)
        delta = float((desc_exc[:flies] - desc_exc[flies:]).mean().cpu())
        peak = int(torch.cuda.max_memory_allocated()) if args.device.startswith("cuda") else 0
        row = {
            "batch": bi,
            "flies": flies,
            "resampled": resampled,
            "min_visible_mass": float(transport.visible_mass.min()),
            "mean_visible_mass": float(transport.visible_mass.mean()),
            "probe_delta": delta,
            "peak_cuda_bytes": peak,
            "elapsed_s": time.perf_counter() - b0,
        }
        rows.append(row)
        print(json.dumps({"event": "swarm_capacity_batch", **row}, sort_keys=True), flush=True)
        del receiver_state, matrix, baseline, external, learned_retina, uniform_retina
        if args.device.startswith("cuda"):
            torch.cuda.empty_cache()

    peak = int(torch.cuda.max_memory_allocated()) if args.device.startswith("cuda") else 0
    total = {
        "experiment": "malecns-swarm-capacity-probe-v1",
        "swarm_size": args.swarm_size,
        "microbatch_size": args.microbatch_size,
        "microbatches": batches,
        "steps_per_microbatch": args.steps,
        "all_visible": True,
        "min_visible_mass": all_visible_min,
        "total_resampled": total_resampled,
        "peak_cuda_bytes": peak,
        "peak_cuda_gib": peak / (1024 ** 3),
        "elapsed_s": time.perf_counter() - t0,
        "batches": rows,
    }
    (args.output_dir / "swarm-capacity-summary.json").write_text(json.dumps(total, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"event": "swarm_capacity_complete", **{k: total[k] for k in ("swarm_size", "microbatch_size", "peak_cuda_gib", "total_resampled", "elapsed_s")}}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
