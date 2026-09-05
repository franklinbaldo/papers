from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

END = -1
LOG2_3 = math.log2(3.0)


@dataclass(frozen=True)
class Metrics:
    bits: int
    weights: int
    zero_rate: float
    avg_trits: float
    capacity_equivalent_bits: float
    packed_2bit_bits: float
    fixed_bits: float
    binary_length_prefix_bits: float

    @property
    def cell_ratio(self) -> float:
        return self.avg_trits / self.fixed_bits

    @property
    def capacity_ratio(self) -> float:
        return self.capacity_equivalent_bits / self.fixed_bits

    @property
    def packed_2bit_ratio(self) -> float:
        return self.packed_2bit_bits / self.fixed_bits

    @property
    def binary_length_prefix_ratio(self) -> float:
        return self.binary_length_prefix_bits / self.fixed_bits

    def as_dict(self) -> dict[str, float | int]:
        data = asdict(self)
        data.update(
            cell_ratio=self.cell_ratio,
            capacity_ratio=self.capacity_ratio,
            packed_2bit_ratio=self.packed_2bit_ratio,
            binary_length_prefix_ratio=self.binary_length_prefix_ratio,
        )
        return data


def trailing_zeros(value: int) -> int:
    if value <= 0:
        raise ValueError("trailing_zeros expects a positive integer")
    return (value & -value).bit_length() - 1


def encode_quantized(value: int, bits: int) -> list[int]:
    """Encode a sign-magnitude integer with alphabet {0, 1, END}.

    The fixed-width reference uses one sign bit plus ``bits - 1`` magnitude
    bits. The ternary stream removes trailing zero magnitude bits and uses END
    to terminate the weight. The decoder restores the omitted suffix as zero,
    so this transformation is lossless relative to the quantized integer.
    """
    if bits < 2:
        raise ValueError("bits must be >= 2")
    magnitude_bits = bits - 1
    qmax = (1 << magnitude_bits) - 1
    if not -qmax <= value <= qmax:
        raise ValueError(f"{value} is outside the {bits}-bit sign-magnitude range")
    if value == 0:
        return [END]

    sign = 1 if value < 0 else 0
    magnitude = abs(value)
    full = f"{magnitude:0{magnitude_bits}b}"
    prefix = full.rstrip("0")
    return [sign, *(int(bit) for bit in prefix), END]


def decode_quantized(symbols: Sequence[int], bits: int) -> int:
    if bits < 2:
        raise ValueError("bits must be >= 2")
    if not symbols or symbols[-1] != END or END in symbols[:-1]:
        raise ValueError("one encoded weight must contain exactly one final END")
    payload = symbols[:-1]
    if not payload:
        return 0
    if payload[0] not in (0, 1):
        raise ValueError("sign must be 0 or 1")
    magnitude_bits = bits - 1
    prefix = payload[1:]
    if not prefix or len(prefix) > magnitude_bits or any(x not in (0, 1) for x in prefix):
        raise ValueError("invalid magnitude prefix")
    padded = list(prefix) + [0] * (magnitude_bits - len(prefix))
    magnitude = int("".join(str(x) for x in padded), 2)
    if magnitude == 0:
        raise ValueError("non-canonical zero encoding")
    return -magnitude if payload[0] else magnitude


def encode_stream(values: Iterable[int], bits: int) -> list[int]:
    stream: list[int] = []
    for value in values:
        stream.extend(encode_quantized(value, bits))
    return stream


def decode_stream(stream: Iterable[int], bits: int) -> list[int]:
    values: list[int] = []
    current: list[int] = []
    for symbol in stream:
        current.append(symbol)
        if symbol == END:
            values.append(decode_quantized(current, bits))
            current = []
    if current:
        raise ValueError("unterminated final weight")
    return values


def quantize(values: Sequence[float], bits: int) -> list[int]:
    magnitude_bits = bits - 1
    qmax = (1 << magnitude_bits) - 1
    max_abs = max((abs(value) for value in values), default=0.0)
    if max_abs == 0.0:
        return [0] * len(values)
    return [max(-qmax, min(qmax, round(value / max_abs * qmax))) for value in values]


