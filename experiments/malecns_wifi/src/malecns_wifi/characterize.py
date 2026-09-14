"""Reservoir characterisation of a compiled connectome operator.

This module answers one question before any downstream task is designed: how much
of the recent input history does the MaleCNS operator hold, and does it hold more
than its own degree-preserving null or a random sparse operator of the same
density? It measures two things on each operator -- the spectral radius of the
linear part, and Jaeger's memory capacity -- and never touches a labelled task.

Conventions:
  * Operators are ``W[post, pre]`` CSR matrices, as emitted by :mod:`compiler`.
  * Operators are rescaled to unit spectral radius, so the ``gain`` argument *is*
    the spectral radius of the linear part of the update.
  * The update is ``x <- (1 - leak) * x + leak * tanh(gain * W x + w_in u)``.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from .runtime import load_graph


@dataclass(frozen=True)
class DriveSpec:
    """Input stream and simulation lengths for the memory-capacity probe."""

    washout: int = 200
    train_steps: int = 2500
    test_steps: int = 1000
    max_lag: int = 100
    readout_size: int = 512
    input_scale: float = 0.1
    ridge: float = 1e-6
    horizon_threshold: float = 0.1

    @property
    def total_steps(self) -> int:
        return self.washout + self.train_steps + self.test_steps


@dataclass(frozen=True)
class CharacterizeSpec:
    """Full grid: which operators, at which gains and leaks, over which seeds."""

    gains: tuple[float, ...] = (0.8, 1.0, 1.2)
    leaks: tuple[float, ...] = (1.0,)
    input_seeds: tuple[int, ...] = (0,)
    null_seed: int = 20260914
    power_iterations: int = 200
    power_tail: int = 20
    drive: DriveSpec = field(default_factory=DriveSpec)


# --- spectral radius -------------------------------------------------------


def spectral_radius(
    matrix: sp.csr_matrix,
    *,
    seed: int = 0,
    iterations: int = 200,
    tail: int = 20,
) -> dict:
    """Estimate ``|lambda_max|`` by the growth rate of the power iteration.

    The plain Rayleigh-quotient form of power iteration assumes a real dominant
    eigenvalue. A signed directed connectome has no such guarantee, so the
    estimate here is the growth of the norm, ``||W^k v||^(1/k)``, which converges
    to ``|lambda_max|`` even when the dominant pair is complex -- in that case the
    per-step ratio oscillates around the true modulus instead of settling, which
    is why the tail spread is reported alongside the estimate.
    """
    rng = np.random.default_rng(seed)
    n = matrix.shape[0]
    vector = rng.normal(size=n).astype(np.float64)
    vector /= np.linalg.norm(vector)
    ratios: list[float] = []

    for _ in range(iterations):
        product = matrix @ vector
        norm = float(np.linalg.norm(product))
        ratios.append(norm)
        if norm == 0.0:
            break
        vector = product / norm

    if not ratios or ratios[-1] == 0.0:
        return {"estimate": 0.0, "converged": True, "iterations": len(ratios), "tail_spread": 0.0}

    window = ratios[-min(tail, len(ratios)) :]
    estimate = float(np.exp(np.mean(np.log(window))))
    spread = float((max(window) - min(window)) / estimate) if estimate > 0 else 0.0
    return {
        "estimate": estimate,
        "last_ratio": float(ratios[-1]),
        "tail_min": float(min(window)),
        "tail_max": float(max(window)),
        "tail_spread": spread,
        "iterations": len(ratios),
        "converged": bool(spread < 1e-3),
        "note": "geometric mean of the last ||W^k v|| ratios; oscillation => complex dominant pair",
    }


def normalize_spectral_radius(matrix: sp.csr_matrix, radius: float) -> sp.csr_matrix:
    """Rescale so the linear part has unit spectral radius, leaving ``gain`` in charge."""
    scaled = matrix.copy()
    if radius > 1e-12:
        scaled.data = (scaled.data / np.float32(radius)).astype(np.float32, copy=False)
    return scaled


# --- null operators --------------------------------------------------------


def degree_preserving_null(matrix: sp.csr_matrix, *, seed: int) -> tuple[sp.csr_matrix, dict]:
    """Directed configuration model: rewire targets, keep every degree exact.

    Each edge keeps its presynaptic neuron, its weight and therefore its sign
    (the sign is a property of the presynaptic transmitter), and is handed a
    postsynaptic target drawn without replacement from the multiset of real
    postsynaptic endpoints. Out-degree and in-degree are preserved exactly per
    neuron; reciprocity, motifs and modularity are destroyed. Self-loops and
    parallel edges can appear and are reported rather than resampled away.
    """
    coo = matrix.tocoo()
    rng = np.random.default_rng(seed)
    rewired_rows = rng.permutation(coo.row)
    self_loops = int((rewired_rows == coo.col).sum())
    null = sp.csr_matrix((coo.data, (rewired_rows, coo.col)), shape=matrix.shape, dtype=np.float32)
    null.sum_duplicates()

    n = matrix.shape[0]
    in_degree_preserved = bool(
        np.array_equal(np.bincount(coo.row, minlength=n), np.bincount(rewired_rows, minlength=n))
    )
    stats = {
        "kind": "directed configuration model (postsynaptic endpoints permuted)",
        "seed": seed,
        "edges_before_merge": int(coo.nnz),
        "edges": int(null.nnz),
        "merged_parallel_edges": int(coo.nnz - null.nnz),
        "self_loops": self_loops,
        "in_degree_preserved": in_degree_preserved,
        "out_degree_preserved": True,  # presynaptic endpoints are never touched
        "preserves": ["in_degree", "out_degree", "weight_multiset", "presynaptic_sign"],
        "note": (
            "Degrees are exact before the rebuild; merged_parallel_edges counts the pairs that "
            "landed on the same (post, pre) cell and were summed. Merged pairs always share a "
            "presynaptic neuron, so per-neuron outgoing weight mass and sign survive the merge."
        ),
    }
    return null, stats


def random_esn(matrix: sp.csr_matrix, *, seed: int) -> tuple[sp.csr_matrix, dict]:
    """Random sparse operator with the same density and the same weight multiset.

    Strictly weaker than :func:`degree_preserving_null`: it also destroys the
    degree distribution, so it is the "would any sparse recurrent operator do?"
    control rather than the "does wiring specificity matter?" control.
    """
    rng = np.random.default_rng(seed)
    n = matrix.shape[0]
    nnz = matrix.nnz
    # int32, not the default int64: at 10M edges each index array is 39MB rather
    # than 82MB, and the CSR build would downcast them anyway.
    rows = rng.integers(0, n, size=nnz, dtype=np.int32)
    cols = rng.integers(0, n, size=nnz, dtype=np.int32)
    data = rng.permutation(matrix.data).astype(np.float32, copy=False)
    esn = sp.csr_matrix((data, (rows, cols)), shape=matrix.shape, dtype=np.float32)
    esn.sum_duplicates()
    stats = {
        "kind": "uniform random sparse operator, matched density and weight multiset",
        "seed": seed,
        "edges_before_merge": int(nnz),
        "edges": int(esn.nnz),
        "merged_parallel_edges": int(nnz - esn.nnz),
        "self_loops": int((rows == cols).sum()),
        "preserves": ["density", "weight_multiset"],
    }
    return esn, stats


# --- reservoir drive -------------------------------------------------------


def drive_reservoir(
    operator: sp.csr_matrix,
    *,
    gains: tuple[float, ...],
    leak: float,
    inputs: np.ndarray,
    input_weights: np.ndarray,
    probes: dict[str, np.ndarray],
    perturbation: np.ndarray,
) -> tuple[dict[tuple[float, str], np.ndarray], dict[float, np.ndarray], dict[float, dict]]:
    """Run every gain in one pass and return probe states plus ESP distances.

    All gains share one sparse matrix product: the states are stacked into a
    dense ``(n, 2 * len(gains))`` block and multiplied once per step, so the
    10M-edge operator is streamed from memory once instead of once per gain.
    Each gain gets two columns -- the trajectory proper and a replica started
    from a perturbed state -- and the distance between them is the echo state
    property check.
    """
    n = operator.shape[0]
    width = 2 * len(gains)
    gain_row = np.repeat(np.asarray(gains, dtype=np.float32), 2)[None, :]

    state = np.zeros((n, width), dtype=np.float32)
    state[:, 1::2] = perturbation[:, None]

    states = {
        (gain, name): np.empty((inputs.size, probe.size), dtype=np.float32)
        for gain in gains
        for name, probe in probes.items()
    }
    separation = {gain: np.empty(inputs.size, dtype=np.float32) for gain in gains}
    energy = {gain: np.zeros(n, dtype=np.float64) for gain in gains}

    for step, value in enumerate(inputs):
        pre = operator @ state
        pre *= gain_row
        for index, gain in enumerate(gains):
            energy[gain] += pre[:, 2 * index].astype(np.float64) ** 2
        pre += input_weights[:, None] * np.float32(value)
        state = ((1.0 - leak) * state + leak * np.tanh(pre)).astype(np.float32, copy=False)
        for index, gain in enumerate(gains):
            for name, probe in probes.items():
                states[(gain, name)][step] = state[probe, 2 * index]
            separation[gain][step] = np.linalg.norm(state[:, 2 * index] - state[:, 2 * index + 1])

    steps = max(inputs.size, 1)
    top = max(1, n // 100)
    drive = {}
    for gain, vector in energy.items():
        total = float(vector.sum())
        hottest = float(np.sort(vector)[-top:].sum())
        drive[gain] = {
            "recurrent_drive_rms": float(np.sqrt(total / (steps * n))),
            # If almost all recurrent energy sits in a hub sliver, a uniform readout
            # probe samples an operator that is inert where it happens to look.
            "recurrent_energy_top1pct_share": hottest / total if total > 0 else 0.0,
        }
    return states, separation, drive


def memory_capacity(states: np.ndarray, inputs: np.ndarray, spec: DriveSpec) -> dict:
    """Jaeger memory capacity from probe states, fitted on train and scored on test.

    ``MC_k`` is the squared Pearson correlation between ``u[t - k]`` and a linear
    readout of the state at ``t``. The readout is a ridge fit on the training
    segment and every reported ``r^2`` comes from the held-out test segment, so
    the number is not inflated by the readout dimension.
    """
    if spec.washout < spec.max_lag:
        raise ValueError("washout must cover max_lag so lagged targets never wrap around")
    lags = np.arange(1, spec.max_lag + 1)
    design = np.hstack([states.astype(np.float64), np.ones((states.shape[0], 1))])

    start = spec.washout
    train_slice = slice(start, start + spec.train_steps)
    test_slice = slice(start + spec.train_steps, start + spec.train_steps + spec.test_steps)

    targets = np.stack([np.roll(inputs, lag) for lag in lags], axis=1).astype(np.float64)
    x_train, x_test = design[train_slice], design[test_slice]
    y_train, y_test = targets[train_slice], targets[test_slice]

    gram = x_train.T @ x_train
    penalty = spec.ridge * float(np.trace(gram)) / gram.shape[0]
    weights = np.linalg.solve(gram + penalty * np.eye(gram.shape[0]), x_train.T @ y_train)
    predictions = x_test @ weights

    per_lag: list[float] = []
    for column in range(lags.size):
        predicted, actual = predictions[:, column], y_test[:, column]
        if predicted.std() < 1e-12 or actual.std() < 1e-12:
            per_lag.append(0.0)
            continue
        per_lag.append(float(np.corrcoef(predicted, actual)[0, 1] ** 2))

    floor_window = max(1, spec.max_lag // 10)
    noise_floor = float(np.mean(per_lag[-floor_window:]))
    above = [int(lag) for lag, value in zip(lags, per_lag, strict=True) if value >= spec.horizon_threshold]
    return {
        "memory_capacity": float(sum(per_lag)),
        "memory_capacity_above_floor": float(sum(max(0.0, value - noise_floor) for value in per_lag)),
        "effective_horizon_steps": max(above) if above else 0,
        "horizon_threshold": spec.horizon_threshold,
        "noise_floor": noise_floor,
        "r2_lag1": per_lag[0],
        "per_lag_r2": [round(value, 6) for value in per_lag],
        "readout_units": int(states.shape[1]),
        "ridge_penalty": penalty,
    }


# --- orchestration ---------------------------------------------------------


def characterize_operator(
    name: str,
    matrix: sp.csr_matrix,
    spec: CharacterizeSpec,
    *,
    extra: dict | None = None,
) -> dict:
    """Spectral radius plus a memory-capacity sweep for one operator."""
    started = time.perf_counter()
    radius = spectral_radius(
        matrix, seed=spec.null_seed, iterations=spec.power_iterations, tail=spec.power_tail
    )
    operator = normalize_spectral_radius(matrix, radius["estimate"])
    drive = spec.drive
    n = matrix.shape[0]

    # For an i.i.d. random sparse matrix the spectral radius tracks ||W||_F / sqrt(n).
    # A ratio far above 1 means one structured mode dominates a much smaller bulk, so
    # rescaling by rho leaves that bulk inert -- the concentration diagnostic below.
    frobenius = float(np.linalg.norm(matrix.data))
    bulk_scale = frobenius / np.sqrt(n)
    norms = {
        "frobenius": frobenius,
        "bulk_scale": bulk_scale,
        "spectral_concentration": radius["estimate"] / bulk_scale if bulk_scale > 0 else 0.0,
        "max_abs_row_sum": float(np.abs(matrix).sum(axis=1).max()),
        "mean_abs_row_sum": float(np.abs(matrix).sum(axis=1).mean()),
    }
    in_strength = np.asarray(np.abs(matrix).sum(axis=1)).ravel()

    sweep: list[dict] = []
    for leak in spec.leaks:
        for seed in spec.input_seeds:
            rng = np.random.default_rng(seed)
            inputs = rng.uniform(-1.0, 1.0, size=drive.total_steps).astype(np.float32)
            input_weights = (
                rng.uniform(-1.0, 1.0, size=n) * drive.input_scale
            ).astype(np.float32)
            size = min(drive.readout_size, n)
            probes = {
                "random": np.sort(rng.choice(n, size=size, replace=False)),
                # Control for the probe itself: if the operator concentrates its
                # computation in high-in-strength neurons, a uniform probe would
                # under-read a structured operator and over-read a random one.
                "hub": np.sort(np.argsort(in_strength)[-size:]),
            }
            perturbation = rng.uniform(-0.5, 0.5, size=n).astype(np.float32)

            input_rms = float(np.sqrt(np.mean(input_weights**2) * np.mean(inputs**2)))
            states, separation, drive_stats = drive_reservoir(
                operator,
                gains=spec.gains,
                leak=leak,
                inputs=inputs,
                input_weights=input_weights,
                probes=probes,
                perturbation=perturbation,
            )
            initial_separation = float(np.linalg.norm(perturbation))
            for gain in spec.gains:
                trace = separation[gain]
                stats = drive_stats[gain]
                for probe_name in probes:
                    probed = states[(gain, probe_name)]
                    entry = memory_capacity(probed, inputs, drive)
                    entry.update(
                        {
                            "gain": gain,
                            "leak": leak,
                            "input_seed": seed,
                            "probe": probe_name,
                            "esp_initial_separation": initial_separation,
                            "esp_final_separation": float(trace[-1]),
                            "echo_state_property": bool(
                                trace[-1] < 1e-3 * max(initial_separation, 1e-12)
                            ),
                            "state_rms": float(np.sqrt(np.mean(probed[drive.washout :] ** 2))),
                            "input_drive_rms": input_rms,
                            "recurrent_to_input_ratio": stats["recurrent_drive_rms"]
                            / max(input_rms, 1e-12),
                            "saturated_fraction": float(
                                np.mean(np.abs(probed[drive.washout :]) > 0.99)
                            ),
                            **stats,
                        }
                    )
                    sweep.append(entry)

    return {
        "operator": name,
        "neurons": int(n),
        "edges": int(matrix.nnz),
        "spectral_radius": radius,
        "operator_norms": norms,
        "sweep": sweep,
        "seconds": round(time.perf_counter() - started, 1),
        **({"null_stats": extra} if extra else {}),
    }


def characterize(
    graph_path: Path,
    output_path: Path,
    spec: CharacterizeSpec = CharacterizeSpec(),
) -> dict:
    """Characterise the real operator and both nulls, and write the report."""
    matrix = load_graph(graph_path)
    null, null_stats = degree_preserving_null(matrix, seed=spec.null_seed)
    esn, esn_stats = random_esn(matrix, seed=spec.null_seed + 1)

    report = {
        "format": "papers/malecns-characterization-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "graph": str(graph_path),
        "spec": {**asdict(spec), "drive": asdict(spec.drive)},
        "update_rule": "x <- (1 - leak) * x + leak * tanh(gain * W_hat x + w_in u), W_hat = W / rho(W)",
        "claim_boundary": (
            "Operator characterisation only: spectral radius and Jaeger memory capacity on "
            "i.i.d. input. No task, no labels, no claim about downstream accuracy. Memory "
            "capacity is bounded by the number of readout units, so every value here is the "
            "memory visible to a fixed-size probe of a much larger state, not the operator's "
            "total capacity; it is comparable across operators because the probe rule and "
            "size are identical, and is reported for both a uniform and a hub probe because "
            "a uniform probe alone would under-read an operator that concentrates its "
            "computation in high-in-strength neurons."
        ),
        "results": [
            characterize_operator("malecns", matrix, spec),
            characterize_operator("degree_preserving_null", null, spec, extra=null_stats),
            characterize_operator("random_esn", esn, spec, extra=esn_stats),
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def summary_table(report: dict) -> str:
    """Compact human-readable view of the sweep."""
    lines = [
        f"{'operator':<24}{'rho':>9}{'conc':>7}{'gain':>6}{'probe':>8}{'MC':>8}{'horizon':>8}"
        f"{'rec/in':>9}{'top1%':>7}{'sat':>7}{'ESP':>5}"
    ]
    for result in report["results"]:
        radius = result["spectral_radius"]["estimate"]
        concentration = result["operator_norms"]["spectral_concentration"]
        for entry in result["sweep"]:
            lines.append(
                f"{result['operator']:<24}{radius:>9.1f}{concentration:>7.1f}{entry['gain']:>6.2f}"
                f"{entry['probe']:>8}{entry['memory_capacity']:>8.2f}"
                f"{entry['effective_horizon_steps']:>8d}"
                f"{entry['recurrent_to_input_ratio']:>9.3f}"
                f"{entry['recurrent_energy_top1pct_share']:>7.3f}"
                f"{entry['saturated_fraction']:>7.3f}"
                f"{'yes' if entry['echo_state_property'] else 'no':>5}"
            )
    return "\n".join(lines)
