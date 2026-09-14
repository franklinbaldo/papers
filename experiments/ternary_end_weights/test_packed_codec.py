from __future__ import annotations

import itertools
import tempfile
import unittest
from pathlib import Path

import numpy as np

from packed_codec import (
    BPEWriter,
    FixedReader,
    FixedWriter,
    combination_rank,
    combination_unrank,
    decode_block,
    decode_indexed_block,
    encode_block,
    iter_bpe_blocks,
    parse_header,
)


class PackedCodecTests(unittest.TestCase):
    def test_combination_rank_unrank_is_bijection(self) -> None:
        for n in range(1, 9):
            for k in range(n + 1):
                for positions in itertools.combinations(range(n), k):
                    rank = combination_rank(positions)
                    self.assertEqual(combination_unrank(rank, n, k), list(positions))

    def test_block_round_trip_exhaustive_int4_values(self) -> None:
        values = list(range(-7, 8)) + [0, -1, 1, -7, 7]
        block, _ = encode_block(values, 4)
        self.assertEqual(decode_block(block, 4), values)

    def test_block_round_trip_int8_tail(self) -> None:
        values = [0, 1, -1, 3, -5, 17, -63, 127, -127, 2, 4, 8, 16, 32, 64, -2, -4]
        block, _ = encode_block(values, 8)
        self.assertEqual(decode_block(block, 8), values)

    def test_file_indexed_round_trip_and_fixed_stream(self) -> None:
        rng = np.random.default_rng(20260831)
        blocks = [rng.integers(-7, 8, size=128, dtype=np.int16) for _ in range(67)]
        blocks.append(rng.integers(-7, 8, size=19, dtype=np.int16))
        weight_count = sum(int(block.size) for block in blocks)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bpe_path = root / "test.bpe"
            fixed_path = root / "test.bin"
            with bpe_path.open("wb+") as bpe_handle, fixed_path.open("wb") as fixed_handle:
                writer = BPEWriter(bpe_handle, 4, 128, len(blocks), weight_count)
                fixed = FixedWriter(fixed_handle, 4)
                for block in blocks:
                    writer.write(block)
                    fixed.write(block)
                fixed.finish()
                writer.finish()

            data = bpe_path.read_bytes()
            header = parse_header(data)
            self.assertEqual(header["block_count"], len(blocks))
            self.assertEqual(header["weight_count"], weight_count)
            self.assertEqual(len(header["offsets"]), 3)

            sequential = [decode_block(block, 4) for _, block in iter_bpe_blocks(data)]
            for expected, observed in zip(blocks, sequential, strict=True):
                self.assertEqual(observed, expected.tolist())
            for index in (0, 1, 31, 32, 63, 64, 67):
                self.assertEqual(decode_indexed_block(data, index), blocks[index].tolist())

            fixed_reader = FixedReader(fixed_path.read_bytes(), 4, weight_count)
            for block in blocks:
                self.assertEqual(fixed_reader.read(int(block.size)), block.tolist())

    def test_all_zero_block_is_small(self) -> None:
        block, payload_bits = encode_block([0] * 128, 4)
        self.assertLessEqual(payload_bits, 8)
        self.assertLessEqual(len(block), 3)

    def test_payload_length_fits_registered_byte(self) -> None:
        alternating = [127 if index % 2 else -127 for index in range(128)]
        block, _ = encode_block(alternating, 8)
        self.assertLessEqual(block[1], 255)
        self.assertEqual(len(block), block[1] + 2)


if __name__ == "__main__":
    unittest.main()
