# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "matplotlib>=3.9",
#   "healpy>=1.18; platform_system != 'Windows'",
# ]
# ///
"""CMB acoustic-occlusion parameter Monte Carlo for Pontifex Torus.

This is an intervention-space explorer, not a cosmological-detection pipeline.
The main Monte Carlo budget is spent on occlusion parameters theta, while null
maps are used only for calibration.

Two modes are supported:
- synthetic: cheap periodic random field for CI/smoke tests;
- healpix: real HEALPix FITS map (e.g. Planck foreground-cleaned temperature map).

The experiment records the full sampled theta -> response table so later runs can
replace the response functional without losing the intervention design.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Theta:
    sample: int
    center_a: float
    center_b: float
    radius: float
    depth: float
    phase: float
    aspect: float
    geometry: str
    occlusion: str


GEOMETRIES = ("disc", "ellipse", "annulus")
OCCLUSIONS = ("hard", "apodized", "local_mean", "residual_permute")


def periodic_distance(x: np.ndarray, c: float, period: float) -> np.ndarray:
    d = np.abs(x - c)
    return np.minimum(d, period - d)


def synthetic_map(ny: int, nx: int, seed: int) -> np.ndarray:
    """Smooth periodic Gaussian-like field with several spatial scales."""
    rng = np.random.default_rng(seed)
    white = rng.normal(size=(ny, nx))
    ft = np.fft.rfft2(white)
    ky = np.fft.fftfreq(ny)[:, None]
    kx = np.fft.rfftfreq(nx)[None, :]
    k2 = kx * kx + ky * ky
    filt = np.exp(-k2 / 0.012) / np.sqrt(1.0 + 80.0 * k2)
    field = np.fft.irfft2(ft * filt, s=(ny, nx)).real
    field -= field.mean()
    field /= max(field.std(), 1e-12)
    return field


def sample_theta(rng: np.random.Generator, i: int, radius_min: float, radius_max: float) -> Theta:
    # log-uniform radius prevents the largest lesions from dominating the design.
    radius = float(np.exp(rng.uniform(np.log(radius_min), np.log(radius_max))))
    return Theta(
        sample=i,
        center_a=float(rng.random()),
        center_b=float(rng.uniform(-0.9, 0.9)),
        radius=radius,
        depth=float(rng.uniform(0.15, 1.0)),
        phase=float(rng.random()),
        aspect=float(np.exp(rng.uniform(np.log(0.5), np.log(2.0)))),
        geometry=str(rng.choice(GEOMETRIES)),
        occlusion=str(rng.choice(OCCLUSIONS)),
    )


def synthetic_masks(shape: tuple[int, int], theta: Theta) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ny, nx = shape
    yy = np.linspace(-1.0, 1.0, ny, endpoint=False)[:, None]
    xx = np.linspace(0.0, 1.0, nx, endpoint=False)[None, :]
    dx = periodic_distance(xx, theta.center_a, 1.0)
    dy = yy - theta.center_b
    # radius is expressed as a fraction of the shorter map dimension / domain.
    rr = np.sqrt((dx / theta.aspect) ** 2 + (dy * theta.aspect * 0.5) ** 2)
    r = theta.radius
    if theta.geometry == "annulus":
        core = (rr >= 0.55 * r) & (rr <= r)
    else:
        core = rr <= r
    outer = rr <= (1.65 * r)
    boundary = outer & ~core
    return core, boundary, rr


def healpix_masks(nside: int, theta: Theta) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    import healpy as hp

    npix = hp.nside2npix(nside)
    # center_a is longitude phase in [0,1); center_b maps to sin(latitude).
    lon = 2.0 * np.pi * theta.center_a
    lat = np.arcsin(np.clip(theta.center_b, -1.0, 1.0))
    vec = hp.ang2vec(0.5 * np.pi - lat, lon)
    rad = theta.radius
    pix = np.arange(npix)
    vx, vy, vz = hp.pix2vec(nside, pix)
    dots = np.clip(vx * vec[0] + vy * vec[1] + vz * vec[2], -1.0, 1.0)
    rr = np.arccos(dots)
    if theta.geometry == "ellipse":
        # HEALPix ellipse approximation: longitude-dependent angular stretch.
        th, ph = hp.pix2ang(nside, pix)
        dlon = np.angle(np.exp(1j * (ph - lon)))
        dlat = (0.5 * np.pi - th) - lat
        rr = np.sqrt((dlon * np.cos(lat) / theta.aspect) ** 2 + (dlat * theta.aspect) ** 2)
    if theta.geometry == "annulus":
        core = (rr >= 0.55 * rad) & (rr <= rad)
    else:
        core = rr <= rad
    outer = rr <= (1.65 * rad)
    return core, outer & ~core, rr


def apply_occlusion(
    field: np.ndarray,
    core: np.ndarray,
    boundary: np.ndarray,
    rr: np.ndarray,
    theta: Theta,
    rng: np.random.Generator,
) -> np.ndarray:
    out = field.copy()
    if not np.any(core):
        return out
    local = field[boundary]
    if local.size == 0:
        local = field[~core]
    mu = float(np.mean(local))
    sigma = float(np.std(local))
    target = np.full(np.count_nonzero(core), mu, dtype=float)

    if theta.occlusion == "hard":
        target[:] = 0.0
    elif theta.occlusion == "local_mean":
        target[:] = mu
    elif theta.occlusion == "residual_permute":
        residual = local - mu
        if residual.size:
            target = mu + rng.choice(residual, size=target.size, replace=True)
        else:
            target = mu + rng.normal(0.0, sigma, size=target.size)
    elif theta.occlusion == "apodized":
        target[:] = mu

    if theta.occlusion == "apodized":
        x = np.clip(rr[core] / max(theta.radius, 1e-12), 0.0, 1.0)
        weight = theta.depth * 0.5 * (1.0 + np.cos(np.pi * x))
    else:
        weight = np.full(target.size, theta.depth)
    out[core] = (1.0 - weight) * field[core] + weight * target
    return out


def response_metrics(original: np.ndarray, altered: np.ndarray, core: np.ndarray, boundary: np.ndarray) -> dict[str, float]:
    delta = altered - original
    if not np.any(core):
        return {"score": 0.0, "core_rmse": 0.0, "boundary_shift": 0.0, "global_energy": 0.0}
    core_rmse = float(np.sqrt(np.mean(delta[core] ** 2)))
    if np.any(boundary):
        boundary_shift = float(abs(np.mean(altered[boundary]) - np.mean(original[boundary])))
    else:
        boundary_shift = 0.0
    global_energy = float(np.mean(delta * delta))
    # Dimensionless-ish stress score. It deliberately emphasizes local disruption
    # while retaining a weak global penalty; later experiments may replace this.
    scale = max(float(np.std(original)), 1e-12)
    score = core_rmse / scale + 0.25 * boundary_shift / scale + 0.1 * math.sqrt(global_energy) / scale
    return {
        "score": float(score),
        "core_rmse": core_rmse,
        "boundary_shift": boundary_shift,
        "global_energy": global_energy,
    }


def make_null(field: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Phase-scrambled periodic null preserving the discrete power spectrum."""
    shape = field.shape
    if field.ndim != 2:
        # HEALPix lightweight null: permutation is intentionally conservative here;
        # production nulls should use synfast / a_lm randomization.
        return rng.permutation(field)
    ft = np.fft.rfft2(field)
    phase = rng.uniform(0.0, 2.0 * np.pi, size=ft.shape)
    scrambled = np.abs(ft) * np.exp(1j * phase)
    out = np.fft.irfft2(scrambled, s=shape).real
    out -= out.mean()
    out *= field.std() / max(out.std(), 1e-12)
    out += field.mean()
    return out


