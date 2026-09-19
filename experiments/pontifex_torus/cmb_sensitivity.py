# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "matplotlib>=3.9",
# ]
# ///
"""Synthetic sensitivity / power benchmark for the CMB occlusion stress test.

Goal
----
Measure the smallest injected toroidal signal amplitude that the matched-theta
occlusion pipeline can recover with controlled false-positive rate *before*
running on real CMB data.

This is deliberately synthetic and adversarial. It estimates a detection-power
curve over amplitudes alpha and reports alpha_80 / alpha_90 when observed.

The injection is not tied to a single easy pattern. Three families are used:
- canonical: first-harmonic toroidal modulation;
- warped: phase-warped toroidal modulation;
- offmodel: second-harmonic / mixed modulation.

Detection is based on a held-out phase-aware statistic computed over matched-null
z(theta) values, not on raw intervention damage.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cmb_occlusion_mc import (
    Theta,
    make_null,
    matched_null_stats,
    run_one,
    sample_theta,
    synthetic_map,
)


INJECTION_FAMILIES = ("canonical", "warped", "offmodel")


@dataclass(frozen=True)
class TrialResult:
    alpha: float
    family: str
    seed: int
    detected: bool
    statistic: float
    null_threshold: float
    p_empirical: float
    phase_alignment: float
    samples: int
    null_maps: int


def injection_pattern(
    shape: tuple[int, int],
    amplitude: float,
    family: str,
    phase0: float,
) -> np.ndarray:
    ny, nx = shape
    y = np.linspace(-1.0, 1.0, ny, endpoint=False)[:, None]
    x = np.linspace(0.0, 1.0, nx, endpoint=False)[None, :]
    theta = 2.0 * np.pi * (x + phase0)

    # Smooth spatial envelope avoids a trivially global sinusoid while preserving
    # a toroidal phase coordinate around x.
    envelope = np.exp(-0.5 * (y / 0.52) ** 2)

    if family == "canonical":
        pat = np.cos(theta) * envelope
    elif family == "warped":
        warped = theta + 0.55 * np.sin(2.0 * np.pi * y)
        pat = np.cos(warped) * envelope
    elif family == "offmodel":
        pat = (
            0.65 * np.cos(2.0 * theta + 0.4)
            + 0.35 * np.sin(theta + 1.8 * np.pi * y)
        ) * envelope
    else:
        raise ValueError(f"unknown injection family: {family}")

    pat -= pat.mean()
    pat /= max(float(pat.std()), 1e-12)
    return amplitude * pat


def phase_statistic(rows: list[dict], phase0: float) -> tuple[float, float]:
    """Phase-aware coherent statistic and alignment.

    Uses first harmonic over phase-active interventions only. The projected
    statistic asks whether matched-null z(theta) coherently follows the injected
    toroidal phase, instead of rewarding isolated extreme z values.
    """
    active = [
        r
        for r in rows
        if r["occlusion"] == "adjacency_phase" or r["geometry"] == "ellipse"
    ]
    if len(active) < 8:
        return float("nan"), float("nan")

    phase = np.asarray([r["phase"] for r in active], dtype=float)
    z = np.asarray([r["z"] for r in active], dtype=float)
    good = np.isfinite(z)
    phase = phase[good]
    z = z[good]
    if len(z) < 8:
        return float("nan"), float("nan")

    expected = np.cos(2.0 * np.pi * (phase - phase0))
    statistic = float(np.sum(z * expected) / math.sqrt(np.sum(expected**2) + 1e-12))
    alignment = float(np.corrcoef(z, expected)[0, 1]) if np.std(z) > 1e-12 else 0.0
    return statistic, alignment


def evaluate_field(
    field: np.ndarray,
    seed: int,
    samples: int,
    null_maps_n: int,
    phase0: float,
) -> tuple[float, float, list[dict], list[np.ndarray]]:
    rng = np.random.default_rng(seed)
    rmin, rmax = 0.008, 0.20
    thetas = [sample_theta(rng, i, rmin, rmax) for i in range(samples)]
    null_maps = [
        make_null(field, np.random.default_rng(seed + 1_000_003 * (i + 1)))
        for i in range(null_maps_n)
    ]

    rows: list[dict] = []
    for theta in thetas:
        obs_rng = np.random.default_rng(seed + 97_409 * (theta.sample + 1))
        score = run_one(field, theta, obs_rng, "synthetic")["score"]
        mu, sd, _ = matched_null_stats(null_maps, theta, seed, "synthetic", None)
        z = float((score - mu) / sd) if np.isfinite(sd) and sd > 1e-12 else float("nan")
        rows.append(
            {
                "sample": theta.sample,
                "phase": theta.phase,
                "geometry": theta.geometry,
                "occlusion": theta.occlusion,
                "z": z,
            }
        )

    statistic, alignment = phase_statistic(rows, phase0)
    return statistic, alignment, rows, null_maps


def null_statistic_distribution(
    base_field: np.ndarray,
    seed: int,
    samples: int,
    null_maps_n: int,
    phase0: float,
    repeats: int,
) -> np.ndarray:
    vals = []
    for i in range(repeats):
        null_field = make_null(
            base_field, np.random.default_rng(seed + 70_000_001 + i * 1_000_003)
        )
        stat, _, _, _ = evaluate_field(
            null_field,
            seed + 10_007 * (i + 1),
            samples,
            null_maps_n,
            phase0,
        )
        if np.isfinite(stat):
            vals.append(stat)
    return np.asarray(vals, dtype=float)


def empirical_two_sided_p(stat: float, null_stats: np.ndarray) -> float:
    return float((1 + np.count_nonzero(np.abs(null_stats) >= abs(stat))) / (len(null_stats) + 1))


def threshold_from_null(null_stats: np.ndarray, alpha: float = 0.05) -> float:
    if len(null_stats) == 0:
        return float("nan")
    return float(np.quantile(np.abs(null_stats), 1.0 - alpha))


def estimate_crossing(summary: list[dict], target: float) -> float | None:
    pts = sorted(
        [(float(r["alpha"]), float(r["power"])) for r in summary if r["alpha"] > 0],
        key=lambda x: x[0],
    )
    for a, p in pts:
        if p >= target:
            return a
    return None


def plot_power(summary: list[dict], out: Path) -> None:
    import matplotlib.pyplot as plt

    out.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    families = sorted(set(r["family"] for r in summary))
    for family in families:
        rows = sorted(
            [r for r in summary if r["family"] == family and r["alpha"] > 0],
            key=lambda r: r["alpha"],
        )
        ax.plot(
            [r["alpha"] for r in rows],
            [r["power"] for r in rows],
            marker="o",
            label=family,
        )
    ax.axhline(0.8, linestyle="--", linewidth=1)
    ax.axhline(0.9, linestyle=":", linewidth=1)
    ax.set_xscale("log")
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("injected amplitude alpha")
    ax.set_ylabel("empirical detection power")
    ax.set_title("Synthetic toroidal-signal sensitivity curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--amplitudes",
        type=float,
        nargs="+",
        default=[0.0, 0.003, 0.01, 0.03, 0.1, 0.3],
    )
    ap.add_argument("--families", nargs="+", default=list(INJECTION_FAMILIES))
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--null-maps", type=int, default=8)
    ap.add_argument("--null-stat-repeats", type=int, default=24)
    ap.add_argument("--ny", type=int, default=128)
    ap.add_argument("--nx", type=int, default=256)
    ap.add_argument("--seed-base", type=int, default=20260918)
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-sensitivity.json")
    )
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-sensitivity.csv")
    )
    ap.add_argument(
        "--plot", type=Path, default=Path("pontifex-cmb-sensitivity-power.png")
    )
    args = ap.parse_args()

    trials: list[TrialResult] = []

    for family in args.families:
        for seed_offset in args.seeds:
            seed = args.seed_base + 1_000_003 * seed_offset
            base = synthetic_map(args.ny, args.nx, seed)
            phase0 = float(np.random.default_rng(seed + 17).random())

            null_stats = null_statistic_distribution(
                base,
                seed + 101,
                args.samples,
                args.null_maps,
                phase0,
                args.null_stat_repeats,
            )
            threshold = threshold_from_null(null_stats, 0.05)

            for alpha in args.amplitudes:
                field = base.copy()
                if alpha > 0:
                    field = field + injection_pattern(
                        field.shape, alpha, family, phase0
                    )

                stat, alignment, _, _ = evaluate_field(
                    field,
                    seed + 211,
                    args.samples,
                    args.null_maps,
                    phase0,
                )
                p = empirical_two_sided_p(stat, null_stats)
                detected = bool(np.isfinite(stat) and abs(stat) >= threshold)
                trials.append(
                    TrialResult(
                        alpha=float(alpha),
                        family=family,
                        seed=int(seed_offset),
                        detected=detected,
                        statistic=float(stat),
                        null_threshold=float(threshold),
                        p_empirical=p,
                        phase_alignment=float(alignment),
                        samples=args.samples,
                        null_maps=args.null_maps,
                    )
                )

    records = [t.__dict__ for t in trials]
    args.rows.parent.mkdir(parents=True, exist_ok=True)
    with args.rows.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    summary = []
    for family in args.families:
        for alpha in args.amplitudes:
            rr = [r for r in records if r["family"] == family and r["alpha"] == alpha]
            power = float(np.mean([bool(r["detected"]) for r in rr]))
            summary.append(
                {
                    "family": family,
                    "alpha": float(alpha),
                    "trials": len(rr),
                    "power": power,
                    "mean_abs_statistic": float(np.mean([abs(r["statistic"]) for r in rr])),
                    "mean_alignment": float(np.mean([r["phase_alignment"] for r in rr])),
                }
            )

    alpha_thresholds = {}
    for family in args.families:
        fam = [r for r in summary if r["family"] == family]
        alpha_thresholds[family] = {
            "alpha_80": estimate_crossing(fam, 0.80),
            "alpha_90": estimate_crossing(fam, 0.90),
            "false_positive_rate_at_alpha_0": next(
                (r["power"] for r in fam if r["alpha"] == 0.0), None
            ),
        }

    plot_power(summary, args.plot)

    result = {
        "experiment": "CMB synthetic toroidal sensitivity benchmark",
        "amplitudes": args.amplitudes,
        "families": args.families,
        "seeds": args.seeds,
        "samples_per_trial": args.samples,
        "null_maps_per_trial": args.null_maps,
        "null_stat_repeats": args.null_stat_repeats,
        "summary": summary,
        "thresholds": alpha_thresholds,
        "gate_contract": {
            "purpose": "estimate detection power before any real CMB run",
            "real_data_gate": "do not interpret a null result on Planck until alpha_80/alpha_90 are characterized in the signal class of interest",
            "false_positive_gate": "alpha=0 detection rate should be compatible with the nominal 5% threshold across repeated seeds",
            "robustness_gate": "canonical, warped, and offmodel injections are reported separately so sensitivity is not defined only for the easiest assumed signal",
            "scope": "this benchmark calibrates sensitivity of the current statistic; it does not validate a physical torus model",
        },
        "rows_csv": str(args.rows),
        "plot": str(args.plot),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
