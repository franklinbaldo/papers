# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "matplotlib>=3.9",
#   "healpy>=1.18; platform_system != 'Windows'",
# ]
# ///
"""CMB acoustic-occlusion parameter Monte Carlo for Pontifex Torus.

The main Monte Carlo budget is spent on intervention parameters theta. Every
observed intervention is calibrated against the *same theta* on a small ensemble
of null maps, producing excess(theta) and z(theta).

Modes:
- synthetic: cheap periodic random field for CI / design validation;
- healpix: real HEALPix FITS map, e.g. a Planck CMB temperature map.

This is a stress/falsification harness, not a cosmological-detection pipeline.
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
OCCLUSIONS = (
    "hard",
    "apodized",
    "local_mean",
    "residual_permute",
    "adjacency_phase",
)


def signed_periodic_delta(x: np.ndarray, c: float, period: float) -> np.ndarray:
    return (x - c + 0.5 * period) % period - 0.5 * period


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


def sample_theta(
    rng: np.random.Generator, i: int, radius_min: float, radius_max: float
) -> Theta:
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


def synthetic_masks(
    shape: tuple[int, int], theta: Theta
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ny, nx = shape
    yy = np.linspace(-1.0, 1.0, ny, endpoint=False)[:, None]
    xx = np.linspace(0.0, 1.0, nx, endpoint=False)[None, :]
    dx = signed_periodic_delta(xx, theta.center_a, 1.0)
    dy = yy - theta.center_b

    # phase is a genuine intervention coordinate: for anisotropic lesions it
    # rotates the local frame; for adjacency_phase it also rotates the boundary
    # correspondence used to reconstruct the hidden region.
    ang = 2.0 * np.pi * theta.phase
    ca, sa = math.cos(ang), math.sin(ang)
    ux = ca * dx - sa * (0.5 * dy)
    uy = sa * dx + ca * (0.5 * dy)
    if theta.geometry == "ellipse":
        rr = np.sqrt((ux / theta.aspect) ** 2 + (uy * theta.aspect) ** 2)
    else:
        rr = np.sqrt(dx**2 + (0.5 * dy) ** 2)
    local_angle = np.arctan2(uy, ux)

    r = theta.radius
    if theta.geometry == "annulus":
        core = (rr >= 0.55 * r) & (rr <= r)
    else:
        core = rr <= r
    outer = rr <= 1.65 * r
    return core, outer & ~core, rr, local_angle


def healpix_masks(
    nside: int, theta: Theta
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    import healpy as hp

    npix = hp.nside2npix(nside)
    lon = 2.0 * np.pi * theta.center_a
    lat = np.arcsin(np.clip(theta.center_b, -1.0, 1.0))
    center = hp.ang2vec(0.5 * np.pi - lat, lon)

    pix = np.arange(npix)
    vx, vy, vz = hp.pix2vec(nside, pix)
    dots = np.clip(vx * center[0] + vy * center[1] + vz * center[2], -1.0, 1.0)
    angular_distance = np.arccos(dots)

    east = np.array([-math.sin(lon), math.cos(lon), 0.0])
    north = np.array(
        [-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat)]
    )
    x = vx * east[0] + vy * east[1] + vz * east[2]
    y = vx * north[0] + vy * north[1] + vz * north[2]

    ang = 2.0 * np.pi * theta.phase
    ca, sa = math.cos(ang), math.sin(ang)
    ux = ca * x - sa * y
    uy = sa * x + ca * y
    local_angle = np.arctan2(uy, ux)

    if theta.geometry == "ellipse":
        rr = np.sqrt((ux / theta.aspect) ** 2 + (uy * theta.aspect) ** 2)
    else:
        rr = angular_distance

    rad = theta.radius
    if theta.geometry == "annulus":
        core = (rr >= 0.55 * rad) & (rr <= rad)
    else:
        core = rr <= rad
    outer = rr <= 1.65 * rad
    return core, outer & ~core, rr, local_angle


def phase_matched_boundary_values(
    field: np.ndarray,
    core: np.ndarray,
    boundary: np.ndarray,
    local_angle: np.ndarray,
    phase: float,
) -> np.ndarray:
    """Map each hidden pixel to a boundary value after an angular phase shift."""
    bidx = np.flatnonzero(boundary)
    cidx = np.flatnonzero(core)
    if bidx.size == 0:
        return np.full(cidx.size, float(np.mean(field[~core])))
    ba = local_angle.flat[bidx]
    order = np.argsort(ba)
    ba = ba[order]
    bv = field.flat[bidx[order]]
    target_angle = ((local_angle.flat[cidx] + 2.0 * np.pi * phase + np.pi) % (2.0 * np.pi)) - np.pi
    pos = np.searchsorted(ba, target_angle, side="left")
    pos = np.clip(pos, 0, len(ba) - 1)
    left = np.clip(pos - 1, 0, len(ba) - 1)
    choose_left = np.abs(ba[left] - target_angle) < np.abs(ba[pos] - target_angle)
    pos = np.where(choose_left, left, pos)
    return bv[pos]


def apply_occlusion(
    field: np.ndarray,
    core: np.ndarray,
    boundary: np.ndarray,
    rr: np.ndarray,
    local_angle: np.ndarray,
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
    ncore = int(np.count_nonzero(core))
    target = np.full(ncore, mu, dtype=float)

    if theta.occlusion == "hard":
        target[:] = 0.0
    elif theta.occlusion == "local_mean":
        target[:] = mu
    elif theta.occlusion == "residual_permute":
        residual = local - mu
        target = (
            mu + rng.choice(residual, size=ncore, replace=True)
            if residual.size
            else mu + rng.normal(0.0, sigma, size=ncore)
        )
    elif theta.occlusion == "adjacency_phase":
        target = phase_matched_boundary_values(
            field, core, boundary, local_angle, theta.phase
        )
    elif theta.occlusion == "apodized":
        target[:] = mu

    if theta.occlusion == "apodized":
        x = np.clip(rr[core] / max(theta.radius, 1e-12), 0.0, 1.0)
        weight = theta.depth * 0.5 * (1.0 + np.cos(np.pi * x))
    else:
        weight = np.full(ncore, theta.depth)

    out[core] = (1.0 - weight) * field[core] + weight * target
    return out


def response_metrics(
    original: np.ndarray,
    altered: np.ndarray,
    core: np.ndarray,
    boundary: np.ndarray,
) -> dict[str, float]:
    delta = altered - original
    if not np.any(core):
        return {
            "score": 0.0,
            "core_rmse": 0.0,
            "boundary_shift": 0.0,
            "global_energy": 0.0,
        }
    core_rmse = float(np.sqrt(np.mean(delta[core] ** 2)))
    boundary_shift = (
        float(abs(np.mean(altered[boundary]) - np.mean(original[boundary])))
        if np.any(boundary)
        else 0.0
    )
    global_energy = float(np.mean(delta * delta))
    scale = max(float(np.std(original)), 1e-12)
    score = (
        core_rmse / scale
        + 0.25 * boundary_shift / scale
        + 0.1 * math.sqrt(global_energy) / scale
    )
    return {
        "score": float(score),
        "core_rmse": core_rmse,
        "boundary_shift": boundary_shift,
        "global_energy": global_energy,
    }


def make_null(field: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Phase-scrambled 2D null preserving power; lightweight HEALPix placeholder."""
    if field.ndim != 2:
        # Production HEALPix runs must graduate to C_l-matched synfast / a_lm
        # randomization before scientific interpretation.
        return rng.permutation(field)

    shape = field.shape
    ft = np.fft.rfft2(field)
    random_phase = rng.uniform(0.0, 2.0 * np.pi, size=ft.shape)
    scrambled = np.abs(ft) * np.exp(1j * random_phase)
    out = np.fft.irfft2(scrambled, s=shape).real
    out -= out.mean()
    out *= field.std() / max(out.std(), 1e-12)
    out += field.mean()
    return out


