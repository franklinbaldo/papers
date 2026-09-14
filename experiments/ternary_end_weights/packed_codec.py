from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Sequence

import numpy as np

from binary_alternatives import (
    _load_safetensors_header,
    _tensor_view,
    _to_float32,
    file_sha256,
    quantize_groups,
)

MAGIC = b"BPE1"
INDEX_STRIDE = 32
HEADER = struct.Struct("<4sBHHIQI")
SUPPORTED_DTYPES = {"F16", "BF16", "F32", "F64"}


def ceil_log2(value: int) -> int:
    return 0 if value <= 1 else (value - 1).bit_length()


def combination_rank(positions: Sequence[int]) -> int:
    """Colexicographic combinatorial rank for a sorted subset."""
    return sum(math.comb(position, index) for index, position in enumerate(positions, start=1))


def combination_unrank(rank: int, n: int, k: int) -> list[int]:
    """Inverse of :func:`combination_rank` for k positions selected from n."""
    if rank < 0 or rank >= math.comb(n, k):
        raise ValueError("combination rank outside registered subset space")
    if k == 0:
        return []

    positions = [0] * k
    x = n - 1
    remaining = rank
    for index in range(k, 0, -1):
        while math.comb(x, index) > remaining:
            x -= 1
        positions[index - 1] = x
        remaining -= math.comb(x, index)
        x -= 1
    if remaining:
        raise ValueError("combination unrank left a residual")
    return positions


class BitWriter:
    def __init__(self) -> None:
        self.buffer = bytearray()
        self.current = 0
        self.used = 0
        self.bits_written = 0

    def write(self, value: int, bits: int) -> None:
        if bits < 0 or value < 0 or (bits and value >= (1 << bits)):
            raise ValueError("value does not fit requested bit width")
        for index in range(bits):
            self.current |= ((value >> index) & 1) << self.used
            self.used += 1
            self.bits_written += 1
            if self.used == 8:
                self.buffer.append(self.current)
                self.current = 0
                self.used = 0

    def finish(self) -> bytes:
        if self.used:
            self.buffer.append(self.current)
            self.current = 0
            self.used = 0
        return bytes(self.buffer)


class BitReader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.position = 0

    def read(self, bits: int) -> int:
        value = 0
        for index in range(bits):
            byte_index = self.position >> 3
            bit_index = self.position & 7
            if byte_index >= len(self.data):
                raise ValueError("truncated bitplane payload")
            value |= ((self.data[byte_index] >> bit_index) & 1) << index
            self.position += 1
        return value


def _encode_plane(plane: Sequence[int], writer: BitWriter) -> None:
    n = len(plane)
    k = sum(int(value) for value in plane)
    if k == 0:
        writer.write(0, 2)
        return
    if k == n:
        writer.write(1, 2)
        return

    count_bits = ceil_log2(n + 1)
    rank_bits = ceil_log2(math.comb(n, k))
    if count_bits + rank_bits < n:
        writer.write(3, 2)
        writer.write(k, count_bits)
        positions = [index for index, value in enumerate(plane) if value]
        writer.write(combination_rank(positions), rank_bits)
        return

    writer.write(2, 2)
    for value in plane:
        writer.write(int(value), 1)


def _decode_plane(reader: BitReader, n: int) -> list[int]:
    mode = reader.read(2)
    if mode == 0:
        return [0] * n
    if mode == 1:
        return [1] * n
    if mode == 2:
        return [reader.read(1) for _ in range(n)]

    count_bits = ceil_log2(n + 1)
    k = reader.read(count_bits)
    if not 0 < k < n:
        raise ValueError("non-canonical enumerative plane population")
    rank_bits = ceil_log2(math.comb(n, k))
    rank = reader.read(rank_bits)
    positions = combination_unrank(rank, n, k)
    plane = [0] * n
    for position in positions:
        plane[position] = 1
    return plane


def encode_block(values: Sequence[int], bits: int) -> tuple[bytes, int]:
    if not values or len(values) > 128:
        raise ValueError("BPE1 blocks must contain 1..128 weights")
    qmax = (1 << (bits - 1)) - 1
    if any(not -qmax <= int(value) <= qmax for value in values):
        raise ValueError("quantized value outside sign-magnitude range")

    writer = BitWriter()
    _encode_plane([int(value) < 0 for value in values], writer)
    absolute = [abs(int(value)) for value in values]
    for plane_index in range(bits - 1):
        _encode_plane([(value >> plane_index) & 1 for value in absolute], writer)
    payload_bits = writer.bits_written
    payload = writer.finish()
    if len(payload) > 255:
        raise ValueError("BPE1 one-byte block payload length overflow")
    block = bytes((len(values) - 1, len(payload))) + payload
    return block, payload_bits


