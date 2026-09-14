import numpy as np
import scipy.sparse as sp

from gpu_batch import simulate_stimulus_swarm_batch
from visual_attractor import (
    ArenaConfig,
    BrainConfig,
    FlyPose,
    Interface,
    StimulusSpec,
    simulate,
    trajectory_metrics,
)


def toy():
    rows = np.array([2, 3], dtype=np.int32)
    cols = np.array([0, 1], dtype=np.int32)
    data = np.array([1.0, 1.0], dtype=np.float32)
    graph = sp.csr_matrix((data, (rows, cols)), shape=(4, 4))
    interface = Interface(
        visual_indices=np.array([0, 1], dtype=np.int32),
        visual_azimuth=np.array([-0.5, 0.5], dtype=np.float32),
        descending_left=np.array([2], dtype=np.int32),
        descending_right=np.array([3], dtype=np.int32),
        steer_left=np.array([2], dtype=np.int32),
        steer_right=np.array([3], dtype=np.int32),
        forward_left=np.array([], dtype=np.int32),
        forward_right=np.array([], dtype=np.int32),
        courtship_indices=np.array([], dtype=np.int32),
    )
    return graph, interface


def test_batch_columns_preserve_matched_starts_and_cpu_metrics():
    graph, interface = toy()
    starts = (
        FlyPose(1.0, 0.0, np.pi),
        FlyPose(0.0, 1.0, -np.pi / 2),
    )
    stimuli = (
        StimulusSpec("moving"),
        StimulusSpec("static", path="static"),
    )
    brain = BrainConfig(spectral_scale=1.0)
    arena = ArenaConfig()
    result = simulate_stimulus_swarm_batch(
        graph,
        interface,
        stimuli,
        starts,
        steps=20,
        brain=brain,
        arena=arena,
        device="cpu",
    )
    assert result.trajectory["x"].shape == (20, 4)
    for stimulus_index, stimulus in enumerate(stimuli):
        for fly_index, start in enumerate(starts):
            cpu = simulate(
                graph,
                interface,
                stimulus,
                start,
                steps=20,
                brain=brain,
                arena=arena,
            )
            metrics = trajectory_metrics(
                cpu,
                float(np.hypot(start.x, start.y)),
                arena.near_radius,
            )
            column = stimulus_index * len(starts) + fly_index
            for key in metrics:
                np.testing.assert_allclose(
                    result.metrics[key][column],
                    metrics[key],
                    rtol=2e-5,
                    atol=2e-5,
                )


def test_batch_summary_keeps_stimuli_separate():
    graph, interface = toy()
    result = simulate_stimulus_swarm_batch(
        graph,
        interface,
        (StimulusSpec("blank", path="blank"), StimulusSpec("moving")),
        (FlyPose(1, 0, np.pi),),
        steps=5,
        brain=BrainConfig(spectral_scale=1.0),
        device="cpu",
    )
    summary = result.stimulus_summary()
    assert set(summary) == {"blank", "moving"}
    assert summary["blank"]["initial_distance"] == 1.0