def load_healpix(path: Path, field_index: int) -> tuple[np.ndarray, int]:
    import healpy as hp

    m = np.asarray(hp.read_map(path, field=field_index, dtype=float, verbose=False))
    good = np.isfinite(m) & (m > hp.UNSEEN / 2)
    fill = float(np.median(m[good]))
    m = np.where(good, m, fill)
    return m, hp.get_nside(m)


def run_one(field, theta, rng, mode, nside=None):
    if mode == "synthetic":
        core, boundary, rr = synthetic_masks(field.shape, theta)
    else:
        core, boundary, rr = healpix_masks(nside, theta)
    altered = apply_occlusion(field, core, boundary, rr, theta, rng)
    metrics = response_metrics(field, altered, core, boundary)
    return metrics


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plots(rows: list[dict], outdir: Path) -> list[str]:
    import matplotlib.pyplot as plt

    outdir.mkdir(parents=True, exist_ok=True)
    files = []

    radius = np.array([r["radius"] for r in rows])
    phase = np.array([r["phase"] for r in rows])
    score = np.array([r["score"] for r in rows])

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    sc = ax.scatter(radius, score, c=phase, s=10, alpha=0.65)
    ax.set_xscale("log")
    ax.set_xlabel("occlusion radius")
    ax.set_ylabel("response score")
    ax.set_title("Pontifex CMB occlusion parameter Monte Carlo")
    fig.colorbar(sc, ax=ax, label="torus phase")
    p = outdir / "radius-response.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    h = ax.hexbin(phase, radius, C=score, gridsize=30, reduce_C_function=np.mean, mincnt=1)
    ax.set_yscale("log")
    ax.set_xlabel("phase")
    ax.set_ylabel("occlusion radius")
    ax.set_title("Mean response over (phase, radius)")
    fig.colorbar(h, ax=ax, label="mean response")
    p = outdir / "phase-radius-heatmap.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))

    labels = sorted(set((r["geometry"], r["occlusion"]) for r in rows))
    means = [np.mean([r["score"] for r in rows if (r["geometry"], r["occlusion"]) == x]) for x in labels]
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.bar(np.arange(len(labels)), means)
    ax.set_xticks(np.arange(len(labels)), [f"{a}\n{b}" for a, b in labels], rotation=45, ha="right")
    ax.set_ylabel("mean response score")
    ax.set_title("Intervention family response")
    p = outdir / "family-response.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))
    return files


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["synthetic", "healpix"], default="synthetic")
    ap.add_argument("--map-fits", type=Path)
    ap.add_argument("--field-index", type=int, default=0)
    ap.add_argument("--samples", type=int, default=5000)
    ap.add_argument("--null-maps", type=int, default=8)
    ap.add_argument("--null-samples", type=int, default=250)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("--ny", type=int, default=192)
    ap.add_argument("--nx", type=int, default=384)
    ap.add_argument("--radius-min", type=float)
    ap.add_argument("--radius-max", type=float)
    ap.add_argument("--output", type=Path, default=Path("pontifex-cmb-occlusion-mc.json"))
    ap.add_argument("--rows", type=Path, default=Path("pontifex-cmb-occlusion-mc.csv"))
    ap.add_argument("--plots", type=Path, default=Path("pontifex-cmb-occlusion-plots"))
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    if args.mode == "healpix":
        if args.map_fits is None:
            ap.error("--map-fits is required in healpix mode")
        field, nside = load_healpix(args.map_fits, args.field_index)
        rmin = args.radius_min or math.radians(0.25)
        rmax = args.radius_max or math.radians(12.0)
    else:
        field = synthetic_map(args.ny, args.nx, args.seed)
        nside = None
        rmin = args.radius_min or 0.008
        rmax = args.radius_max or 0.20

    rows = []
    thetas = [sample_theta(rng, i, rmin, rmax) for i in range(args.samples)]
    for theta in thetas:
        metrics = run_one(field, theta, rng, args.mode, nside)
        rows.append({**asdict(theta), **metrics, "dataset": "observed" if args.mode == "healpix" else "synthetic"})

    null_scores = []
    # Nulls calibrate the response scale; they do not consume the main MC budget.
    for null_id in range(args.null_maps):
        null = make_null(field, rng)
        for j in range(min(args.null_samples, len(thetas))):
            theta = thetas[(null_id * args.null_samples + j) % len(thetas)]
            m = run_one(null, theta, rng, args.mode, nside)
            null_scores.append(m["score"])

    scores = np.array([r["score"] for r in rows], dtype=float)
    null_scores_a = np.asarray(null_scores, dtype=float)
    null_mu = float(np.mean(null_scores_a)) if len(null_scores_a) else float("nan")
    null_sd = float(np.std(null_scores_a, ddof=1)) if len(null_scores_a) > 1 else float("nan")
    for r in rows:
        r["z_vs_null"] = float((r["score"] - null_mu) / null_sd) if null_sd > 0 else float("nan")

    top = sorted(rows, key=lambda x: x["score"], reverse=True)[:25]
    plot_files = plots(rows, args.plots)
    result = {
        "experiment": "CMB Acoustic Occlusion Stress Test — intervention parameter Monte Carlo",
        "mode": args.mode,
        "seed": args.seed,
        "samples": args.samples,
        "null_maps": args.null_maps,
        "null_samples_per_map": args.null_samples,
        "parameter_space": {
            "geometry": list(GEOMETRIES),
            "occlusion": list(OCCLUSIONS),
            "radius_min": rmin,
            "radius_max": rmax,
            "depth": [0.15, 1.0],
            "phase": [0.0, 1.0],
            "aspect": [0.5, 2.0],
        },
        "observed_response": {
            "mean": float(np.mean(scores)),
            "median": float(np.median(scores)),
            "p95": float(np.quantile(scores, 0.95)),
            "max": float(np.max(scores)),
        },
        "null_calibration": {"mean": null_mu, "std": null_sd, "n": len(null_scores)},
        "top_parameter_samples": top,
        "rows_csv": str(args.rows),
        "plots": plot_files,
        "interpretation_contract": {
            "primary_object": "theta -> response surface over intervention parameters",
            "monte_carlo_budget": "spent primarily on intervention parameters, not on generating many universes",
            "null_role": "calibration only; production HEALPix nulls should use C_l-matched synfast or a_lm phase randomization",
            "no_detection_claim": "high response is a candidate region for follow-up, not evidence of cosmic torus topology",
            "next_step": "repeat surviving regions on Planck, ACT+Planck, Gaussian C_l-matched skies, and phase-scrambled skies",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    save_csv(rows, args.rows)
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
