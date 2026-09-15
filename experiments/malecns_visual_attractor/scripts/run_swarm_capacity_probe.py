from __future__ import annotations

import argparse
import json
import threading
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


class Telemetry:
    def __init__(self, *, output_dir: Path, torch, device: str, interval_s: float = 15.0):
        self.output_dir = output_dir
        self.torch = torch
        self.device = device
        self.interval_s = interval_s
        self.started = time.perf_counter()
        self.stage = "startup"
        self.batch = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._heartbeat, daemon=True)
        self.path = output_dir / "telemetry.jsonl"
        self.path.write_text("", encoding="utf-8")

    def _cuda(self):
        if not self.device.startswith("cuda"):
            return {"cuda_allocated_gib": 0.0, "cuda_reserved_gib": 0.0, "cuda_peak_gib": 0.0}
        g = 1024 ** 3
        return {
            "cuda_allocated_gib": self.torch.cuda.memory_allocated() / g,
            "cuda_reserved_gib": self.torch.cuda.memory_reserved() / g,
            "cuda_peak_gib": self.torch.cuda.max_memory_allocated() / g,
        }

    def emit(self, event: str, **extra):
        row = {
            "event": event,
            "stage": self.stage,
            "batch": self.batch,
            "elapsed_s": round(time.perf_counter() - self.started, 3),
            **self._cuda(),
            **extra,
        }
        line = json.dumps(row, sort_keys=True)
        print(line, flush=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()

    def set_stage(self, stage: str, *, batch=None, **extra):
        self.stage = stage
        self.batch = batch
        self.emit("stage", **extra)

    def _heartbeat(self):
        while not self._stop.wait(self.interval_s):
            self.emit("heartbeat")

    def start(self):
        self.emit("probe_start")
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=2.0)
        self.emit("probe_stop")


