"""Runtime for semantic trajectories plus counterfactual food through MaleCNS.

This module knows nothing about language models or gold spans. Its contract is two
synchronised time series prepared upstream:

* ``semantic_drive[t]``: the left-to-right semantic change of the text, already
  mapped to the chosen sensory population;
* ``food_drive[t]``: the non-negative population code derived from
  ``E(text+tag) - E(text)`` and mapped to the anatomically selected food neurons.

Keeping this boundary narrow matters scientifically: the exact same signals can
be replayed through the real connectome, topology nulls, the food-location null,
and a no-connectome control without changing the semantic encoder.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp


@dataclass(frozen=True)
class SemanticRuntimeResult:
    """Readout trajectory and auditable energy diagnostics."""

    readout_states: np.ndarray
    final_state: np.ndarray
    mean_state: np.ndarray
    recurrent_rms: float
    semantic_rms: float
    food_rms: float


def _validate_population(indices: np.ndarray, neurons: int, name: str) -> np.ndarray:
    values = np.asarray(indices, dtype=np.int64).reshape(-1)
    if values.size == 0:
        raise ValueError(f"{name} population is empty")
    if np.any(values < 0) or np.any(values >= neurons):
        raise ValueError(f"{name} population index outside operator")
    if np.unique(values).size != values.size:
        raise ValueError(f"{name} population contains duplicate indices")
    return values


def run_semantic_food(
    operator: sp.csr_matrix,
    semantic_drive: np.ndarray,
    sensory_indices: np.ndarray,
    food_drive: np.ndarray,
    food_indices: np.ndarray,
    readout_indices: np.ndarray,
    *,
    leak: float = 0.4,
    gain: float = 1.0,
) -> SemanticRuntimeResult:
    """Replay one semantic/food trajectory through a frozen sparse operator.

    ``semantic_drive`` has shape ``[time, n_sensory]`` and ``food_drive`` has shape
    ``[time, n_food]``. Both are external currents. The food channel is additive,
    so an anatomical-food condition and its matched random-location control can use
    byte-identical values and differ only in ``food_indices``.
    """
    matrix = sp.csr_matrix(operator, dtype=np.float32)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    neurons = matrix.shape[0]
    sensory = _validate_population(sensory_indices, neurons, "sensory")
    food = _validate_population(food_indices, neurons, "food")
    readout = _validate_population(readout_indices, neurons, "readout")

    semantic = np.asarray(semantic_drive, dtype=np.float32)
    appetitive = np.asarray(food_drive, dtype=np.float32)
    if semantic.ndim != 2 or semantic.shape[1] != sensory.size:
        raise ValueError("semantic_drive must have shape [time, len(sensory_indices)]")
    if appetitive.ndim != 2 or appetitive.shape[1] != food.size:
        raise ValueError("food_drive must have shape [time, len(food_indices)]")
    if semantic.shape[0] != appetitive.shape[0]:
        raise ValueError("semantic and food drives must have the same number of time steps")
    if not (0.0 < leak <= 1.0):
        raise ValueError("leak must be in (0, 1]")

    state = np.zeros(neurons, dtype=np.float32)
    trajectory = np.zeros((semantic.shape[0], readout.size), dtype=np.float32)
    recurrent_energy = 0.0
    semantic_energy = float(np.mean(semantic.astype(np.float64) ** 2)) if semantic.size else 0.0
    food_energy = float(np.mean(appetitive.astype(np.float64) ** 2)) if appetitive.size else 0.0

    current = np.zeros(neurons, dtype=np.float32)
    for step in range(semantic.shape[0]):
        current.fill(0.0)
        current[sensory] += semantic[step]
        current[food] += appetitive[step]
        recurrent = matrix @ state
        recurrent *= np.float32(gain)
        recurrent_energy += float(np.mean(recurrent.astype(np.float64) ** 2))
        pre = recurrent + current
        updated = (1.0 - leak) * state + leak * np.tanh(pre)
        state = updated.astype(np.float32, copy=False)
        trajectory[step] = state[readout]

    steps = max(semantic.shape[0], 1)
    return SemanticRuntimeResult(
        readout_states=trajectory,
        final_state=trajectory[-1].copy() if len(trajectory) else np.zeros(readout.size, dtype=np.float32),
        mean_state=trajectory.mean(axis=0) if len(trajectory) else np.zeros(readout.size, dtype=np.float32),
        recurrent_rms=float(np.sqrt(recurrent_energy / steps)),
        semantic_rms=float(np.sqrt(semantic_energy)),
        food_rms=float(np.sqrt(food_energy)),
    )


def direct_semantic_features(
    semantic_drive: np.ndarray,
    food_drive: np.ndarray,
) -> np.ndarray:
    """No-connectome control features from the exact same two input streams.

    This is intentionally topology-free. A learned direct control can consume
    these features with a parameter budget matched to the MaleCNS adapter. If this
    condition solves tagging equally well, the encoder/counterfactual food signal
    did the work rather than the connectome.
    """
    semantic = np.asarray(semantic_drive, dtype=np.float32)
    food = np.asarray(food_drive, dtype=np.float32)
    if semantic.ndim != 2 or food.ndim != 2 or semantic.shape[0] != food.shape[0]:
        raise ValueError("semantic and food drives must be aligned 2-D time series")
    joined = np.concatenate([semantic, food], axis=1)
    if len(joined) == 0:
        return np.zeros(joined.shape[1] * 2, dtype=np.float32)
    return np.concatenate([joined[-1], joined.mean(axis=0)]).astype(np.float32, copy=False)
