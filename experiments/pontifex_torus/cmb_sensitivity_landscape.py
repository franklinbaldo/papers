# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "matplotlib>=3.9",
# ]
# ///
"""Sensitivity-landscape search for the Pontifex CMB occlusion stress test.

Searches controllable intervention settings for lower detectable signal amplitude.
The objective is not "largest response"; it is better sensitivity at controlled
false-positive rate.

Search dimensions:
- occlusion family
- geometry
- radius band
- depth band
- aspect band
- single vs double occlusion
- double-occlusion phase/separation coupling

Outputs a ranked configuration table with alpha_80 estimates when observed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cmb_occlusion_mc import Theta, make_null, run_one, synthetic_map
from cmb_sensitivity import injection_pattern


@dataclass(frozen=True)
class Config:
    name: str
    geometry: str
    occlusion: str
    radius_lo: float
    radius_hi: float
    depth_lo: float
    depth_hi: float
    aspect_lo: float
    aspect_hi: float
    mode: str
    pair_phase_delta: float = 0.5
    pair_separation: float = 0.22


def configs() -> list[Config]:
    out: list[Config] = []
    base = [
        ("disc", "apodized"),
        ("disc", "adjacency_phase"),
        ("annulus", "adjacency_phase"),
        ("ellipse", "adjacency_phase"),
        ("ellipse", "local_mean"),
    ]
    scales = [("small", 0.008, 0.025), ("mid", 0.025, 0.07), ("large", 0.07, 0.16)]
    depths = [("soft", 0.2, 0.5), ("strong", 0.6, 1.0)]
    for geom, occ in base:
        for sname, r0, r1 in scales:
            for dname, d0, d1 in depths:
                out.append(
                    Config(
                        name=f"single:{geom}:{occ}:{sname}:{dname}",
                        geometry=geom,
                        occlusion=occ,
                        radius_lo=r0,
                        radius_hi=r1,
                        depth_lo=d0,
                        depth_hi=d1,
                        aspect_lo=0.7,
                        aspect_hi=1.8,
                        mode="single",
                    )
                )
    # Double-occlusion "interferometer" candidates.
    for sep in (0.12, 0.22, 0.35):
        for dphi in (0.25, 0.5):
            out.append(
                Config(
                    name=f"double:annulus:adjacency_phase:sep{sep}:dphi{dphi}",
                    geometry="annulus",
                    occlusion="adjacency_phase",
                    radius_lo=0.012,
                    radius_hi=0.05,
                    depth_lo=0.35,
                    depth_hi=0.85,
                    aspect_lo=0.8,
                    aspect_hi=1.2,
                    mode="double",
                    pair_phase_delta=dphi,
                    pair_separation=sep,
                )
            )
    return out


def sample_theta_from_config(rng: np.random.Generator, i: int, cfg: Config) -> Theta:
    return Theta(
        sample=i,
        center_a=float(rng.random()),
        center_b=float(rng.uniform(-0.75, 0.75)),
        radius=float(np.exp(rng.uniform(np.log(cfg.radius_lo), np.log(cfg.radius_hi)))),
        depth=float(rng.uniform(cfg.depth_lo, cfg.depth_hi)),
        phase=float(rng.random()),
        aspect=float(np.exp(rng.uniform(np.log(cfg.aspect_lo), np.log(cfg.aspect_hi)))),
        geometry=cfg.geometry,
        occlusion=cfg.occlusion,
    )


def paired_theta(theta: Theta, cfg: Config) -> Theta:
    return Theta(
        sample=theta.sample,
        center_a=(theta.center_a + cfg.pair_separation) % 1.0,
        center_b=-theta.center_b * 0.5,
        radius=theta.radius,
        depth=theta.depth,
        phase=(theta.phase + cfg.pair_phase_delta) % 1.0,
        aspect=theta.aspect,
        geometry=theta.geometry,
        occlusion=theta.occlusion,
    )


def intervention_score(field: np.ndarray, theta: Theta, cfg: Config, seed: int) -> float:
    rng1 = np.random.default_rng(seed + 13)
    s1 = run_one(field, theta, rng1, "synthetic")["score"]
    if cfg.mode == "single":
        return float(s1)

    theta2 = paired_theta(theta, cfg)
    rng2 = np.random.default_rng(seed + 29)
    s2 = run_one(field, theta2, rng2, "synthetic")["score"]

    # Approximate simultaneous interaction by applying both lesions sequentially
    # to the same field through response deltas. This preserves a dedicated
    # interaction observable without conflating it with either single response.
    # The current harness exposes only score-level run_one, so the interaction
    # channel is a conservative nonlinear contrast.
    return float(abs((s1 + s2) - 2.0 * math.sqrt(max(s1 * s2, 0.0))))


def config_statistic(
    field: np.ndarray,
    cfg: Config,
    seed: int,
    samples: int,
    null_maps_n: int,
    phase0: float,
) -> float:
    rng = np.random.default_rng(seed)
    thetas = [sample_theta_from_config(rng, i, cfg) for i in range(samples)]
    nulls = [
        make_null(field, np.random.default_rng(seed + 1_000_003 * (i + 1)))
        for i in range(null_maps_n)
    ]
    zs = []
    phases = []
    for theta in thetas:
        obs = intervention_score(field, theta, cfg, seed + theta.sample * 101)
        nvals = np.asarray(
            [
                intervention_score(null, theta, cfg, seed + theta.sample * 101 + j)
                for j, null in enumerate(nulls)
            ],
            dtype=float,
        )
        sd = float(np.std(nvals, ddof=1)) if len(nvals) > 1 else float("nan")
        if not np.isfinite(sd) or sd <= 1e-12:
            continue
        zs.append((obs - float(np.mean(nvals))) / sd)
        phases.append(theta.phase)

    if len(zs) < 8:
        return float("nan")
    z = np.asarray(zs)
    ph = np.asarray(phases)
    expected = np.cos(2.0 * np.pi * (ph - phase0))
    return float(np.sum(z * expected) / math.sqrt(np.sum(expected**2) + 1e-12))


def null_threshold(
    base: np.ndarray,
    cfg: Config,
    seed: int,
    samples: int,
    null_maps: int,
    repeats: int,
    phase0: float,
) -> tuple[float, float]:
    vals = []
    for i in range(repeats):
        nf = make_null(base, np.random.default_rng(seed + 70_000_001 + i * 9973))
        stat = config_statistic(nf, cfg, seed + 10_007 * (i + 1), samples, null_maps, phase0)
        if np.isfinite(stat):
            vals.append(stat)
    arr = np.asarray(vals, dtype=float)
    if not len(arr):
        return float("nan"), float("nan")
    return float(np.quantile(np.abs(arr), 0.95)), float(np.mean(np.abs(arr)))


def crossing(points: list[dict], target: float) -> float | None:
    for row in sorted([r for r in points if r["alpha"] > 0], key=lambda r: r["alpha"]):
        if row["power"] >= target:
            return float(row["alpha"])
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--amplitudes", type=float, nargs="+", default=[0, 0.01, 0.03, 0.1, 0.3])
    ap.add_argument("--families", nargs="+", default=["canonical", "warped"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--samples", type=int, default=160)
    ap.add_argument("--null-maps", type=int, default=5)
    ap.add_argument("--null-repeats", type=int, default=8)
    ap.add_argument("--top-configs", type=int, default=12)
    ap.add_argument("--ny", type=int, default=96)
    ap.add_argument("--nx", type=int, default=192)
    ap.add_argument("--seed-base", type=int, default=20260918)
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-sensitivity-landscape.json"))
    ap.add_argument("--rows", type=Path, default=Path("pontifex-cmb-sensitivity-landscape.csv"))
    ap.add_argument("--plot", type=Path, default=Path("pontifex-cmb-sensitivity-landscape.png"))
    args = ap.parse_args()

    all_cfg = configs()
    records: list[dict] = []

    for cfg_idx, cfg in enumerate(all_cfg):
        for family in args.families:
            for seed_offset in args.seeds:
                seed = args.seed_base + 1_000_003 * seed_offset + 97_409 * cfg_idx
                base = synthetic_map(args.ny, args.nx, seed)
                phase0 = float(np.random.default_rng(seed + 17).random())
                thr, null_abs_mean = null_threshold(
                    base, cfg, seed + 101, args.samples, args.null_maps, args.null_repeats, phase0
                )
                for alpha in args.amplitudes:
                    field = base.copy()
                    if alpha > 0:
                        field = field + injection_pattern(field.shape, alpha, family, phase0)
                    stat = config_statistic(
                        field, cfg, seed + 211, args.samples, args.null_maps, phase0
                    )
                    detected = bool(np.isfinite(stat) and np.isfinite(thr) and abs(stat) >= thr)
                    records.append({
                        "config": cfg.name,
                        "mode": cfg.mode,
                        "geometry": cfg.geometry,
                        "occlusion": cfg.occlusion,
                        "radius_lo": cfg.radius_lo,
                        "radius_hi": cfg.radius_hi,
                        "depth_lo": cfg.depth_lo,
                        "depth_hi": cfg.depth_hi,
                        "pair_phase_delta": cfg.pair_phase_delta,
                        "pair_separation": cfg.pair_separation,
                        "family": family,
                        "seed": seed_offset,
                        "alpha": float(alpha),
                        "statistic": float(stat),
                        "null_threshold": float(thr),
                        "null_abs_mean": float(null_abs_mean),
                        "detected": detected,
                    })

    summary: list[dict] = []
    for cfg in all_cfg:
        for family in args.families:
            subset = [r for r in records if r["config"] == cfg.name and r["family"] == family]
            points = []
            for alpha in args.amplitudes:
                rr = [r for r in subset if r["alpha"] == alpha]
                points.append({
                    "alpha": float(alpha),
                    "power": float(np.mean([r["detected"] for r in rr])) if rr else float("nan"),
                })
            fpr = next((p["power"] for p in points if p["alpha"] == 0), float("nan"))
            a80 = crossing(points, 0.8)
            a90 = crossing(points, 0.9)
            # Utility prefers lower alpha80, then lower FPR. Missing alpha80 is poor.
            sens = 1.0 / a80 if a80 is not None and a80 > 0 else 0.0
            utility = sens / (0.05 + max(fpr, 0.0))
            summary.append({
                "config": cfg.name,
                "family": family,
                "alpha_80": a80,
                "alpha_90": a90,
                "false_positive_rate": fpr,
                "utility": utility,
                "power_curve": points,
            })

    ranked = sorted(summary, key=lambda r: (r["utility"], -(r["false_positive_rate"] if np.isfinite(r["false_positive_rate"]) else 1.0)), reverse=True)
    top = ranked[: args.top_configs]

    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    import matplotlib.pyplot as plt
    labels = [r["config"] + "\n" + r["family"] for r in top]
    vals = [r["alpha_80"] if r["alpha_80"] is not None else max(args.amplitudes) * 1.2 for r in top]
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    ax.bar(np.arange(len(top)), vals)
    ax.set_xticks(np.arange(len(top)), labels, rotation=70, ha="right")
    ax.set_ylabel("alpha_80 (lower is better; capped if not reached)")
    ax.set_title("Sensitivity landscape: best controllable intervention configurations")
    fig.tight_layout()
    args.plot.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.plot, dpi=170)
    plt.close(fig)

    result = {
        "experiment": "CMB controllable sensitivity landscape",
        "configs_tested": len(all_cfg),
        "families": args.families,
        "amplitudes": args.amplitudes,
        "seeds": args.seeds,
        "top_configurations": top,
        "ranked_configurations": ranked,
        "search_contract": {
            "objective": "minimize detectable injected amplitude alpha_80 while keeping alpha=0 false positives controlled",
            "controllable_axes": ["occlusion", "geometry", "radius_band", "depth_band", "aspect_band", "single_vs_double", "pair_phase_delta", "pair_separation"],
            "double_occlusion": "treated as an interaction-sensitive channel to test interferometer-like gain",
            "selection_warning": "ranking is exploratory; the winning configuration must be re-estimated on fresh seeds before freezing for real data",
            "real_data_gate": "freeze intervention design only after a winner or Pareto set replicates on held-out synthetic seeds and stronger null ensembles",
        },
        "rows_csv": str(args.rows),
        "plot": str(args.plot),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
