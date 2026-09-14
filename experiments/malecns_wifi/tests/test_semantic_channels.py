"""Tests for mixed-encoder hierarchical semantic channels."""

import numpy as np
import pytest

from malecns_wifi.semantic_channels import (
    bundle_channels,
    concatenated_view,
    project_channels,
    relation_channel,
)


def _rows(seed: int, rows: int, dims: int) -> np.ndarray:
    return np.random.default_rng(seed).normal(size=(rows, dims)).astype(np.float32)


def test_channels_from_different_encoders_may_have_different_widths() -> None:
    qwen = relation_channel(
        name="qwen-256-1024",
        encoder="qwen3-0.6b",
        child_scale=256,
        parent_scale=1024,
        child_embeddings=_rows(1, 5, 12),
        parent_embeddings=_rows(2, 5, 12),
    )
    minilm = relation_channel(
        name="minilm-64-256",
        encoder="minilm",
        child_scale=64,
        parent_scale=256,
        child_embeddings=_rows(3, 5, 7),
        parent_embeddings=_rows(4, 5, 7),
    )
    bundle = bundle_channels(qwen, minilm)
    values, slices = concatenated_view(bundle)

    assert bundle.names == ("qwen-256-1024", "minilm-64-256")
    assert qwen.width == 13  # alignment + 12-d residual
    assert minilm.width == 8
    assert values.shape == (5, 21)
    assert slices == ((0, 13), (13, 21))


def test_relation_is_only_formed_within_one_compatible_encoder_space() -> None:
    with pytest.raises(ValueError, match="same encoder"):
        relation_channel(
            name="invalid-cross-model",
            encoder="not-a-real-shared-space",
            child_scale=64,
            parent_scale=256,
            child_embeddings=_rows(1, 4, 7),
            parent_embeddings=_rows(2, 4, 12),
        )


def test_finer_level_can_have_multiple_ancestor_channels() -> None:
    child = _rows(1, 6, 10)
    near = relation_channel(
        name="256-512",
        encoder="encoder-a",
        child_scale=256,
        parent_scale=512,
        child_embeddings=child,
        parent_embeddings=_rows(2, 6, 10),
    )
    far = relation_channel(
        name="256-1024",
        encoder="encoder-a",
        child_scale=256,
        parent_scale=1024,
        child_embeddings=child,
        parent_embeddings=_rows(3, 6, 10),
    )
    bundle = bundle_channels(near, far)
    assert bundle.rows == 6
    assert len(bundle.channels) == 2


def test_mixed_channels_keep_total_drive_energy_fixed() -> None:
    first = relation_channel(
        name="a",
        encoder="one",
        child_scale=64,
        parent_scale=256,
        child_embeddings=_rows(1, 20, 8),
        parent_embeddings=_rows(2, 20, 8),
    )
    second = relation_channel(
        name="b",
        encoder="two",
        child_scale=256,
        parent_scale=1024,
        child_embeddings=_rows(3, 20, 13),
        parent_embeddings=_rows(4, 20, 13),
    )
    bundle = bundle_channels(first, second)
    rng = np.random.default_rng(5)
    projections = {
        "a": rng.normal(size=(32, first.width)).astype(np.float32),
        "b": rng.normal(size=(32, second.width)).astype(np.float32),
    }
    drive, diagnostics = project_channels(bundle, projections, target_total_rms=0.05)

    assert drive.shape == (32, 20)
    assert diagnostics["realised_total_rms"] == pytest.approx(0.05, rel=1e-5)
    assert set(diagnostics["channel_rms_before_mix"]) == {"a", "b"}


def test_adding_a_channel_does_not_buy_more_total_current() -> None:
    a = relation_channel(
        name="a",
        encoder="one",
        child_scale=64,
        parent_scale=256,
        child_embeddings=_rows(1, 10, 6),
        parent_embeddings=_rows(2, 10, 6),
    )
    b = relation_channel(
        name="b",
        encoder="two",
        child_scale=16,
        parent_scale=64,
        child_embeddings=_rows(3, 10, 9),
        parent_embeddings=_rows(4, 10, 9),
    )
    rng = np.random.default_rng(7)
    pa = rng.normal(size=(24, a.width)).astype(np.float32)
    pb = rng.normal(size=(24, b.width)).astype(np.float32)

    _, one = project_channels(bundle_channels(a), {"a": pa}, target_total_rms=0.05)
    _, two = project_channels(bundle_channels(a, b), {"a": pa, "b": pb}, target_total_rms=0.05)

    assert one["realised_total_rms"] == pytest.approx(0.05, rel=1e-5)
    assert two["realised_total_rms"] == pytest.approx(0.05, rel=1e-5)