def encoded_length(value: int, bits: int) -> int:
    if value == 0:
        return 1
    magnitude_bits = bits - 1
    return 1 + (magnitude_bits - trailing_zeros(abs(value))) + 1


def magnitude_prefix_length(value: int, bits: int) -> int:
    if value == 0:
        return 0
    return (bits - 1) - trailing_zeros(abs(value))


def measure_quantized(values: Sequence[int], bits: int) -> Metrics:
    if not values:
        raise ValueError("at least one quantized value is required")
    lengths = [encoded_length(value, bits) for value in values]
    avg_trits = sum(lengths) / len(lengths)

    # A deliberately simple binary competitor: a fixed-width field encodes the
    # retained magnitude-prefix length (0..bits-1), followed, for non-zero
    # values, by sign and magnitude prefix. It is not claimed to be optimal.
    length_field_bits = math.ceil(math.log2(bits))
    binary_cost = 0
    for value in values:
        prefix_len = magnitude_prefix_length(value, bits)
        binary_cost += length_field_bits
        if value != 0:
            binary_cost += 1 + prefix_len
    avg_binary_length_prefix = binary_cost / len(values)

    return Metrics(
        bits=bits,
        weights=len(values),
        zero_rate=sum(value == 0 for value in values) / len(values),
        avg_trits=avg_trits,
        capacity_equivalent_bits=avg_trits * LOG2_3,
        packed_2bit_bits=avg_trits * 2.0,
        fixed_bits=float(bits),
        binary_length_prefix_bits=avg_binary_length_prefix,
    )


