from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from gpu_batch import scipy_csr_to_torch
from screen_reward_loop import ScreenGeometry
from visual_attractor import ArenaConfig, Interface


def load_runner():
    path = Path(__file__).parents[1] / "scripts" / "run_visual_efficiency_curriculum.py"
    spec = spec_from_file_location("visual_efficiency_runner", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_energy_matched_runner_smoke_cpu(tmp_path):
    runner = load_runner()
    graph = sp.eye(8, dtype=np.float32, format="csr") * np.float32(0.05)
    interface = Interface(
        visual_indices=np.asarray([0, 1, 2, 3], dtype=np.int32),
        visual_azimuth=np.asarray([-0.5, -0.15, 0.15, 0.5], dtype=np.float32),
        descending_left=np.asarray([4, 6], dtype=np.int32),
        descending_right=np.asarray([5, 7], dtype=np.int32),
        steer_left=np.asarray([4], dtype=np.int32),
        steer_right=np.asarray([5], dtype=np.int32),
        forward_left=np.asarray([6], dtype=np.int32),
        forward_right=np.asarray([7], dtype=np.int32),
        courtship_indices=np.asarray([], dtype=np.int32),
    )
    geometry = ScreenGeometry(
        bodies=np.asarray([101, 102, 103, 104], dtype=np.int64),
        x=np.asarray([-0.5, -0.15, 0.15, 0.5], dtype=np.float32),
        y=np.asarray([-0.1, 0.1, -0.1, 0.1], dtype=np.float32),
        resolved=np.asarray([True, True, True, True]),
        eye=np.asarray([-1, -1, 1, 1], dtype=np.int8),
    )
    rng = np.random.default_rng(3)
    weights = rng.normal(0.0, 0.2, size=(2, 6, 6)).astype(np.float32)
    result = runner.run_stage(
        graph=graph,
        interface=interface,
        geometry=geometry,
        sparse=scipy_csr_to_torch(graph, device="cpu"),
        weights_np=weights,
        flies=2,
        steps=3,
        radius=0.75,
        heading_offset_deg=30.0,
        budget=0.1,
        start_seed=5,
        generator_seed=6,
        spectral_scale=1.0,
        gain=1.0,
        leak=0.2,
        visual_scale=0.5,
        reward_scale=0.08,
        reward_feedback_gain=100.0,
        latent_gain=100.0,
        telemetry_every=0,
        arena=ArenaConfig(dt=0.02),
        device="cpu",
        progress_path=tmp_path / "progress.jsonl",
        permutation_seed=7,
    )
    assert result["cumulative_reward"].shape == (4, 2)
    assert result["advantage"].shape == (2,)
    assert result["approach"].shape == (4, 2)
    assert result["final_distance"].shape == (4, 2)
    assert 0 <= result["winner"] < 2
    assert np.isfinite(result["cumulative_reward"]).all()