def decode_block(block: bytes, bits: int) -> list[int]:
    if len(block) < 2:
        raise ValueError("truncated BPE1 block")
    n = block[0] + 1
    payload_length = block[1]
    if len(block) != payload_length + 2:
        raise ValueError("BPE1 block length mismatch")

    reader = BitReader(block[2:])
    sign = _decode_plane(reader, n)
    values = [0] * n
    for plane_index in range(bits - 1):
        plane = _decode_plane(reader, n)
        for index, value in enumerate(plane):
            values[index] |= value << plane_index
    return [-value if sign[index] and value else value for index, value in enumerate(values)]


def sign_magnitude_code(value: int, bits: int) -> int:
    return ((1 << (bits - 1)) if value < 0 else 0) | abs(int(value))


def sign_magnitude_decode(code: int, bits: int) -> int:
    sign = code >> (bits - 1)
    magnitude = code & ((1 << (bits - 1)) - 1)
    return -magnitude if sign and magnitude else magnitude


class FixedWriter:
    def __init__(self, handle: BinaryIO, bits: int) -> None:
        if bits not in (4, 8):
            raise ValueError("registered packed experiment supports INT4/INT8")
        self.handle = handle
        self.bits = bits
        self.pending_nibble: int | None = None
        self.weights = 0

    def write(self, values: Sequence[int] | np.ndarray) -> None:
        array = np.asarray(values, dtype=np.int16).reshape(-1)
        sign = (array < 0).astype(np.uint8) << (self.bits - 1)
        codes = sign | np.abs(array).astype(np.uint8)
        self.weights += int(codes.size)
        if self.bits == 8:
            self.handle.write(codes.tobytes())
            return

        start = 0
        if self.pending_nibble is not None and codes.size:
            self.handle.write(bytes((self.pending_nibble | (int(codes[0]) << 4),)))
            self.pending_nibble = None
            start = 1
        remaining = codes[start:]
        pair_count = remaining.size // 2
        if pair_count:
            low = remaining[: pair_count * 2 : 2]
            high = remaining[1 : pair_count * 2 : 2]
            packed = low | (high << 4)
            self.handle.write(packed.astype(np.uint8, copy=False).tobytes())
        if remaining.size % 2:
            self.pending_nibble = int(remaining[-1])

    def finish(self) -> None:
        if self.pending_nibble is not None:
            self.handle.write(bytes((self.pending_nibble,)))
            self.pending_nibble = None


class FixedReader:
    def __init__(self, data: bytes, bits: int, weight_count: int) -> None:
        self.data = data
        self.bits = bits
        self.weight_count = weight_count
        self.position = 0

    def read(self, count: int) -> list[int]:
        if self.position + count > self.weight_count:
            raise ValueError("fixed stream read beyond registered weight count")
        values: list[int] = []
        for index in range(self.position, self.position + count):
            if self.bits == 8:
                code = self.data[index]
            else:
                byte = self.data[index >> 1]
                code = (byte >> 4) if index & 1 else (byte & 0x0F)
            values.append(sign_magnitude_decode(code, self.bits))
        self.position += count
        return values


@dataclass
class BPEStats:
    blocks: int
    weights: int
    payload_bytes: int = 0
    payload_bits: int = 0


class BPEWriter:
    def __init__(
        self,
        handle: BinaryIO,
        bits: int,
        group_size: int,
        block_count: int,
        weight_count: int,
        index_stride: int = INDEX_STRIDE,
    ) -> None:
        self.handle = handle
        self.bits = bits
        self.group_size = group_size
        self.block_count = block_count
        self.weight_count = weight_count
        self.index_stride = index_stride
        self.index_count = (block_count + index_stride - 1) // index_stride
        self.index_offsets: list[int] = []
        self.block_index = 0
        self.stats = BPEStats(blocks=block_count, weights=weight_count)

        handle.write(
            HEADER.pack(
                MAGIC,
                bits,
                group_size,
                index_stride,
                block_count,
                weight_count,
                self.index_count,
            )
        )
        handle.write(b"\0" * (self.index_count * 8))

    def write(self, values: Sequence[int] | np.ndarray) -> None:
        if self.block_index >= self.block_count:
            raise ValueError("more blocks written than declared")
        if self.block_index % self.index_stride == 0:
            self.index_offsets.append(self.handle.tell())
        block, payload_bits = encode_block(np.asarray(values).reshape(-1).tolist(), self.bits)
        self.handle.write(block)
        self.stats.payload_bytes += len(block) - 2
        self.stats.payload_bits += payload_bits
        self.block_index += 1

    def finish(self) -> BPEStats:
        if self.block_index != self.block_count:
            raise ValueError("fewer blocks written than declared")
        if len(self.index_offsets) != self.index_count:
            raise ValueError("BPE1 index entry count mismatch")
        end = self.handle.tell()
        self.handle.seek(HEADER.size)
        for offset in self.index_offsets:
            self.handle.write(struct.pack("<Q", offset))
        self.handle.seek(end)
        return self.stats