def synthetic_values(name: str, count: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    if name == "uniform":
        return [rng.uniform(-1.0, 1.0) for _ in range(count)]
    if name == "gaussian":
        return [max(-1.0, min(1.0, rng.gauss(0.0, 0.18))) for _ in range(count)]
    if name == "laplace":
        values = []
        scale = 0.12
        for _ in range(count):
            u = rng.random() - 0.5
            sign = 1.0 if u >= 0.0 else -1.0
            value = -scale * sign * math.log(1.0 - 2.0 * abs(u))
            values.append(max(-1.0, min(1.0, value)))
        return values
    if name == "centered_mixture":
        values = []
        for _ in range(count):
            sigma = 0.08 if rng.random() < 0.9 else 0.35
            values.append(max(-1.0, min(1.0, rng.gauss(0.0, sigma))))
        return values
    if name == "sparse_uniform":
        return [0.0 if rng.random() < 0.5 else rng.uniform(-1.0, 1.0) for _ in range(count)]
    raise ValueError(f"unknown synthetic distribution: {name}")


def run_synthetic(count: int, seed: int, bit_widths: Sequence[int]) -> dict[str, object]:
    distributions = ["uniform", "gaussian", "laplace", "centered_mixture", "sparse_uniform"]
    result: dict[str, object] = {
        "mode": "synthetic",
        "generator": "python-random-v1",
        "seed": seed,
        "count_per_distribution": count,
        "bit_widths": list(bit_widths),
        "distributions": {},
    }
    output = result["distributions"]
    assert isinstance(output, dict)
    for name in distributions:
        floats = synthetic_values(name, count, seed)
        output[name] = [measure_quantized(quantize(floats, bits), bits).as_dict() for bits in bit_widths]
    return result


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
    import numpy as np

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
    import numpy as np

    if dtype == "BF16":
        words = np.asarray(values, dtype=np.uint16).astype(np.uint32)
        return (words << 16).view(np.float32)
    return np.asarray(values).astype(np.float32, copy=False)


def _accumulate_quantized_numpy(acc: dict[str, int], quantized, bits: int) -> None:
    import numpy as np

    flat = np.asarray(quantized, dtype=np.int64).reshape(-1)
    absolute = np.abs(flat)
    zero_count = int(np.count_nonzero(absolute == 0))
    nonzero_count = int(flat.size - zero_count)
    magnitude_bits = bits - 1
    trailing_zero_sum = 0
    if nonzero_count:
        nonzero = absolute[absolute != 0]
        for power in range(1, magnitude_bits):
            trailing_zero_sum += int(np.count_nonzero((nonzero & ((1 << power) - 1)) == 0))

    acc["weights"] += int(flat.size)
    acc["zeros"] += zero_count
    acc["trits"] += zero_count + nonzero_count * (magnitude_bits + 2) - trailing_zero_sum
    length_field_bits = math.ceil(math.log2(bits))
    acc["binary_length_prefix_bits"] += (
        int(flat.size) * length_field_bits
        + nonzero_count * (magnitude_bits + 1)
        - trailing_zero_sum
    )


def _metrics_from_accumulator(acc: dict[str, int], bits: int) -> Metrics:
    count = acc["weights"]
    avg_trits = acc["trits"] / count
    return Metrics(
        bits=bits,
        weights=count,
        zero_rate=acc["zeros"] / count,
        avg_trits=avg_trits,
        capacity_equivalent_bits=avg_trits * LOG2_3,
        packed_2bit_bits=avg_trits * 2.0,
        fixed_bits=float(bits),
        binary_length_prefix_bits=acc["binary_length_prefix_bits"] / count,
    )


def run_safetensors(
    path: Path,
    bit_widths: Sequence[int],
    group_size: int,
    model_id: str,
    revision: str,
    expected_sha256: str | None = None,
) -> dict[str, object]:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional model-backed layer
        raise SystemExit("model-backed mode requires: pip install numpy==2.5.2") from exc

    observed_sha256 = file_sha256(path)
    if expected_sha256 and observed_sha256.lower() != expected_sha256.lower():
        raise SystemExit(
            f"checkpoint SHA256 mismatch: expected {expected_sha256}, observed {observed_sha256}"
        )

    data_start, header = _load_safetensors_header(path)
    accumulators = {
        bits: {"weights": 0, "zeros": 0, "trits": 0, "binary_length_prefix_bits": 0}
        for bits in bit_widths
    }
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
            pieces = []
            if full_count:
                pieces.append(float_chunk[:full_count].reshape(-1, group_size))
            if full_count < float_chunk.size:
                pieces.append(float_chunk[full_count:].reshape(1, -1))

            for groups in pieces:
                for bits in bit_widths:
                    qmax = (1 << (bits - 1)) - 1
                    max_abs = np.max(np.abs(groups), axis=1)
                    safe_scale = np.where(max_abs == 0.0, 1.0, max_abs)
                    quantized = np.rint(groups / safe_scale[:, None] * qmax).astype(np.int64)
                    quantized[max_abs == 0.0, :] = 0
                    quantized = np.clip(quantized, -qmax, qmax)
                    _accumulate_quantized_numpy(accumulators[bits], quantized, bits)

    metrics = [_metrics_from_accumulator(accumulators[bits], bits).as_dict() for bits in bit_widths]
    return {
        "mode": "safetensors",
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
        "metrics": metrics,
    }


def parse_bits(raw: str) -> list[int]:
    values = [int(item) for item in raw.split(",") if item.strip()]
    if not values or any(bits < 2 for bits in values):
        raise argparse.ArgumentTypeError("--bits must be comma-separated integers >= 2")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate 0/1/END ternary delimiting for quantized weights")
    parser.add_argument("--bits", default="4,8,16", help="comma-separated fixed-width baselines")
    parser.add_argument("--count", type=int, default=50_000, help="samples per synthetic distribution")
    parser.add_argument("--seed", type=int, default=20_260_831)
    parser.add_argument("--safetensors", type=Path, help="optional local safetensors checkpoint")
    parser.add_argument("--model-id", default="unknown")
    parser.add_argument("--revision", default="unknown")
    parser.add_argument("--group-size", type=int, default=128)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    bit_widths = parse_bits(args.bits)
    if args.safetensors:
        result = run_safetensors(
            args.safetensors,
            bit_widths,
            args.group_size,
            args.model_id,
            args.revision,
            args.expected_sha256,
        )
    else:
        result = run_synthetic(args.count, args.seed, bit_widths)

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
