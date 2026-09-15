from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from connectome_generator import GeneratorConfig, make_adapter, simulate_connectome_generator
from connectome_generator_gpu import simulate_adapter_population_batch
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
    rows = np.asarray([2, 3, 4, 5, 6, 7], dtype=np.int32)
    cols = np.asarray([0, 1, 2, 3, 4, 5], dtype=np.int32)
    values = np.asarray([0.5, 0.5, 0.4, 0.4, 0.3, 0.3], dtype=np.float32)
    return sp.csr_matrix((values, (rows, cols)), shape=(8, 8), dtype=np.float32)


def test_population_batch_matches_scalar_reference_on_cpu() -> None:
    graph = toy_graph()
    interface = toy_interface()
    adapter = make_adapter(interface, seed=17, scale=0.15)
    starts = (
        FlyPose(1.0, 0.0, np.pi),
        FlyPose(0.0, 1.0, -np.pi / 2),
    )
    emitter = GeneratorConfig(spectral_scale=1.0)
    receiver = BrainConfig(spectral_scale=1.0, prime_scale=0.0)
    arena = ArenaConfig(dt=0.05, base_speed=0.05)

    batched = simulate_adapter_population_batch(
        graph,
        interface,
        (adapter,),
        starts,
        steps=20,
        emitter=emitter,
        receiver=receiver,
        arena=arena,
        device="cpu",
    )

    scalar = [
        simulate_connectome_generator(
            graph,
            interface,
            adapter,
            start,
            steps=20,
            emitter=emitter,
            receiver=receiver,
            arena=arena,
        ).metrics
        for start in starts
    ]

    for metric, values in batched.metrics.items():
        expected = np.asarray([row[metric] for row in scalar], dtype=np.float32)
        np.testing.assert_allclose(values[0], expected, rtol=2e-5, atol=2e-6)


def test_candidate_blocks_reuse_identical_receiver_starts() -> None:
    graph = toy_graph()
    interface = toy_interface()
    adapter = make_adapter(interface, seed=5, scale=0.1)
    starts = (FlyPose(1.0, 0.0, np.pi), FlyPose(-1.0, 0.0, 0.0))
    result = simulate_adapter_population_batch(
        graph,
        interface,
        (adapter, adapter),
        starts,
        steps=8,
        emitter=GeneratorConfig(spectral_scale=1.0),
        receiver=BrainConfig(spectral_scale=1.0, prime_scale=0.0),
        arena=ArenaConfig(dt=0.05, base_speed=0.05),
        device="cpu",
    )
    for values in result.metrics.values():
        np.testing.assert_allclose(values[0], values[1], rtol=0, atol=0)
