import numpy as np

from semantic_atlas.inverse import (
    InferenceMemory,
    InferenceRecord,
    interpolate_with_generator,
)


def test_position_only_lookup_recovers_nearby_token_distribution():
    memory = InferenceMemory(
        [
            InferenceRecord(np.array([0.0, 0.0]), token_id=10, text="alpha"),
            InferenceRecord(np.array([0.1, 0.0]), token_id=10, text="alpha2"),
            InferenceRecord(np.array([2.0, 0.0]), token_id=20, text="beta"),
        ]
    )
    distribution = memory.token_distribution(np.array([0.05, 0.0]), k=2, bandwidth=0.2)
    assert max(distribution, key=distribution.get) == 10


def test_stored_topk_preserves_more_than_sampled_token():
    memory = InferenceMemory(
        [
            InferenceRecord(
                np.array([0.0]),
                token_id=1,
                text="one",
                topk={1: 0.6, 2: 0.4},
            )
        ]
    )
    distribution = memory.token_distribution(np.array([0.0]), k=1, bandwidth=1.0)
    assert distribution == {1: 0.6, 2: 0.4}


def test_route_conditioning_prefers_neighbor_moving_in_requested_direction():
    forward = InferenceRecord(
        state=np.array([0.0, 0.0]),
        token_id=1,
        text="forward",
        next_state=np.array([1.0, 0.0]),
    )
    backward = InferenceRecord(
        state=np.array([0.0, 0.0]),
        token_id=2,
        text="backward",
        next_state=np.array([-1.0, 0.0]),
    )
    memory = InferenceMemory([forward, backward])
    distribution = memory.token_distribution(
        np.array([0.0, 0.0]),
        k=2,
        desired_delta=np.array([1.0, 0.0]),
        bandwidth=1.0,
        route_weight=3.0,
    )
    assert distribution[1] > distribution[2]


def test_entropy_falls_when_zoom_selects_tighter_neighborhood():
    records = [
        InferenceRecord(np.array([0.00]), 1, "a"),
        InferenceRecord(np.array([0.02]), 1, "a2"),
        InferenceRecord(np.array([0.50]), 2, "b"),
        InferenceRecord(np.array([0.70]), 3, "c"),
    ]
    memory = InferenceMemory(records)
    coarse = memory.lexical_entropy(np.array([0.01]), k=4, bandwidth=1.0)
    fine = memory.lexical_entropy(np.array([0.01]), k=2, bandwidth=0.05)
    assert fine < coarse


def test_llm_interpolation_is_verified_by_reembedding_not_midpoint_assumption():
    neighbors = InferenceMemory(
        [
            InferenceRecord(np.array([0.0]), 1, "left"),
            InferenceRecord(np.array([2.0]), 2, "right"),
        ]
    ).query(np.array([1.0]), k=2, bandwidth=2.0)

    candidates = iter(["bad", "near", "worse"])

    def synthesize(records):
        return next(candidates)

    locations = {
        "bad": np.array([4.0]),
        "near": np.array([1.1]),
        "worse": np.array([-2.0]),
    }
    text, distance = interpolate_with_generator(
        np.array([1.0]),
        neighbors,
        synthesize=synthesize,
        embed=lambda text: locations[text],
        attempts=3,
    )
    assert text == "near"
    assert distance < 0.11
