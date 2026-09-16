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
import scipy.sparse.linalg as sla

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


def leading_eigenpairs(matrix: sp.csr_matrix, *, k: int = 3, tol: float = 1e-9) -> dict:
    """Leading eigenvalues and right/left eigenvectors via ARPACK.

    Preferred over power iteration on this operator. MaleCNS has a near-degenerate
    leading pair (3776.27 and 3718.80 -- the symmetric and antisymmetric
    combination of two hemisphere-local modes), so power iteration converges as
    ``(lambda_2/lambda_1)^k = 0.9848^k`` and needs hundreds of iterations for a
    percent. ARPACK returns the whole leading subspace in seconds.

    Left eigenvectors come from the transpose, and are what a spectral projector
    needs: the projector onto mode ``i`` is ``v_i u_i^T / (u_i . v_i)``.
    """
    operator = matrix.astype(np.float64)
    k = min(k, matrix.shape[0] - 2)
    values, right = sla.eigs(operator, k=k, which="LM", maxiter=20000, tol=tol)
    left_values, left = sla.eigs(operator.T.tocsr(), k=k, which="LM", maxiter=20000, tol=tol)

    order = np.argsort(-np.abs(values))
    left_order = np.argsort(-np.abs(left_values))
    return {
        "eigenvalues": [complex(values[i]) for i in order],
        "left_eigenvalues": [complex(left_values[i]) for i in left_order],
        "right": right[:, order],
        "left": left[:, left_order],
        "estimate": float(np.abs(values[order[0]])),
        "method": "arpack",
    }


def spectral_radius(
    matrix: sp.csr_matrix,
    *,
    seed: int = 0,
    iterations: int = 200,
    tail: int = 20,
    method: str = "arpack",
) -> dict:
    """Estimate ``|lambda_max|`` by the growth rate of the power iteration.

    The plain Rayleigh-quotient form of power iteration assumes a real dominant
    eigenvalue. A signed directed connectome has no such guarantee, so the
    estimate here is the growth of the norm, ``||W^k v||^(1/k)``, which converges
    to ``|lambda_max|`` even when the dominant pair is complex -- in that case the
    per-step ratio oscillates around the true modulus instead of settling, which
    is why the tail spread is reported alongside the estimate.
    """
    if (
        method == "arpack"
        and sp.issparse(matrix)
        and matrix.shape[0] > 3
        and matrix.nnz > 0
    ):
        try:
            pair = leading_eigenpairs(matrix, k=min(3, matrix.shape[0] - 2))
            values, estimate = pair["eigenvalues"], pair["estimate"]
            # ARPACK returns numerical noise on nilpotent and strongly defective
            # operators, where "largest magnitude" is degenerate at zero. The
            # eigenpair residual catches that: a real eigenpair has a small one.
            leading = pair["right"][:, 0]
            residual = float(
                np.linalg.norm(matrix @ leading - values[0] * leading) / max(estimate, 1e-300)
            )
            # Cross-check against the norm growth rate, which is an honest estimator
            # exactly where ARPACK is not: it goes to zero on a nilpotent operator.
            probe = np.random.default_rng(seed).normal(size=matrix.shape[0])
            probe /= np.linalg.norm(probe)
            for _ in range(40):
                probe = matrix @ probe
                norm = float(np.linalg.norm(probe))
                if norm == 0.0:
                    break
                probe /= norm
            growth = norm if norm > 0 else 0.0
            if residual < 1e-6 and growth > 0.5 * estimate:
                second = abs(values[1]) if len(values) > 1 else 0.0
                return {
                    "estimate": estimate,
                    "method": "arpack",
                    "converged": True,
                    "residual": residual,
                    "growth_cross_check": growth,
                    "leading_eigenvalues": [[v.real, v.imag] for v in values],
                    "degeneracy_ratio": second / estimate if estimate else 0.0,
                }
        except (sla.ArpackNoConvergence, sla.ArpackError, ValueError):
            pass  # fall through to power iteration

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
        return {
            "estimate": 0.0,
            "method": "power_iteration",
            "converged": True,
            "iterations": len(ratios),
            "tail_spread": 0.0,
        }

    window = ratios[-min(tail, len(ratios)) :]
    estimate = float(np.exp(np.mean(np.log(window))))
    spread = float((max(window) - min(window)) / estimate) if estimate > 0 else 0.0
    return {
        "estimate": estimate,
        "method": "power_iteration",
        "last_ratio": float(ratios[-1]),
        "tail_min": float(min(window)),
        "tail_max": float(max(window)),
        "tail_spread": spread,
        "iterations": len(ratios),
        "converged": bool(spread < 1e-3),
        "note": "geometric mean of the last ||W^k v|| ratios; oscillation => complex dominant pair",
    }