def _ensure_visible(poses, geometry, *, width, height, physical_width, ambient, seed, telemetry: Telemetry):
    rng = np.random.default_rng(seed)
    poses = np.asarray(poses, dtype=np.float64).copy()
    resampled = 0
    for attempt in range(8):
        telemetry.emit("optics_compile_start", attempt=attempt, flies=len(poses))
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
        telemetry.emit(
            "optics_compile_done",
            attempt=attempt,
            invisible=int(len(bad)),
            min_visible_mass=float(transport.visible_mass.min()),
            mean_visible_mass=float(transport.visible_mass.mean()),
        )
        if not len(bad):
            return transport, resampled
        resampled += int(len(bad))
        x = rng.uniform(0.35, 1.15, size=len(bad))
        y = rng.uniform(-0.35, 0.35, size=len(bad))
        gaze = np.arctan2(-y, -x)
        span = max(0.0, np.deg2rad(25.0 - 4.0 * attempt))
        heading = gaze + rng.uniform(-span, span, size=len(bad))
        poses[bad] = np.stack((x, y, heading), axis=1)
        telemetry.emit("poses_resampled", attempt=attempt, count=int(len(bad)), cumulative=resampled)
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
    p.add_argument("--heartbeat-seconds", type=float, default=15.0)
    args = p.parse_args()

    if args.swarm_size < 1 or args.microbatch_size < 1 or args.swarm_size % args.microbatch_size:
        p.error("swarm-size must be a positive multiple of microbatch-size")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    torch = _torch()
    if args.device.startswith("cuda"):
        torch.cuda.reset_peak_memory_stats()

    telemetry = Telemetry(
        output_dir=args.output_dir,
        torch=torch,
        device=args.device,
        interval_s=args.heartbeat_seconds,
    )
    telemetry.start()
    try:
        telemetry.set_stage("load_graph")
        graph = load_graph(args.graph)
        telemetry.emit("graph_loaded", neurons=int(graph.shape[0]), edges=int(graph.nnz))

        telemetry.set_stage("load_interface")
        interface = load_interface(args.interface)
        geometry = load_screen_geometry(args.screen_geometry)
        telemetry.emit("interface_loaded", visual_receptors=int(len(interface.visual_indices)))

        telemetry.set_stage("graph_to_gpu")
        sparse = scipy_csr_to_torch(graph, device=args.device)
        visual_idx = _idx(interface.visual_indices, args.device)
        desc = torch.unique(torch.cat((_idx(interface.descending_left, args.device), _idx(interface.descending_right, args.device))))
        telemetry.emit("graph_on_gpu", descending=int(desc.numel()))

        batches = args.swarm_size // args.microbatch_size
        rows = []
        total_resampled = 0
        all_visible_min = float("inf")
        for bi in range(batches):
            b0 = time.perf_counter()
            telemetry.set_stage("sample_poses", batch=bi, microbatches=batches, flies=args.microbatch_size)
            poses = sample_swarm_poses(
                flies=args.microbatch_size,
                seed=args.seed + bi,
                max_lateral=0.35,
                max_heading_offset_deg=25.0,
            )

            telemetry.set_stage("compile_optics", batch=bi)
            transport, resampled = _ensure_visible(
                poses,
                geometry,
                width=args.screen_width_px,
                height=args.screen_height_px,
                physical_width=args.physical_width,
                ambient=args.ambient,
                seed=args.seed + 10000 + bi,
                telemetry=telemetry,
            )
            total_resampled += resampled
            all_visible_min = min(all_visible_min, float(transport.visible_mass.min()))

            telemetry.set_stage("transport_to_gpu", batch=bi)
            matrix, baseline = to_torch(transport, device=args.device)

            flies = args.microbatch_size
            telemetry.set_stage("allocate_receiver_state", batch=bi)
            receiver_state = torch.zeros((graph.shape[0], 2 * flies), dtype=torch.float32, device=args.device)
            telemetry.emit("receiver_state_allocated", shape=list(receiver_state.shape))

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

            telemetry.set_stage("neural_probe", batch=bi, steps=args.steps)
            with torch.no_grad():
                for step in range(args.steps):
                    telemetry.emit("neural_step_start", step=step)
                    recurrent = torch.sparse.mm(sparse, receiver_state) / float(args.spectral_scale)
                    pre = float(args.gain) * recurrent
                    pre.index_add_(0, visual_idx, float(args.visual_scale) * external)
                    receiver_state = (1.0 - float(args.leak)) * receiver_state + float(args.leak) * torch.tanh(pre)
                    telemetry.emit("neural_step_done", step=step)

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
            telemetry.emit("microbatch_complete", **row)

            del receiver_state, matrix, baseline, external, learned_retina, uniform_retina
            if args.device.startswith("cuda"):
                torch.cuda.empty_cache()

        peak = int(torch.cuda.max_memory_allocated()) if args.device.startswith("cuda") else 0
        total = {
            "experiment": "malecns-swarm-capacity-probe-v2-telemetry",
            "swarm_size": args.swarm_size,
            "microbatch_size": args.microbatch_size,
            "microbatches": batches,
            "steps_per_microbatch": args.steps,
            "all_visible": True,
            "min_visible_mass": all_visible_min,
            "total_resampled": total_resampled,
            "peak_cuda_bytes": peak,
            "peak_cuda_gib": peak / (1024 ** 3),
            "elapsed_s": time.perf_counter() - telemetry.started,
            "batches": rows,
        }
        (args.output_dir / "swarm-capacity-summary.json").write_text(
            json.dumps(total, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        telemetry.set_stage("complete")
        telemetry.emit(
            "swarm_capacity_complete",
            swarm_size=total["swarm_size"],
            microbatch_size=total["microbatch_size"],
            peak_cuda_gib=total["peak_cuda_gib"],
            total_resampled=total["total_resampled"],
            elapsed_s=total["elapsed_s"],
        )
    except BaseException as exc:
        telemetry.emit("probe_error", error=type(exc).__name__, message=str(exc))
        raise
    finally:
        telemetry.stop()


if __name__ == "__main__":
    main()
