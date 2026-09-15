import numpy as np
import scipy.sparse as sp

from gpu_batch import simulate_stimulus_swarm_batch
from visual_attractor import BrainConfig, FlyPose, Interface, StimulusSpec


def toy():
    rows = np.array([2, 3], dtype=np.int32)
    cols = np.array([0, 1], dtype=np.int32)
    data = np.array([1.0, 1.0], dtype=np.float32)
    graph = sp.csr_matrix((data, (rows, cols)), shape=(4, 4))
    interface = Interface(
        visual_indices=np.array([0, 1], dtype=np.int32),
        # Keep the toy receptors inside the narrow central target footprint so
        # this test checks stimulus separation rather than float32 underflow.
        visual_azimuth=np.array([-0.02, 0.02], dtype=np.float32),
        descending_left=np.array([2], dtype=np.int32),
        descending_right=np.array([3], dtype=np.int32),
        steer_left=np.array([2], dtype=np.int32),
        steer_right=np.array([3], dtype=np.int32),
        forward_left=np.array([], dtype=np.int32),
        forward_right=np.array([], dtype=np.int32),
        courtship_indices=np.array([], dtype=np.int32),
    )
    return graph, interface


def test_blank_has_zero_visual_rms_while_moving_has_drive():
    graph, interface = toy()
    result = simulate_stimulus_swarm_batch(
        graph,
        interface,
        (StimulusSpec("blank", path="blank"), StimulusSpec("moving")),
        (FlyPose(1.0, 0.0, np.pi),),
        steps=8,
        brain=BrainConfig(spectral_scale=1.0),
        device="cpu",
    )
    blank = result.trajectory["visual_rms"][:, 0]
    moving = result.trajectory["visual_rms"][:, 1]
    assert np.all(blank == 0.0)
    assert np.any(moving > 0.0)


def test_blank_and_moving_do_not_share_the_same_visual_trace():
    graph, interface = toy()
    result = simulate_stimulus_swarm_batch(
        graph,
        interface,
        (StimulusSpec("blank", path="blank"), StimulusSpec("moving")),
        (FlyPose(1.0, 0.0, np.pi),),
        steps=8,
        brain=BrainConfig(spectral_scale=1.0),
        device="cpu",
    )
    assert not np.array_equal(
        result.trajectory["visual_rms"][:, 0],
        result.trajectory["visual_rms"][:, 1],
    )
