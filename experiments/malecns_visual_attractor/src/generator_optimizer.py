from __future__ import annotations

from dataclasses import replace

import numpy as np

from connectome_generator import GeneratorAdapter


def adapter_to_vector(adapter: GeneratorAdapter) -> np.ndarray:
    return np.concatenate(
        [
            adapter.input_weight.ravel(),
            adapter.input_bias.ravel(),
            adapter.output_weight.ravel(),
            adapter.output_bias.ravel(),
        ]
    ).astype(np.float32, copy=False)


def adapter_from_vector(template: GeneratorAdapter, vector: np.ndarray) -> GeneratorAdapter:
    values = np.asarray(vector, dtype=np.float32).ravel()
    expected = template.trainable_parameters
    if values.size != expected:
        raise ValueError(f"adapter vector has {values.size} values, expected {expected}")
    cursor = 0

    def take(shape):
        nonlocal cursor
        size = int(np.prod(shape))
        out = values[cursor : cursor + size].reshape(shape).copy()
        cursor += size
        return out

    return replace(
        template,
        input_weight=take(template.input_weight.shape),
        input_bias=take(template.input_bias.shape),
        output_weight=take(template.output_weight.shape),
        output_bias=take(template.output_bias.shape),
    )


def mirrored_population(
    center: np.ndarray,
    *,
    sigma: float,
    population: int,
    seed: int,
) -> np.ndarray:
    """Center plus mirrored Gaussian perturbations for deterministic black-box ES."""
    center = np.asarray(center, dtype=np.float32).ravel()
    if sigma <= 0:
        raise ValueError("sigma must be > 0")
    if population < 3 or population % 2 == 0:
        raise ValueError("population must be odd and >= 3")
    rng = np.random.default_rng(seed)
    half = (population - 1) // 2
    noise = rng.normal(size=(half, center.size)).astype(np.float32)
    out = np.empty((population, center.size), dtype=np.float32)
    out[0] = center
    out[1 : 1 + half] = center + np.float32(sigma) * noise
    out[1 + half :] = center - np.float32(sigma) * noise
    return out


def weighted_score(summary: dict[str, np.ndarray], weights: dict[str, float]) -> np.ndarray:
    if not weights:
        raise ValueError("score weights cannot be empty")
    missing = sorted(set(weights) - set(summary))
    if missing:
        raise KeyError(f"score references missing metrics: {missing}")
    first = np.asarray(summary[next(iter(weights))], dtype=np.float64)
    score = np.zeros_like(first, dtype=np.float64)
    for name, weight in weights.items():
        values = np.asarray(summary[name], dtype=np.float64)
        if values.shape != score.shape:
            raise ValueError(f"metric shape mismatch for {name}: {values.shape} != {score.shape}")
        if not np.isfinite(values).all():
            raise ValueError(f"metric {name} contains non-finite values")
        score += float(weight) * values
    return score


def elite_center(population_vectors: np.ndarray, scores: np.ndarray, *, elite: int) -> np.ndarray:
    vectors = np.asarray(population_vectors, dtype=np.float32)
    score_values = np.asarray(scores, dtype=np.float64)
    if vectors.ndim != 2 or score_values.shape != (vectors.shape[0],):
        raise ValueError("population/scores shape mismatch")
    if not 1 <= elite <= vectors.shape[0]:
        raise ValueError("elite must be between 1 and population size")
    order = np.argsort(-score_values, kind="stable")
    return vectors[order[:elite]].mean(axis=0, dtype=np.float64).astype(np.float32)
