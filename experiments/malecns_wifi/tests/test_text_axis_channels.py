import numpy as np

from malecns_wifi.text_axis_channels import (
    byte_aligned_scale,
    elementwise_ratio,
    interpolate_to_bytes,
    utf8_byte_axis,
    vector_relations,
)


def test_utf8_byte_axis_preserves_character_boundaries() -> None:
    axis = utf8_byte_axis("aç🙂")
    assert axis.byte_length == len("aç🙂".encode("utf-8"))
    assert axis.char_to_byte.tolist() == [0, 1, 3, 7]


def test_interpolation_fills_every_byte_with_full_vector() -> None:
    anchors = np.asarray([[0.0, 10.0], [10.0, 30.0]], dtype=np.float32)
    centres = np.asarray([1.0, 5.0])
    field = interpolate_to_bytes(anchors, centres, byte_length=7)

    assert field.shape == (7, 2)
    np.testing.assert_allclose(field[0], anchors[0])
    np.testing.assert_allclose(field[1], anchors[0])
    np.testing.assert_allclose(field[3], [5.0, 20.0])
    np.testing.assert_allclose(field[5], anchors[1])
    np.testing.assert_allclose(field[6], anchors[1])


def test_byte_aligned_scale_uses_window_centres() -> None:
    spans = np.asarray([[0, 4], [4, 8]], dtype=np.int64)
    anchors = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    field = byte_aligned_scale(anchors, spans, byte_length=8)

    assert field.shape == (8, 2)
    assert field[0, 0] > field[0, 1]
    assert field[-1, 1] > field[-1, 0]
    np.testing.assert_allclose(field[3] + field[4], [1.0, 1.0], atol=1e-6)


def test_ratio_is_an_embedding_shaped_channel_not_a_scalar() -> None:
    left = np.asarray([[2.0, -4.0, 1.0]], dtype=np.float32)
    right = np.asarray([[1.0, -2.0, 0.5]], dtype=np.float32)
    ratio = elementwise_ratio(left, right)

    assert ratio.shape == left.shape
    np.testing.assert_allclose(ratio, [[2.0, 2.0, 2.0]])


def test_vector_relations_preserve_every_coordinate() -> None:
    left = np.asarray([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    right = np.asarray([[2.0, 1.0], [1.5, 8.0]], dtype=np.float32)
    channels = vector_relations(left, right)

    assert set(channels) == {"ratio", "difference", "product"}
    assert all(value.shape == left.shape for value in channels.values())
