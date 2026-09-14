import numpy as np
import pytest
import scipy.sparse as sp

pytest.importorskip("torch")

from malecns_wifi.gpu_cache import compare_states, reservoir_states_multi_gain
from malecns_wifi.multitag import MultitagSpec, reservoir_states


def test_multi_gain_engine_matches_cpu_reference_on_toy_operator() -> None:
    operator = sp.csr_matrix(
        np.asarray(
            [
                [0.0, 0.20, 0.00, -0.10],
                [0.1, 0.00, 0.15, 0.00],
                [0.0, -0.05, 0.00, 0.20],
                [0.1, 0.00, 0.05, 0.00],
            ],
            dtype=np.float32,
        )
    )
    sensation = np.asarray(
        [[1.0, 0.0], [0.5, 0.5], [0.0, 1.0]], dtype=np.float32
    )
    input_indices = np.asarray([0, 2], dtype=np.int64)
    readout_indices = np.asarray([0, 1, 2, 3], dtype=np.int64)
    input_weights = np.asarray([[0.3, -0.1], [0.2, 0.4]], dtype=np.float32)
    gains = (0.0, 0.5, 0.95)

    batched = reservoir_states_multi_gain(
        operator,
        sensation,
        input_weights=input_weights,
        readout_indices=readout_indices,
        input_indices=input_indices,
        gains=gains,
        leak=0.4,
        steps_per_chunk=4,
        scale=0.7,
        device="cpu",
    )

    for gain in gains:
        spec = MultitagSpec(gain=gain, leak=0.4, steps_per_chunk=4)
        reference, _ = reservoir_states(
            operator,
            sensation,
            input_weights=input_weights,
            readout_indices=readout_indices,
            input_indices=input_indices,
            spec=spec,
            scale=0.7,
        )
        stats = compare_states(reference, batched[gain])
        assert stats.max_abs < 1e-6
        assert stats.relative_rmse < 1e-6