def parse_header(data: bytes) -> dict[str, object]:
    if len(data) < HEADER.size:
        raise ValueError("truncated BPE1 header")
    magic, bits, group_size, index_stride, block_count, weight_count, index_count = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise ValueError("invalid BPE1 magic")
    index_end = HEADER.size + index_count * 8
    if index_end > len(data):
        raise ValueError("truncated BPE1 index")
    offsets = [struct.unpack_from("<Q", data, HEADER.size + index * 8)[0] for index in range(index_count)]
    return {
        "bits": bits,
        "group_size": group_size,
        "index_stride": index_stride,
        "block_count": block_count,
        "weight_count": weight_count,
        "index_count": index_count,
        "offsets": offsets,
        "data_start": index_end,
    }


def iter_bpe_blocks(data: bytes) -> Iterable[tuple[int, bytes]]:
    header = parse_header(data)
    position = int(header["data_start"])
    for block_index in range(int(header["block_count"])):
        if position + 2 > len(data):
            raise ValueError("truncated BPE1 block header")
        payload_length = data[position + 1]
        end = position + 2 + payload_length
        if end > len(data):
            raise ValueError("truncated BPE1 block payload")
        yield block_index, data[position:end]
        position = end
    if position != len(data):
        raise ValueError("trailing bytes after final BPE1 block")


def decode_indexed_block(data: bytes, block_index: int) -> list[int]:
    header = parse_header(data)
    block_count = int(header["block_count"])
    if not 0 <= block_index < block_count:
        raise IndexError(block_index)
    stride = int(header["index_stride"])
    offsets = list(header["offsets"])
    superblock = block_index // stride
    position = int(offsets[superblock])
    current = superblock * stride
    while current < block_index:
        payload_length = data[position + 1]
        position += 2 + payload_length
        current += 1
    payload_length = data[position + 1]
    return decode_block(data[position : position + 2 + payload_length], int(header["bits"]))


def _registered_tensor_counts(path: Path, group_size: int) -> tuple[int, int, int]:
    _, header = _load_safetensors_header(path)
    tensor_count = 0
    weight_count = 0
    block_count = 0
    for name, raw_meta in header.items():
        if name == "__metadata__":
            continue
        meta = dict(raw_meta)
        shape = [int(value) for value in meta["shape"]]
        if len(shape) < 2 or str(meta["dtype"]) not in SUPPORTED_DTYPES:
            continue
        count = math.prod(shape)
        tensor_count += 1
        weight_count += count
        block_count += (count + group_size - 1) // group_size
    return tensor_count, weight_count, block_count


