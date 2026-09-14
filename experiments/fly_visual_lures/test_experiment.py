from math import isnan

from experiment import (
    FlyObservation,
    attraction_by_sector,
    mutate,
    paired_scene_delta,
    radial_swarm,
    random_pattern,
    scene_summary,
)


WEIGHTS = {
    "orientation": 1.0,
    "approach": 1.0,
    "dwell": 1.0,
    "landing": 1.0,
    "avoidance": 1.0,
}


def test_same_swarm_seed_reuses_exact_initial_conditions() -> None:
    assert radial_swarm(flies=16, radius=5.0, seed=7) == radial_swarm(
        flies=16, radius=5.0, seed=7
    )
    assert radial_swarm(flies=16, radius=5.0, seed=7) != radial_swarm(
        flies=16, radius=5.0, seed=8
    )


def test_pattern_mutation_is_reproducible_and_preserves_binary_printability() -> None:
    base = random_pattern(size=8, seed=1)
    a = mutate(base, flips=5, seed=2)
    b = mutate(base, flips=5, seed=2)
    assert a == b
    assert set(a.pixels) <= {0, 1}


def test_scene_summary_keeps_lower_tail_visible() -> None:
    observations = tuple(
        FlyObservation(i, float(i), 0.0, 1.0, 1.0, 1.0 if i else 0.0, 0.0, 0.0)
        for i in range(8)
    )
    summary = scene_summary(observations, WEIGHTS)
    assert summary["flies"] == 8
    assert summary["lower_quartile_score"] <= summary["median_score"] <= summary["mean_score"]


def test_attraction_field_can_expose_empty_and_weak_sectors() -> None:
    observations = (
        FlyObservation(0, 1.0, 0.0, 1, 1, 1, 0, 0),
        FlyObservation(1, -1.0, 0.0, 0, 0, 0, 0, 1),
    )
    sectors = attraction_by_sector(observations, WEIGHTS, sectors=4)
    assert len(sectors) == 4
    assert any(isnan(value) for value in sectors)
    finite = [value for value in sectors if not isnan(value)]
    assert max(finite) > min(finite)


def test_paired_scene_delta_uses_scene_aggregates() -> None:
    assert paired_scene_delta({"mean_score": 2.0}, {"mean_score": 0.5}) == 1.5
