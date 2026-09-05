from __future__ import annotations

import unittest

from experiment import (
    decode_quantized,
    decode_stream,
    encode_quantized,
    encode_stream,
    measure_quantized,
    quantize,
    synthetic_values,
)


class TernaryEndEncodingTests(unittest.TestCase):
    def test_every_4bit_value_round_trips(self) -> None:
        for value in range(-7, 8):
            self.assertEqual(decode_quantized(encode_quantized(value, 4), 4), value)

    def test_concatenated_stream_is_self_delimiting(self) -> None:
        values = [0, 4, -6, 1, 0, -7]
        self.assertEqual(decode_stream(encode_stream(values, 4), 4), values)

    def test_uniform_control_does_not_create_a_fake_information_win(self) -> None:
        values = synthetic_values("uniform", 20_000, 20_260_831)
        metrics = measure_quantized(quantize(values, 8), 8)
        self.assertGreater(metrics.capacity_ratio, 1.0)

    def test_sparse_control_can_cross_information_threshold(self) -> None:
        values = synthetic_values("sparse_uniform", 20_000, 20_260_831)
        metrics = measure_quantized(quantize(values, 8), 8)
        self.assertLess(metrics.capacity_ratio, 1.0)
        self.assertGreater(metrics.packed_2bit_ratio, 1.0)


if __name__ == "__main__":
    unittest.main()
