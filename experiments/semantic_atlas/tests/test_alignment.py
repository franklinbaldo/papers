from __future__ import annotations

import numpy as np
import pytest

from semantic_atlas.alignment import (
    complement_indices,
    deterministic_folds,
    fit_affine_ridge,
    fit_regularized_cca,
    knn_overlap,
    local_distance_correlation,
    row_cosine,
    summarize_metrics,
)


def _synthetic_pair(seed: int = 7):
    rng = np.random.default_rng(seed)
    calibration = 60
    heldout = 18
    latent_dim = 6
    reference_dim = 14
    transfer_dim = 11
    latent = rng.normal(size=(calibration + heldout, latent_dim))
    reference_projection = rng.normal(size=(latent_dim, reference_dim))
    transfer_projection = rng.normal(size=(latent_dim, transfer_dim))
    reference = latent @ reference_projection + 0.03 * rng.normal(
        size=(calibration + heldout, reference_dim)
    )
    transfer = latent @ transfer_projection + 0.03 * rng.normal(
        size=(calibration + heldout, transfer_dim)
    )
    canonical = latent[:, :latent_dim]
    canonical /= np.linalg.norm(canonical, axis=1, keepdims=True)
    return (
        reference[:calibration],
        transfer[:calibration],
        canonical[:calibration],
        reference[calibration:],
        transfer[calibration:],
        canonical[calibration:],
    )


def test_affine_ridge_generalizes_on_paired_linear_spaces():
    _, transfer_cal, canonical_cal, _, transfer_held, canonical_held = _synthetic_pair()
    alignment = fit_affine_ridge(transfer_cal, canonical_cal, alpha=0.1)
    predicted = alignment.transform(transfer_held)
    assert row_cosine(canonical_held, predicted) > 0.98
    metrics = summarize_metrics(canonical_held, predicted, knn_values=(3, 5))
    assert metrics["coordinate_rmse"] < 0.08
    assert metrics["local_distance_correlation"] > 0.95


def test_regularized_cca_recovers_shared_signal():
    ref_cal, transfer_cal, canonical_cal, _, transfer_held, canonical_held = _synthetic_pair()
    alignment = fit_regularized_cca(
        ref_cal,
        transfer_cal,
        canonical_cal,
        regularization=0.05,
        components=6,
    )
    predicted = alignment.transform(transfer_held)
    assert row_cosine(canonical_held, predicted) > 0.98
    assert local_distance_correlation(canonical_held, predicted) > 0.95


def test_shuffled_correspondence_destroys_affine_signal():
    _, transfer_cal, canonical_cal, _, transfer_held, canonical_held = _synthetic_pair()
    rng = np.random.default_rng(991)
    shuffled = canonical_cal[rng.permutation(len(canonical_cal))]
    paired = fit_affine_ridge(transfer_cal, canonical_cal, alpha=0.1).transform(transfer_held)
    negative = fit_affine_ridge(transfer_cal, shuffled, alpha=0.1).transform(transfer_held)
    assert row_cosine(canonical_held, paired) > row_cosine(canonical_held, negative) + 0.5


def test_folds_are_deterministic_disjoint_and_complete():
    paths = [f"doc-{index}.md" for index in range(23)]
    folds_a = deterministic_folds(paths, folds=5)
    folds_b = deterministic_folds(paths, folds=5)
    assert [fold.tolist() for fold in folds_a] == [fold.tolist() for fold in folds_b]
    observed = np.concatenate(folds_a)
    assert sorted(observed.tolist()) == list(range(len(paths)))
    for fold in folds_a:
        train = complement_indices(len(paths), fold)
        assert not set(train.tolist()) & set(fold.tolist())
        assert len(train) + len(fold) == len(paths)


def test_knn_overlap_is_one_for_identical_geometry():
    rng = np.random.default_rng(12)
    values = rng.normal(size=(15, 4))
    assert knn_overlap(values, values.copy(), k=4) == pytest.approx(1.0)


def test_bad_cca_configuration_fails_before_any_evaluation():
    reference = np.eye(4)
    transfer = np.eye(4)
    targets = np.eye(4)
    with pytest.raises(ValueError, match="regularization"):
        fit_regularized_cca(reference, transfer, targets, regularization=0.0, components=2)
    with pytest.raises(ValueError, match="rank bound"):
        fit_regularized_cca(reference, transfer, targets, regularization=0.1, components=4)
