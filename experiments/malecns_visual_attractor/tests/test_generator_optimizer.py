from __future__ import annotations

import numpy as np

from connectome_generator import make_adapter
from generator_optimizer import (
    adapter_from_vector,
    adapter_to_vector,
    elite_center,
    mirrored_population,
    weighted_score,
)
from test_connectome_generator import toy_interface


def test_adapter_vector_roundtrip_is_exact() -> None:
    adapter = make_adapter(toy_interface(), seed=13, scale=0.2)
    vector = adapter_to_vector(adapter)
    restored = adapter_from_vector(adapter, vector)
    np.testing.assert_array_equal(restored.input_weight, adapter.input_weight)
    np.testing.assert_array_equal(restored.input_bias, adapter.input_bias)
    np.testing.assert_array_equal(restored.output_weight, adapter.output_weight)
    np.testing.assert_array_equal(restored.output_bias, adapter.output_bias)


def test_mirrored_population_contains_center_and_antithetic_pairs() -> None:
    center = np.arange(6, dtype=np.float32)
    pop = mirrored_population(center, sigma=0.1, population=5, seed=7)
    np.testing.assert_array_equal(pop[0], center)
    np.testing.assert_allclose(pop[1] + pop[3], 2 * center)
    np.testing.assert_allclose(pop[2] + pop[4], 2 * center)


def test_weighted_score_and_elite_center_are_explicit() -> None:
    summary = {
        "approach": np.asarray([0.1, 0.8, 0.6]),
        "orientation_fraction_30deg": np.asarray([0.2, 0.3, 0.9]),
    }
    score = weighted_score(summary, {"approach": 1.0, "orientation_fraction_30deg": 0.5})
    np.testing.assert_allclose(score, [0.2, 0.95, 1.05])
    vectors = np.asarray([[0.0], [1.0], [3.0]], dtype=np.float32)
    center = elite_center(vectors, score, elite=2)
    np.testing.assert_allclose(center, [2.0])
