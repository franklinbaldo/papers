from __future__ import annotations

import unittest

import numpy as np

from binary_alternatives import (
    Accumulator,
    _enumerative_plane_cost_table,
    huffman_weighted_bits,
    quantize_groups,
)


class BinaryAlternativeTests(unittest.TestCase):
    def test_huffman_cost(self) -> None:
        self.assertEqual(huffman_weighted_bits([5, 5]), 10)
        self.assertEqual(huffman_weighted_bits([10]), 10)
        self.assertEqual(huffman_weighted_bits([0, 0]), 0)

    def test_sparse_bitmap_wins_on_all_zero_block(self) -> None:
        acc = Accumulator(4)
        acc.add_groups(np.zeros((1, 128), dtype=np.int64))
        result = acc.result()
        self.assertLess(result["adaptive_bitmap_sparse_bits_per_weight"], 1.1)
        self.assertLess(result["adaptive_bitmap_sparse_ratio"], 0.3)

    def test_sparse_bitmap_falls_back_on_dense_block(self) -> None:
        acc = Accumulator(4)
        values = np.tile(np.array([1, -1], dtype=np.int64), 64).reshape(1, 128)
        acc.add_groups(values)
        result = acc.result()
        self.assertAlmostEqual(result["adaptive_bitmap_sparse_bits_per_weight"], 513 / 128)
        self.assertGreater(result["adaptive_bitmap_sparse_ratio"], 1.0)

    def test_bitplane_all_zero_has_special_mode(self) -> None:
        table = _enumerative_plane_cost_table(128)
        self.assertEqual(int(table[0]), 2)
        self.assertEqual(int(table[128]), 2)

    def test_quantizer_is_groupwise_and_bounded(self) -> None:
        groups = np.array([[0.0, 1.0, -1.0, 0.5], [0.0, 0.0, 0.0, 0.0]])
        quantized = quantize_groups(groups, 4)
        self.assertEqual(quantized.tolist()[0][:3], [0, 7, -7])
        self.assertEqual(quantized.tolist()[1], [0, 0, 0, 0])
        self.assertTrue(np.all(quantized <= 7))
        self.assertTrue(np.all(quantized >= -7))

    def test_accounting_is_deterministic(self) -> None:
        values = np.array(
            [[0, 1, 2, 3, 4, 5, 6, 7, 0, -1, -2, -3, -4, -5, -6, -7]],
            dtype=np.int64,
        )
        first = Accumulator(4)
        second = Accumulator(4)
        first.add_groups(values)
        second.add_groups(values)
        self.assertEqual(first.result(), second.result())


if __name__ == "__main__":
    unittest.main()