def load_healpix(path: Path, field_index: int) -> tuple[np.ndarray, int]:
    import healpy as hp

    m = np.asarray(hp.read_map(path, field=field_index, dtype=float))
    good = np.isfinite(m) & (m > hp.UNSEEN / 2)
    fill = float(np.median(m[good]))
    m = np.where(good, m, fill)
    return m, hp.get_nside(m)


def run_one(
    field: np.ndarray,
    theta: Theta,
    rng: np.random.Generator,
    mode: str,
    nside: int | None = None,
) -> dict[str, float]:
    if mode == "synthetic":
        core, boundary, rr, local_angle = synthetic_masks(field.shape, theta)
    else:
        assert nside is not None
        core, boundary, rr, local_angle = healpix_masks(nside, theta)
    altered = apply_occlusion(
        field, core, boundary, rr, local_angle, theta, rng
    )
    return response_metrics(field, altered, core, boundary)


def matched_null_stats(
    null_maps: list[np.ndarray],
    theta: Theta,
    seed: int,
    mode: str,
    nside: int | None,
) -> tuple[float, float, list[float]]:
    vals = []
    for null_id, null in enumerate(null_maps):
        local_rng = np.random.default_rng(seed + 10_000_019 * (theta.sample + 1) + null_id)
        vals.append(run_one(null, theta, local_rng, mode, nside)["score"])
    arr = np.asarray(vals, dtype=float)
    mu = float(np.mean(arr))
    sd = float(np.std(arr, ddof=1)) if len(arr) > 1 else float("nan")
    return mu, sd, vals


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def binned_phase_radius(
    phase: np.ndarray,
    radius: np.ndarray,
    values: np.ndarray,
    phase_bins: int = 24,
    radius_bins: int = 18,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p_edges = np.linspace(0.0, 1.0, phase_bins + 1)
    r_edges = np.geomspace(float(radius.min()), float(radius.max()), radius_bins + 1)
    grid = np.full((radius_bins, phase_bins), np.nan)
    for ri in range(radius_bins):
        rm = (radius >= r_edges[ri]) & (radius < r_edges[ri + 1])
        if ri == radius_bins - 1:
            rm = (radius >= r_edges[ri]) & (radius <= r_edges[ri + 1])
        for pi in range(phase_bins):
            pm = (phase >= p_edges[pi]) & (phase < p_edges[pi + 1])
            if pi == phase_bins - 1:
                pm = (phase >= p_edges[pi]) & (phase <= p_edges[pi + 1])
            m = rm & pm & np.isfinite(values)
            if np.any(m):
                grid[ri, pi] = float(np.mean(values[m]))
    return p_edges, r_edges, grid


def plots(rows: list[dict], outdir: Path) -> list[str]:
    import matplotlib.pyplot as plt

    outdir.mkdir(parents=True, exist_ok=True)
    files: list[str] = []

    radius = np.array([r["radius"] for r in rows], dtype=float)
    phase = np.array([r["phase"] for r in rows], dtype=float)
    score = np.array([r["score"] for r in rows], dtype=float)
    z = np.array([r["z_matched_null"] for r in rows], dtype=float)

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    sc = ax.scatter(radius, z, c=phase, s=10, alpha=0.65)
    ax.axhline(0.0, linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("occlusion radius")
    ax.set_ylabel("matched-null z(theta)")
    ax.set_title("Matched-null response over intervention scale")
    fig.colorbar(sc, ax=ax, label="intervention phase")
    p = outdir / "radius-zmatched.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))

    p_edges, r_edges, grid = binned_phase_radius(phase, radius, z)
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    mesh = ax.pcolormesh(p_edges, r_edges, grid, shading="auto")
    ax.set_yscale("log")
    ax.set_xlabel("phase")
    ax.set_ylabel("occlusion radius")
    ax.set_title("Mean matched-null z(theta) over phase × radius")
    fig.colorbar(mesh, ax=ax, label="mean z(theta)")
    p = outdir / "phase-radius-zmatched.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))

    labels = sorted(set((r["geometry"], r["occlusion"]) for r in rows))
    means = [
        np.nanmean(
            [
                r["z_matched_null"]
                for r in rows
                if (r["geometry"], r["occlusion"]) == label
            ]
        )
        for label in labels
    ]
    fig = plt.figure(figsize=(11, 5))
    ax = fig.add_subplot(111)
    ax.bar(np.arange(len(labels)), means)
    ax.axhline(0.0, linewidth=1)
    ax.set_xticks(
        np.arange(len(labels)),
        [f"{a}\n{b}" for a, b in labels],
        rotation=45,
        ha="right",
    )
    ax.set_ylabel("mean matched-null z(theta)")
    ax.set_title("Intervention-family excess after theta matching")
    p = outdir / "family-zmatched.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))

    # Keep raw score as a diagnostic so severity confounds stay visible.
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    ax.scatter(radius, score, c=phase, s=8, alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("occlusion radius")
    ax.set_ylabel("raw response score")
    ax.set_title("Diagnostic: raw response before matched-null normalization")
    p = outdir / "raw-radius-response.png"
    fig.tight_layout()
    fig.savefig(p, dpi=160)
    plt.close(fig)
    files.append(str(p))
    return files


def finite_summary(x: np.ndarray) -> dict[str, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return {"mean": float("nan"), "median": float("nan"), "std": float("nan")}
    return {
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
        "p95_abs": float(np.quantile(np.abs(x), 0.95)),
        "max_abs": float(np.max(np.abs(x))),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["synthetic", "healpix"], default="synthetic")
    ap.add_argument("--map-fits", type=Path)
    ap.add_argument("--field-index", type=int, default=0)
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--null-maps", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("--ny", type=int, default=192)
    ap.add_argument("--nx", type=int, default=384)
    ap.add_argument("--radius-min", type=float)
    ap.add_argument("--radius-max", type=float)
    ap.add_argument(
        "--output", type=Path, default=Path("pontifex-cmb-occlusion-mc.json")
    )
    ap.add_argument(
        "--rows", type=Path, default=Path("pontifex-cmb-occlusion-mc.csv")
    )
    ap.add_argument(
        "--plots", type=Path, default=Path("pontifex-cmb-occlusion-plots")
    )
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

    # Null skies are few; the large budget remains in theta sampling.
    null_maps = [
        make_null(field, np.random.default_rng(args.seed + 1_000_003 * (i + 1)))
        for i in range(args.null_maps)
    ]

    rows: list[dict] = []
    thetas = [sample_theta(rng, i, rmin, rmax) for i in range(args.samples)]
    for theta in thetas:
        observed_rng = np.random.default_rng(args.seed + 97_409 * (theta.sample + 1))
        metrics = run_one(field, theta, observed_rng, args.mode, nside)
        null_mu, null_sd, null_vals = matched_null_stats(
            null_maps, theta, args.seed, args.mode, nside
        )
        excess = float(metrics["score"] - null_mu)
        z = float(excess / null_sd) if np.isfinite(null_sd) and null_sd > 1e-12 else float("nan")
        rows.append(
            {
                **asdict(theta),
                **metrics,
                "null_mean_same_theta": null_mu,
                "null_std_same_theta": null_sd,
                "excess_same_theta": excess,
                "z_matched_null": z,
                "null_n": len(null_vals),
                "dataset": "observed" if args.mode == "healpix" else "synthetic",
            }
        )

    scores = np.asarray([r["score"] for r in rows], dtype=float)
    excess = np.asarray([r["excess_same_theta"] for r in rows], dtype=float)
    z = np.asarray([r["z_matched_null"] for r in rows], dtype=float)

    top = sorted(
        [r for r in rows if np.isfinite(r["z_matched_null"])],
        key=lambda x: abs(x["z_matched_null"]),
        reverse=True,
    )[:25]
    plot_files = plots(rows, args.plots)

    phase_active = [
        r for r in rows if r["occlusion"] == "adjacency_phase" or r["geometry"] == "ellipse"
    ]
    phase_corr = float("nan")
    if len(phase_active) >= 3:
        pa = np.asarray([r["phase"] for r in phase_active], dtype=float)
        pz = np.asarray([r["z_matched_null"] for r in phase_active], dtype=float)
        good = np.isfinite(pz)
        if np.count_nonzero(good) >= 3 and np.std(pz[good]) > 1e-12:
            # Circular phase is represented with first harmonic; report the larger
            # absolute correlation with sin/cos as a simple smoke diagnostic.
            c1 = np.corrcoef(np.sin(2 * np.pi * pa[good]), pz[good])[0, 1]
            c2 = np.corrcoef(np.cos(2 * np.pi * pa[good]), pz[good])[0, 1]
            phase_corr = float(max(abs(c1), abs(c2)))

    result = {
        "experiment": "CMB Acoustic Occlusion Stress Test — matched-theta Monte Carlo",
        "mode": args.mode,
        "seed": args.seed,
        "samples": args.samples,
        "null_maps": args.null_maps,
        "parameter_space": {
            "geometry": list(GEOMETRIES),
            "occlusion": list(OCCLUSIONS),
            "radius_min": rmin,
            "radius_max": rmax,
            "depth": [0.15, 1.0],
            "phase": [0.0, 1.0],
            "aspect": [0.5, 2.0],
        },
        "raw_response": {
            "mean": float(np.mean(scores)),
            "median": float(np.median(scores)),
        },
        "matched_null_excess": finite_summary(excess),
        "matched_null_z": finite_summary(z),
        "phase_active_first_harmonic_abs_corr": phase_corr,
        "top_abs_z_parameter_samples": top,
        "rows_csv": str(args.rows),
        "plots": plot_files,
        "interpretation_contract": {
            "primary_object": "theta -> z(theta), with each theta compared against the same theta on every null map",
            "phase_contract": "phase rotates anisotropic lesion orientation and the adjacency mapping for adjacency_phase; it is no longer a plotted-but-unused parameter",
            "monte_carlo_budget": "spent primarily on intervention parameters; null-map count is intentionally much smaller than theta count",
            "null_role": "matched-theta calibration; production HEALPix nulls must use C_l-matched synfast or a_lm phase randomization",
            "no_detection_claim": "large |z(theta)| is only a follow-up candidate until replicated across independent maps and stronger nulls",
            "next_step": "validate this harness on synthetic nulls, then run Planck with C_l-matched null skies and replicate surviving regions on ACT+Planck",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    save_csv(rows, args.rows)
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
