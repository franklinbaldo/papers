from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import math
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class AdmissionPolicy:
    """Reality-bounded admission contract for paired scalar sensor slices."""

    max_timestamp_quantum_s: float = 1.0
    min_unique_timestamps: int = 3
    min_paired_fraction: float = 0.95
    min_rows_for_benchmark: int = 100


@dataclass(frozen=True)
class AdmissionReport:
    rows: int
    unique_timestamps: int
    timestamp_quantum_s: float | None
    duplicate_timestamp_fraction: float
    paired_fraction: float
    median_abs_channel_delta: float | None
    interface_compatible: bool
    benchmark_ready: bool
    interface_reasons: tuple[str, ...]
    benchmark_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def parse_timestamp(value: str, fmt: str | None = None) -> datetime:
    """Parse a timestamp with an explicit source format when available."""

    if fmt is not None:
        return datetime.strptime(value, fmt)
    return datetime.fromisoformat(value)


def _timestamp_quantum_s(timestamps: Sequence[datetime]) -> float | None:
    unique_us = sorted({int(round(ts.timestamp() * 1_000_000)) for ts in timestamps})
    if len(unique_us) < 2:
        return None
    positive_diffs = [b - a for a, b in zip(unique_us, unique_us[1:]) if b > a]
    if not positive_diffs:
        return None
    quantum_us = positive_diffs[0]
    for delta in positive_diffs[1:]:
        quantum_us = math.gcd(quantum_us, delta)
    return quantum_us / 1_000_000.0


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def assess_scalar_pair(
    records: Iterable[Mapping[str, object]],
    *,
    timestamp_key: str,
    left_key: str,
    right_key: str,
    timestamp_format: str | None = None,
    policy: AdmissionPolicy = AdmissionPolicy(),
) -> AdmissionReport:
    """Assess whether a recorded sensor pair preserves a usable physical timebase.

    This is an offline dataset/interface gate. It only inspects values and timestamps
    present in the recorded slice. It never needs simulator truth, future state, fault
    labels, map/object truth, or any privileged state.
    """

    materialized = list(records)
    timestamps: list[datetime] = []
    deltas: list[float] = []
    paired = 0
    parse_failures = 0

    for record in materialized:
        raw_ts = record.get(timestamp_key)
        try:
            ts = parse_timestamp(str(raw_ts), timestamp_format)
        except (TypeError, ValueError):
            parse_failures += 1
            continue
        timestamps.append(ts)

        left = _finite_float(record.get(left_key))
        right = _finite_float(record.get(right_key))
        if left is not None and right is not None:
            paired += 1
            deltas.append(abs(left - right))

    rows = len(materialized)
    unique = len(set(timestamps))
    quantum = _timestamp_quantum_s(timestamps)
    duplicate_fraction = 0.0 if not timestamps else 1.0 - unique / len(timestamps)
    paired_fraction = 0.0 if rows == 0 else paired / rows
    reasons: list[str] = []

    if rows == 0:
        reasons.append("empty_slice")
    if parse_failures:
        reasons.append(f"timestamp_parse_failures={parse_failures}")
    if unique < policy.min_unique_timestamps:
        reasons.append(
            f"unique_timestamps={unique}<min_unique_timestamps={policy.min_unique_timestamps}"
        )
    if quantum is None:
        reasons.append("timestamp_quantum_unresolved")
    elif quantum > policy.max_timestamp_quantum_s:
        reasons.append(
            f"timestamp_quantum_s={quantum:g}>max_timestamp_quantum_s={policy.max_timestamp_quantum_s:g}"
        )
    if paired_fraction < policy.min_paired_fraction:
        reasons.append(
            f"paired_fraction={paired_fraction:.3f}<min_paired_fraction={policy.min_paired_fraction:.3f}"
        )

    interface_compatible = not reasons
    benchmark_reasons = list(reasons)
    if rows < policy.min_rows_for_benchmark:
        benchmark_reasons.append(
            f"rows={rows}<min_rows_for_benchmark={policy.min_rows_for_benchmark}"
        )
    benchmark_ready = not benchmark_reasons

    return AdmissionReport(
        rows=rows,
        unique_timestamps=unique,
        timestamp_quantum_s=quantum,
        duplicate_timestamp_fraction=duplicate_fraction,
        paired_fraction=paired_fraction,
        median_abs_channel_delta=median(deltas) if deltas else None,
        interface_compatible=interface_compatible,
        benchmark_ready=benchmark_ready,
        interface_reasons=tuple(reasons),
        benchmark_reasons=tuple(benchmark_reasons),
    )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cache_key(*, source: str, revision: str, content_sha256: str) -> str:
    """Stable cache key so unchanged heavyweight sources are never redownloaded."""

    payload = f"{source}\n{revision}\n{content_sha256}\n".encode()
    return hashlib.sha256(payload).hexdigest()[:24]
