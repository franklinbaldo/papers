import numpy as np
import scipy.sparse as sp

from visual_attractor import (
    ArenaConfig,
    BrainConfig,
    FlyPose,
    Interface,
    StimulusSpec,
    capture_pass,
    radial_swarm,
    simulate,
    target_geometry,
    trajectory_metrics,
    visual_drive,
)


def toy():
    # visual L/R -> descending L/R
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


def test_geometry_shrinks_with_distance():
    stim = StimulusSpec("moving")
    near = target_geometry(FlyPose(1, 0, np.pi), stim, 0.0)
    far = target_geometry(FlyPose(2, 0, np.pi), stim, 0.0)
    assert near[1] > far[1]


def test_blank_has_no_visual_drive():
    _, interface = toy()
    drive = visual_drive(
        4,
        interface,
        FlyPose(1, 0, np.pi),
        StimulusSpec("blank", path="blank"),
        0.0,
        ArenaConfig(),
    )
    assert np.all(drive == 0)


def test_swarm_is_seed_deterministic():
    assert radial_swarm(flies=8, radius=1.0, seed=3) == radial_swarm(
        flies=8, radius=1.0, seed=3
    )


def test_simulation_is_deterministic():
    graph, interface = toy()
    args = dict(
        graph=graph,
        interface=interface,
        stimulus=StimulusSpec("moving"),
        start=FlyPose(1, 0, np.pi),
        steps=20,
        brain=BrainConfig(spectral_scale=1.0),
    )
    assert simulate(**args) == simulate(**args)


def test_trajectory_approach_is_half_distance_reduction():
    from visual_attractor import StepRecord

    rows = (
        StepRecord(0.1, 0, 0, 0, 0.75, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        StepRecord(0.2, 0, 0, 0, 0.49, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    )
    metrics = trajectory_metrics(rows, 1.0, 0.5)
    assert metrics["approach"] == 1.0
    assert metrics["near_time_fraction"] == 0.5


def test_capture_requires_absolute_and_control_margin():
    assert capture_pass(0.70, 0.55)
    assert not capture_pass(0.59, 0.10)
    assert not capture_pass(0.70, 0.65)