class DeflatedOperator:
    """``W`` with its leading spectral modes projected out, applied matrix-free.

    Not a null model -- it is a question. The two leading MaleCNS modes are
    hemisphere-local and enormous relative to the bulk; removing them asks what the
    rest of the wiring does on its own, which no degree-preserving rewiring can
    answer because no rewiring reproduces that geometry.

    The rank-k correction stays factored rather than materialised: ``W`` minus a
    dense 165k x 165k update is not representable, but ``W x - sum_i lambda_i v_i
    (u_i . x) / (u_i . v_i)`` costs one extra O(n) pass per mode. Left eigenvectors
    are required -- for a non-symmetric operator the spectral projector is
    ``v u^T / (u . v)``, not ``v v^T``.
    """

    def __init__(self, matrix: sp.csr_matrix, *, modes: int = 2, tol: float = 1e-9,
                 scale: float = 1.0):
        pair = leading_eigenpairs(matrix, k=max(modes + 2, 4), tol=tol)
        self.matrix = matrix
        self.shape = matrix.shape
        self.nnz = matrix.nnz
        self.modes = modes
        self.scale = np.float32(scale)

        values = pair["eigenvalues"]
        right_all, left_all = pair["right"], pair["left"]
        # ARPACK returns the left and right spectra in their own orders, and near
        # degeneracy makes index-matching wrong. Pair them by eigenvalue instead.
        kept_right, kept_left, kept_values = [], [], []
        used: set[int] = set()
        for index in range(min(modes, len(values))):
            value = values[index]
            # Only real modes are deflated with a real rank-1 projector. A complex
            # pair spans a two-dimensional real invariant subspace and cannot be
            # removed this way; deflating its real part alone is not a projector
            # and can make the spectral radius grow.
            if abs(value.imag) > 1e-6 * max(abs(value), 1e-300):
                continue
            candidates = [
                j for j in range(left_all.shape[1])
                if j not in used and abs(pair["left_eigenvalues"][j] - value) < 1e-6 * abs(value)
            ]
            if not candidates:
                continue
            j = candidates[0]
            used.add(j)
            right = np.real(right_all[:, index]).astype(np.float64)
            left = np.real(left_all[:, j]).astype(np.float64)
            overlap = float(left @ right)
            if abs(overlap) < 1e-8:
                continue
            kept_right.append(right)
            kept_left.append(left / overlap)
            kept_values.append(float(value.real))

        self.right = (
            np.stack(kept_right, axis=1).astype(np.float32)
            if kept_right
            else np.zeros((matrix.shape[0], 0), dtype=np.float32)
        )
        self.left = (
            np.stack(kept_left, axis=1).astype(np.float32)
            if kept_left
            else np.zeros((matrix.shape[0], 0), dtype=np.float32)
        )
        self.values = np.asarray(kept_values, dtype=np.float32)
        self.eigenvalues = [complex(v) for v in values[:modes]]
        self.deflated_modes = len(kept_values)
        self.skipped_complex_modes = modes - self.deflated_modes

    def __matmul__(self, state: np.ndarray) -> np.ndarray:
        flat = state.ndim == 1
        columns = state[:, None] if flat else state
        product = self.matrix @ columns
        if self.deflated_modes:
            coefficients = self.left.T @ columns          # (modes, batch)
            product = product - self.right @ (self.values[:, None] * coefficients)
        product = product * self.scale
        return product[:, 0] if flat else product

    def rescaled(self, scale: float) -> "DeflatedOperator":
        """Same deflation, different overall scale, without redoing the eigensolve."""
        clone = object.__new__(DeflatedOperator)
        clone.__dict__.update(self.__dict__)
        clone.scale = np.float32(scale)
        return clone

    def stats(self) -> dict:
        return {
            "kind": f"leading-{self.modes}-mode deflation of the real operator",
            "deflated_modes": self.deflated_modes,
            "skipped_complex_modes": self.skipped_complex_modes,
            "deflated_eigenvalues": [[v.real, v.imag] for v in self.eigenvalues],
            "note": "an ablation, not a null: asks what the bulk does without the slow modes",
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


@dataclass(frozen=True)
class ModeLoading:
    """How much of the state sits in the leading modes, and whether they clamp."""

    projections: np.ndarray
    mass_weighted_saturation: np.ndarray
    mode_saturation: np.ndarray
    echo_state_separation: float
    echo_state_property: bool
    eigenvalues: list


def measure_mode_loading(
    operator,
    leading,
    *,
    gain: float,
    leak: float = 0.4,
    steps: int = 600,
    input_indices: np.ndarray | None = None,
    input_scale: float = 1.0,
    seed: int = 0,
) -> ModeLoading:
    """Drive the operator and watch the leading modes directly.

    ``sat_all`` answers "is any of the brain clamped", which is not the question
    the hemispheric-mode hypothesis asks. This projects the state onto each
    leading right eigenvector, ``v_k^T x_t``, and weights saturation by the mass
    each mode carries, so "the two slow modes are the thing that clamps" becomes
    checkable rather than inferred from a global fraction.

    ``leading`` is the dict from :func:`leading_eigenpairs` on the *same*
    normalised operator that ``gain`` multiplies.
    """
    rng = np.random.default_rng(seed)
    n = operator.shape[0]
    modes = np.real(leading["right"]).astype(np.float32)
    modes = modes / np.maximum(np.linalg.norm(modes, axis=0, keepdims=True), 1e-12)

    if input_indices is None:
        input_indices = np.arange(n)
    weights = np.zeros(n, dtype=np.float32)
    weights[input_indices] = rng.normal(size=len(input_indices)).astype(np.float32) * input_scale

    # Two trajectories from different starts, same input: the echo state check.
    state = np.zeros((n, 2), dtype=np.float32)
    state[:, 1] = rng.uniform(-0.5, 0.5, size=n).astype(np.float32)
    initial = float(np.linalg.norm(state[:, 1]))

    projections = np.empty((steps, modes.shape[1]), dtype=np.float32)
    weighted = np.zeros(modes.shape[1], dtype=np.float64)

    for step in range(steps):
        drive = weights[:, None] * np.float32(rng.uniform(-1.0, 1.0))
        pre = (operator @ state) * np.float32(gain) + drive
        state = ((1.0 - leak) * state + leak * np.tanh(pre)).astype(np.float32, copy=False)

        primary = state[:, 0]
        projections[step] = modes.T @ primary
        clamped = np.abs(primary) > 0.99
        # Saturation as each mode sees it: the share of that mode's own mass that
        # is pinned, rather than the share of all 165k neurons.
        mass = modes**2
        weighted += (mass[clamped].sum(axis=0) / np.maximum(mass.sum(axis=0), 1e-12)).astype(
            np.float64
        )

    separation = float(np.linalg.norm(state[:, 0] - state[:, 1]))
    return ModeLoading(
        projections=projections,
        mass_weighted_saturation=(weighted / max(steps, 1)).astype(np.float32),
        mode_saturation=np.abs(projections).max(axis=0).astype(np.float32),
        echo_state_separation=separation,
        echo_state_property=bool(separation < 1e-3 * max(initial, 1e-12)),
        eigenvalues=[[complex(v).real, complex(v).imag] for v in leading["eigenvalues"]],
    )


def mode_loading_sweep(
    matrix: sp.csr_matrix,
    gains,
    *,
    leak: float = 0.4,
    steps: int = 600,
    modes: int = 3,
    seed: int = 0,
) -> dict:
    """Mode loading, mass-weighted saturation and ESP across a gain grid.

    The operator is normalised to unit spectral radius once, so ``gain`` is the
    spectral radius of the linear part and the grid is directly comparable with
    the task-side gain grid.
    """
    leading = leading_eigenpairs(matrix, k=max(modes, 3))
    normalised = normalize_spectral_radius(matrix, leading["estimate"])
    unit = leading_eigenpairs(normalised, k=max(modes, 3))

    rows = []
    for gain in gains:
        loading = measure_mode_loading(
            normalised, unit, gain=gain, leak=leak, steps=steps, seed=seed
        )
        per_mode = np.sqrt((loading.projections**2).mean(axis=0))
        # With an exactly degenerate leading pair the individual eigenvectors are an
        # arbitrary basis of the same 2-D invariant subspace, so per-mode loadings
        # are not interpretable on their own. The subspace total is.
        degenerate = abs(unit["eigenvalues"][1]) / max(abs(unit["eigenvalues"][0]), 1e-300) > 0.999
        rows.append(
            {
                "gain": float(gain),
                "leading_subspace_rms": float(np.sqrt((per_mode[:2] ** 2).sum())),
                "leading_pair_degenerate": bool(degenerate),
                "leading_subspace_saturation": float(
                    np.mean(loading.mass_weighted_saturation[:2])
                ),
                "mode_rms": [float(x) for x in per_mode],
                "mode_peak": [float(x) for x in loading.mode_saturation],
                "mass_weighted_saturation": [float(x) for x in loading.mass_weighted_saturation],
                "echo_state_separation": loading.echo_state_separation,
                "echo_state_property": loading.echo_state_property,
            }
        )
    return {
        "spectral_radius": leading["estimate"],
        "eigenvalues": [[complex(v).real, complex(v).imag] for v in leading["eigenvalues"]],
        "degeneracy_ratio": (
            abs(leading["eigenvalues"][1]) / leading["estimate"] if leading["estimate"] else 0.0
        ),
        "leak": leak,
        "steps": steps,
        "sweep": rows,
    }


@dataclass(frozen=True)
class LeadingSubspace:
    """Basis-invariant handle on the leading invariant subspace.

    With an exactly degenerate leading pair, ARPACK's ``v1`` and ``v2`` are an
    arbitrary basis of one plane and a rerun can rotate within it. Everything here
    is a property of the *subspace*, so nothing depends on which vector ARPACK
    happened to call first.
    """

    right: np.ndarray
    left_scaled: np.ndarray
    participation: np.ndarray
    dimension: int
    eigenvalues: list
    degenerate: bool

    def project(self, state: np.ndarray) -> np.ndarray:
        """``P x`` with ``P = V (U^T V)^-1 U^T``, kept factored."""
        columns = state[:, None] if state.ndim == 1 else state
        projected = self.right @ (self.left_scaled.T @ columns)
        return projected[:, 0] if state.ndim == 1 else projected


def _real_invariant_basis(values, vectors, dimension: int) -> np.ndarray:
    """Real basis of the leading invariant subspace.

    A complex conjugate pair contributes ``real(v)`` and ``imag(v)``, which span
    the same two real dimensions. Taking the two conjugate columns instead gives
    the *same* vector twice -- ``real(v) == real(conj(v))`` -- and a rank-deficient
    block whose projector does not exist.
    """
    columns: list[np.ndarray] = []
    consumed: set[int] = set()
    for index, value in enumerate(values):
        if len(columns) >= dimension:
            break
        if index in consumed:
            continue
        scale = max(abs(value), 1e-300)
        if abs(value.imag) < 1e-9 * scale:
            columns.append(np.real(vectors[:, index]))
            continue
        columns.append(np.real(vectors[:, index]))
        if len(columns) < dimension:
            columns.append(np.imag(vectors[:, index]))
        for other in range(index + 1, len(values)):
            if other not in consumed and abs(values[other] - np.conj(value)) < 1e-9 * scale:
                consumed.add(other)
                break
    if len(columns) < dimension:
        raise ValueError(f"only {len(columns)} independent leading directions available")
    return np.stack(columns[:dimension], axis=1).astype(np.float64)


def leading_subspace(matrix, *, dimension: int = 2, tol: float = 1e-9) -> LeadingSubspace:
    """Spectral projector onto the leading ``dimension`` modes.

    The right and left leading vectors are taken as blocks rather than paired
    one-to-one: for a degenerate cluster the pairing is ill-defined but the spans
    are not, and ``U^T V`` is invertible whenever the subspace is not defective.

    ``participation[i]`` is neuron ``i``'s share of the subspace's spatial support,
    ``||Q[i, :]||^2`` for an orthonormal basis ``Q`` of the right subspace. It is
    the weight to use when asking how much of *this subspace* is clamped, rather
    than how much of the brain is.
    """
    pair = leading_eigenpairs(matrix, k=max(dimension + 2, 4), tol=tol)
    right = _real_invariant_basis(pair["eigenvalues"], pair["right"], dimension)
    left = _real_invariant_basis(pair["left_eigenvalues"], pair["left"], dimension)

    overlap = left.T @ right
    if abs(np.linalg.det(overlap)) < 1e-12:
        raise ValueError("leading subspace is defective or left/right blocks do not overlap")
    left_scaled = left @ np.linalg.inv(overlap).T

    orthonormal, _ = np.linalg.qr(right)
    participation = np.sum(orthonormal**2, axis=1)

    values = pair["eigenvalues"]
    degenerate = (
        abs(values[1]) / max(abs(values[0]), 1e-300) > 0.999 if len(values) > 1 else False
    )
    return LeadingSubspace(
        right=right.astype(np.float32),
        left_scaled=left_scaled.astype(np.float32),
        participation=participation.astype(np.float32),
        dimension=dimension,
        eigenvalues=[[complex(v).real, complex(v).imag] for v in values[:dimension]],
        degenerate=bool(degenerate),
    )


def linear_mode_multiplier(gain: float, leak: float, eigenvalue: float = 1.0) -> float:
    """``mu = 1 - leak + leak * gain * lambda``: the linearised per-step growth.

    On a unit-spectral-radius operator the leading mode's linearised multiplier is
    ``0.6 + 0.4 * gain`` at leak 0.4, so the linear stability threshold sits at
    ``gain = 1`` regardless of how large the spectral radius was before
    normalisation. Anything measured above that is the nonlinearity deciding how
    the divergence is bounded, not whether it happens.
    """
    return float(1.0 - leak + leak * gain * eigenvalue)


def measure_subspace_dynamics(
    operator,
    subspace: LeadingSubspace,
    *,
    gain: float,
    leak: float = 0.4,
    steps: int = 400,
    input_indices: np.ndarray | None = None,
    input_scale: float = 1.0,
    seed: int = 0,
) -> dict:
    """Subspace loading, participation-weighted saturation, and a split ESP test.

    The echo state check is reported separately inside and outside the subspace,
    which answers a question a single distance cannot: is it the global integrator
    that loses the echo state property, or the bulk?
    """
    rng = np.random.default_rng(seed)
    n = operator.shape[0]
    if input_indices is None:
        input_indices = np.arange(n)
    weights = np.zeros(n, dtype=np.float32)
    weights[input_indices] = rng.normal(size=len(input_indices)).astype(np.float32) * input_scale

    state = np.zeros((n, 2), dtype=np.float32)
    state[:, 1] = rng.uniform(-0.5, 0.5, size=n).astype(np.float32)
    initial = float(np.linalg.norm(state[:, 1]))

    participation = subspace.participation
    total_participation = float(participation.sum())
    loading, fraction, saturation = [], [], []

    for _ in range(steps):
        drive = weights[:, None] * np.float32(rng.uniform(-1.0, 1.0))
        pre = (operator @ state) * np.float32(gain) + drive
        state = ((1.0 - leak) * state + leak * np.tanh(pre)).astype(np.float32, copy=False)

        primary = state[:, 0]
        inside = float(np.linalg.norm(subspace.project(primary)))
        magnitude = float(np.linalg.norm(primary))
        loading.append(inside)
        fraction.append(inside / magnitude if magnitude > 1e-12 else 0.0)
        clamped = np.abs(primary) > 0.99
        saturation.append(
            float(participation[clamped].sum() / total_participation)
            if total_participation > 0
            else 0.0
        )

    difference = state[:, 0] - state[:, 1]
    inside_difference = subspace.project(difference)
    return {
        "gain": float(gain),
        "linear_multiplier": linear_mode_multiplier(gain, leak),
        "subspace_loading_rms": float(np.sqrt(np.mean(np.square(loading)))),
        "subspace_fraction_mean": float(np.mean(fraction)),
        "subspace_fraction_final": float(fraction[-1]) if fraction else 0.0,
        "participation_weighted_saturation": float(np.mean(saturation)),
        "participation_weighted_saturation_final": float(saturation[-1]) if saturation else 0.0,
        "esp_separation_subspace": float(np.linalg.norm(inside_difference)),
        "esp_separation_bulk": float(np.linalg.norm(difference - inside_difference)),
        "esp_separation_total": float(np.linalg.norm(difference)),
        "echo_state_property": bool(np.linalg.norm(difference) < 1e-3 * max(initial, 1e-12)),
        "degenerate_leading_pair": subspace.degenerate,
    }


def subspace_sweep(
    matrix: sp.csr_matrix,
    gains,
    *,
    leak: float = 0.4,
    steps: int = 400,
    dimension: int = 2,
    input_indices: np.ndarray | None = None,
    input_scale: float = 1.0,
    seed: int = 0,
    label: str = "isotropic",
) -> dict:
    """Run :func:`measure_subspace_dynamics` across a gain grid on one drive regime."""
    radius = leading_eigenpairs(matrix, k=3)["estimate"]
    normalised = normalize_spectral_radius(matrix, radius)
    subspace = leading_subspace(normalised, dimension=dimension)
    return {
        "label": label,
        "spectral_radius": radius,
        "leading_eigenvalues": subspace.eigenvalues,
        "degenerate_leading_pair": subspace.degenerate,
        "drive": {
            "neurons": int(len(input_indices) if input_indices is not None else matrix.shape[0]),
            "input_scale": input_scale,
        },
        "leak": leak,
        "steps": steps,
        "sweep": [
            measure_subspace_dynamics(
                normalised,
                subspace,
                gain=gain,
                leak=leak,
                steps=steps,
                input_indices=input_indices,
                input_scale=input_scale,
                seed=seed,
            )
            for gain in gains
        ],
    }
