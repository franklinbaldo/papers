from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_safetensors_header(path: Path) -> tuple[int, dict[str, object]]:
    with path.open("rb") as handle:
        header_size = int.from_bytes(handle.read(8), "little")
        header = json.loads(handle.read(header_size))
    return 8 + header_size, header


def _tensor_view(path: Path, data_start: int, meta: dict[str, object]):
    dtype = str(meta["dtype"])
    start, end = (int(value) for value in meta["data_offsets"])
    byte_offset = data_start + start
    nbytes = end - start
    dtype_map = {
        "F64": np.dtype("<f8"),
        "F32": np.dtype("<f4"),
        "F16": np.dtype("<f2"),
        "BF16": np.dtype("<u2"),
    }
    if dtype not in dtype_map:
        return None
    raw = np.memmap(
        path,
        dtype=dtype_map[dtype],
        mode="r",
        offset=byte_offset,
        shape=(nbytes // dtype_map[dtype].itemsize,),
    )
    return dtype, raw


def _to_float32(dtype: str, values):
    if dtype == "BF16":
        words = np.asarray(values, dtype=np.uint16).astype(np.uint32)
        return (words << 16).view(np.float32)
    return np.asarray(values).astype(np.float32, copy=False)


def huffman_weighted_bits(counts: Sequence[int]) -> int:
    """Return exact Huffman payload bits for the supplied symbol counts."""
    heap = [int(count) for count in counts if int(count) > 0]
    if not heap:
        return 0
    if len(heap) == 1:
        return heap[0]
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = left + right
        total += merged
        heapq.heappush(heap, merged)
    return total


def shannon_entropy_bits(counts: Sequence[int]) -> float:
    total = sum(int(count) for count in counts)
    if total == 0:
        return 0.0
    entropy = 0.0
    for raw_count in counts:
        count = int(raw_count)
        if count:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def _enumerative_plane_cost_table(n: int) -> np.ndarray:
    """Exact bit cost for one n-bit plane under four deterministic modes.

    Two mode bits select all-zero, all-one, raw, or enumerative storage.
    Enumerative mode stores k in ceil(log2(n+1)) bits and the lexicographic
    rank of the k-subset in ceil(log2(C(n,k))) bits.
    """
    count_bits = math.ceil(math.log2(n + 1))
    table = np.empty(n + 1, dtype=np.int64)
    for k in range(n + 1):
        combinations = math.comb(n, k)
        rank_bits = (combinations - 1).bit_length()
        if k in (0, n):
            table[k] = 2
        else:
            table[k] = 2 + min(n, count_bits + rank_bits)
    return table


@dataclass
class Accumulator:
    bits: int
    weights: int = 0
    zero_count: int = 0
    fixed_total_bits: int = 0
    sparse_total_bits: int = 0
    length_payload_bits: int = 0
    length_fixed_total_bits: int = 0
    bitplane_total_bits: int = 0

    def __post_init__(self) -> None:
        self.qmax = (1 << (self.bits - 1)) - 1
        self.length_counts = np.zeros(self.bits, dtype=np.int64)
        self.value_counts = np.zeros(2 * self.qmax + 1, dtype=np.int64)
        self.bit_length_lookup = np.array(
            [0 if value == 0 else value.bit_length() for value in range(self.qmax + 1)],
            dtype=np.int16,
        )
        self.plane_cost_tables: dict[int, np.ndarray] = {}

    def add_groups(self, quantized: np.ndarray) -> None:
        groups = np.asarray(quantized, dtype=np.int64)
        if groups.ndim != 2:
            raise ValueError("quantized groups must be a 2D array")
        n = int(groups.shape[1])
        if n == 0:
            return
        count_weights = int(groups.size)
        absolute = np.abs(groups)
        nonzero = absolute != 0
        nonzero_counts = np.count_nonzero(nonzero, axis=1).astype(np.int64)

        self.weights += count_weights
        self.zero_count += count_weights - int(nonzero_counts.sum())
        self.fixed_total_bits += count_weights * self.bits

        # One block-mode bit, then either ordinary fixed-width values or a
        # one-bit zero bitmap plus fixed-width payload for nonzero values.
        fixed_by_group = n * self.bits
        sparse_by_group = n + nonzero_counts * self.bits
        self.sparse_total_bits += int(np.sum(1 + np.minimum(fixed_by_group, sparse_by_group)))

        # Per-weight magnitude bit length. Zero has length 0; nonzero payload
        # keeps one sign bit plus exactly the significant magnitude bits.
        lengths = self.bit_length_lookup[absolute]
        flat_lengths = lengths.reshape(-1)
        self.length_counts += np.bincount(flat_lengths, minlength=self.bits)[: self.bits]
        payload_bits = int(flat_lengths.sum()) + int(nonzero_counts.sum())
        self.length_payload_bits += payload_bits
        length_field_bits = math.ceil(math.log2(self.bits))
        self.length_fixed_total_bits += count_weights * length_field_bits + payload_bits

        shifted = (groups + self.qmax).reshape(-1)
        self.value_counts += np.bincount(
            shifted, minlength=self.value_counts.size
        )[: self.value_counts.size]

        # Sign-magnitude bitplanes. Two mode bits choose all-zero, all-one,
        # raw n-bit storage, or exact enumerative subset coding for 1 positions.
        table = self.plane_cost_tables.setdefault(n, _enumerative_plane_cost_table(n))
        negative_counts = np.count_nonzero(groups < 0, axis=1)
        plane_total = int(np.sum(table[negative_counts]))
        for plane in range(self.bits - 1):
            ones = np.count_nonzero((absolute & (1 << plane)) != 0, axis=1)
            plane_total += int(np.sum(table[ones]))
        self.bitplane_total_bits += plane_total

    def result(self) -> dict[str, float | int]:
        if self.weights == 0:
            raise ValueError("no weights accumulated")
        fixed = self.fixed_total_bits / self.weights

        # Collective length stream: a canonical Huffman table can be shared by
        # the whole tensor corpus. The tiny table metadata is charged explicitly.
        length_huffman_stream_bits = huffman_weighted_bits(self.length_counts.tolist())
        length_codebook_bits = self.bits * math.ceil(math.log2(self.bits + 1))
        length_huffman = (
            self.length_payload_bits + length_huffman_stream_bits + length_codebook_bits
        ) / self.weights

        # Full-value Huffman is an entropy-coding reference, not a random-access
        # inference format. Charge 2*B metadata bits per observed symbol for a
        # compact value identity + canonical code-length description.
        value_huffman_stream_bits = huffman_weighted_bits(self.value_counts.tolist())
        observed_values = int(np.count_nonzero(self.value_counts))
        value_codebook_bits = observed_values * (2 * self.bits)
        value_huffman = (value_huffman_stream_bits + value_codebook_bits) / self.weights
        entropy = shannon_entropy_bits(self.value_counts.tolist())

        def ratio(value: float) -> float:
            return value / fixed

        result: dict[str, float | int] = {
            "bits": self.bits,
            "weights": self.weights,
            "zero_rate": self.zero_count / self.weights,
            "fixed_bits_per_weight": fixed,
            "adaptive_bitmap_sparse_bits_per_weight": self.sparse_total_bits / self.weights,
            "length_fixed_bits_per_weight": self.length_fixed_total_bits / self.weights,
            "length_huffman_bits_per_weight": length_huffman,
            "bitplane_enumerative_bits_per_weight": self.bitplane_total_bits / self.weights,
            "value_huffman_bits_per_weight": value_huffman,
            "value_shannon_entropy_bits_per_weight": entropy,
            "observed_quantized_values": observed_values,
        }
        for key in (
            "adaptive_bitmap_sparse_bits_per_weight",
            "length_fixed_bits_per_weight",
            "length_huffman_bits_per_weight",
            "bitplane_enumerative_bits_per_weight",
            "value_huffman_bits_per_weight",
            "value_shannon_entropy_bits_per_weight",
        ):
            result[key.replace("_bits_per_weight", "_ratio")] = ratio(float(result[key]))
        return result


def quantize_groups(groups: np.ndarray, bits: int) -> np.ndarray:
    qmax = (1 << (bits - 1)) - 1
    max_abs = np.max(np.abs(groups), axis=1)
    safe_scale = np.where(max_abs == 0.0, 1.0, max_abs)
    quantized = np.rint(groups / safe_scale[:, None] * qmax).astype(np.int64)
    quantized[max_abs == 0.0, :] = 0
    return np.clip(quantized, -qmax, qmax)


def run_safetensors(
    path: Path,
    bit_widths: Sequence[int],
    group_size: int,
    model_id: str,
    revision: str,
    expected_sha256: str | None = None,
) -> dict[str, object]:
    observed_sha256 = file_sha256(path)
    if expected_sha256 and observed_sha256.lower() != expected_sha256.lower():
        raise SystemExit(
            f"checkpoint SHA256 mismatch: expected {expected_sha256}, observed {observed_sha256}"
        )

    data_start, header = _load_safetensors_header(path)
    accumulators = {bits: Accumulator(bits) for bits in bit_widths}
    tensor_names: list[str] = []
    skipped_dtypes: set[str] = set()
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
            skipped_dtypes.add(str(meta["dtype"]))
            continue
        dtype, raw = view
        tensor_names.append(name)
        chunk_size = group_size * groups_per_chunk

        for start in range(0, raw.size, chunk_size):
            float_chunk = _to_float32(dtype, raw[start : min(start + chunk_size, raw.size)])
            full_count = (float_chunk.size // group_size) * group_size
            if full_count:
                groups = float_chunk[:full_count].reshape(-1, group_size)
                for bits in bit_widths:
                    accumulators[bits].add_groups(quantize_groups(groups, bits))
            if full_count < float_chunk.size:
                tail = float_chunk[full_count:].reshape(1, -1)
                for bits in bit_widths:
                    accumulators[bits].add_groups(quantize_groups(tail, bits))

    return {
        "mode": "binary-alternatives",
        "model_id": model_id,
        "revision": revision,
        "file": path.name,
        "sha256": observed_sha256,
        "numpy_version": np.__version__,
        "group_size": group_size,
        "included_tensor_rule": "ndim >= 2 and dtype in F16/BF16/F32/F64",
        "tensor_count": len(tensor_names),
        "skipped_dtypes": sorted(skipped_dtypes),
        "bit_widths": list(bit_widths),
        "metrics": [accumulators[bits].result() for bits in bit_widths],
    }


def parse_bits(raw: str) -> list[int]:
    values = [int(item) for item in raw.split(",") if item.strip()]
    if not values or any(bits < 2 for bits in values):
        raise argparse.ArgumentTypeError("--bits must be comma-separated integers >= 2")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare binary variable-precision encodings for quantized LLM weights"
    )
    parser.add_argument("--safetensors", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--bits", default="4,8")
    parser.add_argument("--group-size", type=int, default=128)
    parser.add_argument("--output", type=Path, default=Path("binary_results.json"))
    args = parser.parse_args()

    result = run_safetensors(
        args.safetensors,
        parse_bits(args.bits),
        args.group_size,
        args.model_id,
        args.revision,
        args.expected_sha256,
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
