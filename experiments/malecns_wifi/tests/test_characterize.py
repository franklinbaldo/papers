import numpy as np
import scipy.sparse as sp

from malecns_wifi.characterize import (
    CharacterizeSpec,
    DriveSpec,
    characterize_operator,
    degree_preserving_null,
    random_esn,
    spectral_radius,
)


def _random_sparse(n: int = 120, density: float = 0.05, seed: int = 3) -> sp.csr_matrix:
    rng = np.random.default_rng(seed)
    dense = rng.normal(size=(n, n)).astype(np.float32)
    dense[rng.random((n, n)) > density] = 0.0
    return sp.csr_matrix(dense)


def _cyclic_delay_line(n: int = 32) -> sp.csr_matrix:
    """Unit-spectral-radius shift register: state of node i moves to node i+1."""
    rows = (np.arange(n) + 1) % n
    cols = np.arange(n)
    return sp.csr_matrix(
        (np.ones(n, dtype=np.float32), (rows, cols)), shape=(n, n), dtype=np.float32
    )


def test_spectral_radius_matches_dense_eigenvalues() -> None:
    matrix = _random_sparse()
    truth = float(np.abs(np.linalg.eigvals(matrix.toarray())).max())
    estimate = spectral_radius(matrix, iterations=400, tail=40)["estimate"]
    assert abs(estimate - truth) / truth < 0.02


def test_spectral_radius_of_nilpotent_operator_is_zero() -> None:
    chain = sp.csr_matrix(np.diag(np.ones(10, dtype=np.float32), k=-1))
    assert spectral_radius(chain, iterations=50)["estimate"] < 1e-6


def _column_sums(matrix: sp.csr_matrix) -> np.ndarray:
    return np.asarray(matrix.sum(axis=0)).ravel()


def test_degree_preserving_null_keeps_both_degree_sequences() -> None:
    matrix = _random_sparse()
    null, stats = degree_preserving_null(matrix, seed=7)
    assert stats["in_degree_preserved"]
    assert stats["out_degree_preserved"]
    assert stats["merged_parallel_edges"] == matrix.nnz - null.nnz
    # Merged pairs share a presynaptic neuron, so outgoing weight mass survives exactly.
    assert np.allclose(_column_sums(matrix), _column_sums(null), atol=1e-4)


def test_degree_preserving_null_actually_rewires() -> None:
    matrix = _random_sparse()
    null, _ = degree_preserving_null(matrix, seed=11)
    shared = (matrix != 0).multiply(null != 0).nnz
    assert shared < 0.1 * matrix.nnz


def test_random_esn_matches_density_and_total_weight() -> None:
    matrix = _random_sparse()
    esn, stats = random_esn(matrix, seed=5)
    assert stats["edges_before_merge"] == matrix.nnz
    assert matrix.nnz - esn.nnz == stats["merged_parallel_edges"]
    # Collisions follow the birthday bound; at connectome density they are negligible.
    expected_collisions = matrix.nnz**2 / (2 * matrix.shape[0] ** 2)
    assert stats["merged_parallel_edges"] < 3 * expected_collisions
    # Summing collided cells conserves the signed total even when it merges entries.
    assert abs(float(esn.sum()) - float(matrix.sum())) < 1e-2


def test_memory_capacity_separates_delay_line_from_memoryless_operator() -> None:
    spec = CharacterizeSpec(
        gains=(0.9,),
        leaks=(1.0,),
        input_seeds=(0,),
        power_iterations=200,
        drive=DriveSpec(
            washout=120,
            train_steps=600,
            test_steps=300,
            max_lag=20,
            readout_size=32,
            input_scale=1.0,
        ),
    )
    delay = characterize_operator("delay", _cyclic_delay_line(32), spec)
    memoryless = characterize_operator("zero", sp.csr_matrix((32, 32), dtype=np.float32), spec)

    assert {entry["probe"] for entry in delay["sweep"]} == {"random", "hub"}
    for probe in ("random", "hub"):
        delayed = next(e for e in delay["sweep"] if e["probe"] == probe)
        flat = next(e for e in memoryless["sweep"] if e["probe"] == probe)
        assert delayed["memory_capacity"] > 5.0
        assert flat["memory_capacity"] < 1.0
        assert delayed["effective_horizon_steps"] > flat["effective_horizon_steps"]
        assert delayed["echo_state_property"]


def test_memory_capacity_rejects_washout_shorter_than_max_lag() -> None:
    import pytest

    spec = CharacterizeSpec(
        gains=(0.9,),
        drive=DriveSpec(washout=5, train_steps=50, test_steps=20, max_lag=20, readout_size=8),
    )
    with pytest.raises(ValueError, match="washout"):
        characterize_operator("bad", _cyclic_delay_line(8), spec)


def test_partial_degree_preserving_null_preserves_degrees_and_scales_rewiring() -> None:
    from malecns_wifi.characterize import partial_degree_preserving_null
    import pytest

    matrix = _random_sparse(n=100, density=0.1, seed=42)

    # p = 0: identical
    null_0, stats_0 = partial_degree_preserving_null(matrix, p=0.0, seed=1)
    assert stats_0["rewired_edges"] == 0
    assert (null_0 != matrix).nnz == 0

    # p = 1: all edges rewired
    null_1, stats_1 = partial_degree_preserving_null(matrix, p=1.0, seed=1)
    assert stats_1["in_degree_preserved"]
    assert stats_1["out_degree_preserved"]
    assert stats_1["rewired_edges"] == matrix.nnz

    # intermediate p values: degree preservation and monotonic rewiring
    null_small, stats_small = partial_degree_preserving_null(matrix, p=0.10, seed=1)
    null_large, stats_large = partial_degree_preserving_null(matrix, p=0.50, seed=1)

    assert stats_small["in_degree_preserved"]
    assert stats_small["out_degree_preserved"]
    assert stats_large["in_degree_preserved"]
    assert stats_large["out_degree_preserved"]

    # column sums (out-degree mass) preserved exactly
    assert np.allclose(_column_sums(matrix), _column_sums(null_small), atol=1e-4)
    assert np.allclose(_column_sums(matrix), _column_sums(null_large), atol=1e-4)

    # Overlap with original matrix should decrease as p increases
    overlap_0 = (matrix != 0).multiply(null_0 != 0).nnz
    overlap_small = (matrix != 0).multiply(null_small != 0).nnz
    overlap_large = (matrix != 0).multiply(null_large != 0).nnz
    overlap_1 = (matrix != 0).multiply(null_1 != 0).nnz

    assert overlap_0 == matrix.nnz
    assert overlap_0 > overlap_small > overlap_large > overlap_1

    # invalid p values raise ValueError
    with pytest.raises(ValueError, match="rewiring fraction p"):
        partial_degree_preserving_null(matrix, p=-0.1, seed=1)
    with pytest.raises(ValueError, match="rewiring fraction p"):
        partial_degree_preserving_null(matrix, p=1.1, seed=1)

