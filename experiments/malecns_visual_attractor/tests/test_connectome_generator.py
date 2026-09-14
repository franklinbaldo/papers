from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from connectome_generator import (
    CONTEXT_DIM,
    GeneratorConfig,
    generator_step,
    make_adapter,
    receiver_context,
    simulate_connectome_generator,
)
from visual_attractor import ArenaConfig, BrainConfig, FlyPose, Interface


def toy_interface() -> Interface:
    return Interface(
        visual_indices=np.asarray([0, 1], dtype=np.int32),
        visual_azimuth=np.asarray([-0.5, 0.5], dtype=np.float32),
        descending_left=np.asarray([4, 6], dtype=np.int32),
        descending_right=np.asarray([5, 7], dtype=np.int32),
        steer_left=np.asarray([4], dtype=np.int32),
        steer_right=np.asarray([5], dtype=np.int32),
        forward_left=np.asarray([6], dtype=np.int32),
        forward_right=np.asarray([7], dtype=np.int32),
        courtship_indices=np.asarray([], dtype=np.int32),
    )


def toy_graph() -> sp.csr_matrix:
    # Visual cells feed the readout side through a tiny recurrent chain.
    rows = np.asarray([2, 3, 4, 5, 6, 7], dtype=np.int32)
    cols = np.asarray([0, 1, 2, 3, 4, 5], dtype=np.int32)
    values = np.asarray([0.5, 0.5, 0.4, 0.4, 0.3, 0.3], dtype=np.float32)
    return sp.csr_matrix((values, (rows, cols)), shape=(8, 8), dtype=np.float32)


def test_adapter_is_deterministic_and_explicitly_parameter_counted() -> None:
    interface = toy_interface()
    left = make_adapter(interface, seed=7)
    right = make_adapter(interface, seed=7)
    assert np.array_equal(left.input_weight, right.input_weight)
    assert np.array_equal(left.output_weight, right.output_weight)
    expected = (
        len(interface.visual_indices) * CONTEXT_DIM
        + len(interface.visual_indices)
        + 4 * len(np.unique(np.concatenate([interface.descending_left, interface.descending_right])))
        + 4
    )
    assert left.trainable_parameters == expected


def test_receiver_context_exposes_geometry_not_receiver_neural_state() -> None:
    context = receiver_context(
        FlyPose(1.0, 0.0, np.pi),
        distance_scale=2.0,
        previous_radial_velocity=0.25,
    )
    assert context.shape == (CONTEXT_DIM,)
    assert np.isfinite(context).all()
    assert context[0] == 0.5


def test_generator_step_keeps_emitter_graph_frozen_and_outputs_bounded_controls() -> None:
    graph = toy_graph()
    interface = toy_interface()
    adapter = make_adapter(interface, seed=3, scale=0.1)
    state = np.zeros(graph.shape[0], dtype=np.float32)
    context = receiver_context(FlyPose(1.0, 0.0, np.pi), distance_scale=1.0)
    next_state, frame = generator_step(
        graph,
        state,
        context,
        adapter,
        GeneratorConfig(spectral_scale=1.0),
    )
    assert next_state.shape == state.shape
    assert np.isfinite(next_state).all()
    assert -np.deg2rad(35.0) <= frame.bearing_offset_rad <= np.deg2rad(35.0)
    assert 0.5 <= frame.size_scale <= 2.0
    assert 0.0 <= frame.contrast <= 1.0
    assert 0.0 <= frame.temporal_gate <= 1.0


def test_closed_loop_emitter_receiver_rollout_retains_generated_frames_and_behaviour() -> None:
    graph = toy_graph()
    interface = toy_interface()
    adapter = make_adapter(interface, seed=11, scale=0.2)
    rollout = simulate_connectome_generator(
        graph,
        interface,
        adapter,
        FlyPose(1.0, 0.0, np.pi),
        steps=12,
        emitter=GeneratorConfig(spectral_scale=1.0),
        receiver=BrainConfig(spectral_scale=1.0, prime_scale=0.0),
        arena=ArenaConfig(dt=0.05, base_speed=0.05),
    )
    assert len(rollout.records) == 12
    assert len(rollout.generated) == 12
    assert np.isfinite([record.distance for record in rollout.records]).all()
    assert set(rollout.metrics) >= {
        "normalized_distance_reduction",
        "orientation_fraction_30deg",
        "approach",
    }