def _iter_quantized_blocks(path: Path, bits: int, group_size: int) -> Iterable[np.ndarray]:
    data_start, header = _load_safetensors_header(path)
    groups_per_chunk = 4096
    for name, raw_meta in header.items():
        if name == "__metadata__":
            continue
        meta = dict(raw_meta)
        shape = [int(value) for value in meta["shape"]]
        if len(shape) < 2:
            continue
        view = _tensor_view(path, data_start, meta)
        if view is None:
            continue
        dtype, raw = view
        chunk_size = group_size * groups_per_chunk
        for start in range(0, raw.size, chunk_size):
            float_chunk = _to_float32(dtype, raw[start : min(start + chunk_size, raw.size)])
            full_count = (float_chunk.size // group_size) * group_size
            if full_count:
                groups = float_chunk[:full_count].reshape(-1, group_size)
                quantized = quantize_groups(groups, bits)
                for row in quantized:
                    yield row
            if full_count < float_chunk.size:
                tail = float_chunk[full_count:].reshape(1, -1)
                yield quantize_groups(tail, bits)[0]


def verify_against_fixed(bpe_path: Path, fixed_path: Path) -> dict[str, object]:
    started = time.perf_counter()
    bpe = bpe_path.read_bytes()
    fixed = fixed_path.read_bytes()
    header = parse_header(bpe)
    bits = int(header["bits"])
    reader = FixedReader(fixed, bits, int(header["weight_count"]))
    decoded_weights = 0
    for _, block in iter_bpe_blocks(bpe):
        decoded = decode_block(block, bits)
        expected = reader.read(len(decoded))
        if decoded != expected:
            raise ValueError("Python BPE1 decoder disagrees with fixed registered stream")
        decoded_weights += len(decoded)
    if decoded_weights != int(header["weight_count"]):
        raise ValueError("Python BPE1 verification weight count mismatch")
    return {
        "python_verified": True,
        "decoded_weights": decoded_weights,
        "verify_seconds": time.perf_counter() - started,
    }


def build_width(
    model_path: Path,
    bits: int,
    group_size: int,
    output_dir: Path,
) -> dict[str, object]:
    tensor_count, weight_count, block_count = _registered_tensor_counts(model_path, group_size)
    bpe_path = output_dir / f"packed_int{bits}.bpe"
    fixed_path = output_dir / f"fixed_int{bits}.bin"

    with bpe_path.open("wb+") as bpe_handle, fixed_path.open("wb") as fixed_handle:
        bpe_writer = BPEWriter(bpe_handle, bits, group_size, block_count, weight_count)
        fixed_writer = FixedWriter(fixed_handle, bits)
        observed_blocks = 0
        observed_weights = 0
        for block in _iter_quantized_blocks(model_path, bits, group_size):
            bpe_writer.write(block)
            fixed_writer.write(block)
            observed_blocks += 1
            observed_weights += int(block.size)
        fixed_writer.finish()
        stats = bpe_writer.finish()

    if observed_blocks != block_count or observed_weights != weight_count:
        raise ValueError("generated corpus differs from registered tensor metadata")

    verification = verify_against_fixed(bpe_path, fixed_path)
    bpe_bytes = bpe_path.stat().st_size
    fixed_bytes = fixed_path.stat().st_size
    index_bytes = ((block_count + INDEX_STRIDE - 1) // INDEX_STRIDE) * 8
    padding_bits = stats.payload_bytes * 8 - stats.payload_bits

    return {
        "bits": bits,
        "tensor_count": tensor_count,
        "weights": weight_count,
        "blocks": block_count,
        "header_bytes": HEADER.size,
        "index_stride": INDEX_STRIDE,
        "index_bytes": index_bytes,
        "block_header_bytes": block_count * 2,
        "payload_bytes": stats.payload_bytes,
        "payload_unpadded_bits": stats.payload_bits,
        "payload_padding_bits": padding_bits,
        "bpe_file": bpe_path.name,
        "bpe_sha256": file_sha256(bpe_path),
        "bpe_bytes": bpe_bytes,
        "bpe_bits_per_weight": bpe_bytes * 8 / weight_count,
        "fixed_file": fixed_path.name,
        "fixed_sha256": file_sha256(fixed_path),
        "fixed_bytes": fixed_bytes,
        "fixed_bits_per_weight": fixed_bytes * 8 / weight_count,
        "size_ratio": bpe_bytes / fixed_bytes,
        **verification,
    }


def build_model(
    model_path: Path,
    bit_widths: Sequence[int],
    group_size: int,
    output_dir: Path,
    model_id: str,
    revision: str,
    expected_sha256: str,
) -> dict[str, object]:
    observed_sha256 = file_sha256(model_path)
    if observed_sha256.lower() != expected_sha256.lower():
        raise SystemExit(
            f"checkpoint SHA256 mismatch: expected {expected_sha256}, observed {observed_sha256}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    results = [build_width(model_path, bits, group_size, output_dir) for bits in bit_widths]
    return {
        "format": "BPE1",
        "model_id": model_id,
        "revision": revision,
        "checkpoint_sha256": observed_sha256,
        "numpy_version": np.__version__,
        "group_size": group_size,
        "index_stride": INDEX_STRIDE,
        "bit_widths": list(bit_widths),
        "metrics": results,
    }


def parse_bits(raw: str) -> list[int]:
    values = [int(value) for value in raw.split(",") if value.strip()]
    if not values or any(value not in (4, 8) for value in values):
        raise argparse.ArgumentTypeError("registered BPE1 experiment supports --bits 4,8")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and verify the BPE1 packed bitplane codec")
    parser.add_argument("--safetensors", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--bits", default="4,8")
    parser.add_argument("--group-size", type=int, default=128)
    parser.add_argument("--output-dir", type=Path, default=Path("packed_out"))
    parser.add_argument("--output", type=Path, default=Path("packed_build.json"))
    args = parser.parse_args()

    result = build_model(
        args.safetensors,
        parse_bits(args.bits),
        args.group_size,
        args.output_dir,
        args.model_id,
        args.revision,
        args.expected_sha256,
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
