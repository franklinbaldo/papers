from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sensor_slice_admission import AdmissionPolicy, assess_scalar_pair, cache_key, sha256_file


class SensorSliceAdmissionTests(unittest.TestCase):
    def test_second_resolution_pair_is_interface_compatible(self) -> None:
        rows = [
            {"t": "2026-01-01 00:00:00", "a": 10.0, "b": 10.2},
            {"t": "2026-01-01 00:00:01", "a": 11.0, "b": 10.9},
            {"t": "2026-01-01 00:00:02", "a": 12.0, "b": 12.1},
        ]
        report = assess_scalar_pair(
            rows,
            timestamp_key="t",
            left_key="a",
            right_key="b",
            timestamp_format="%Y-%m-%d %H:%M:%S",
            policy=AdmissionPolicy(min_rows_for_benchmark=3),
        )
        self.assertTrue(report.interface_compatible)
        self.assertTrue(report.benchmark_ready)
        self.assertEqual(report.timestamp_quantum_s, 1.0)

    def test_minute_quantization_is_rejected_for_one_hz_contract(self) -> None:
        rows = [
            {"t": "01-01-2026 10:00", "a": 10.0, "b": 10.1},
            {"t": "01-01-2026 10:01", "a": 11.0, "b": 11.1},
            {"t": "01-01-2026 10:02", "a": 12.0, "b": 12.1},
        ]
        report = assess_scalar_pair(
            rows,
            timestamp_key="t",
            left_key="a",
            right_key="b",
            timestamp_format="%d-%m-%Y %H:%M",
            policy=AdmissionPolicy(min_rows_for_benchmark=3),
        )
        self.assertFalse(report.interface_compatible)
        self.assertEqual(report.timestamp_quantum_s, 60.0)
        self.assertTrue(
            any("timestamp_quantum_s=60" in reason for reason in report.interface_reasons)
        )

    def test_missing_paired_values_are_rejected(self) -> None:
        rows = [
            {"t": "2026-01-01T00:00:00", "a": 1.0, "b": None},
            {"t": "2026-01-01T00:00:01", "a": 2.0, "b": 2.0},
            {"t": "2026-01-01T00:00:02", "a": 3.0, "b": None},
        ]
        report = assess_scalar_pair(rows, timestamp_key="t", left_key="a", right_key="b")
        self.assertFalse(report.interface_compatible)
        self.assertAlmostEqual(report.paired_fraction, 1 / 3)

    def test_cache_key_is_content_and_revision_stable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "slice.csv"
            path.write_text("t,a,b\n0,1,1\n", encoding="utf-8")
            digest = sha256_file(path)
            key1 = cache_key(source="example", revision="abc123", content_sha256=digest)
            key2 = cache_key(source="example", revision="abc123", content_sha256=digest)
            key3 = cache_key(source="example", revision="def456", content_sha256=digest)
            self.assertEqual(key1, key2)
            self.assertNotEqual(key1, key3)


if __name__ == "__main__":
    unittest.main()
