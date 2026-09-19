"""Peak RAM / VRAM and wall-clock tracking for benchmark stages."""

from __future__ import annotations

import contextlib
import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Usage:
    seconds: float = 0.0
    peak_rss_bytes: int | None = None
    peak_vram_bytes: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "seconds": self.seconds,
            "peak_rss_bytes": self.peak_rss_bytes,
            "peak_vram_bytes": self.peak_vram_bytes,
            **self.extra,
        }


class _RssSampler(threading.Thread):
    def __init__(self, interval: float = 0.05):
        super().__init__(daemon=True)
        self.interval = interval
        self.peak = 0
        self._halt = threading.Event()

    def run(self) -> None:
        try:
            import psutil
        except ImportError:  # pragma: no cover
            return
        process = psutil.Process()
        while not self._halt.is_set():
            try:
                self.peak = max(self.peak, int(process.memory_info().rss))
            except Exception:  # pragma: no cover
                pass
            self._halt.wait(self.interval)

    def stop(self) -> None:
        self._halt.set()
        self.join(timeout=1.0)


@contextlib.contextmanager
def track(device: str = "cpu"):
    """Measure wall time, peak RSS (sampled) and, on CUDA, peak allocated VRAM."""
    usage = Usage()
    cuda = False
    try:
        import torch

        cuda = device.startswith("cuda") and torch.cuda.is_available()
        if cuda:
            torch.cuda.synchronize()
            torch.cuda.reset_peak_memory_stats()
    except ImportError:  # pragma: no cover
        torch = None
    sampler = _RssSampler()
    sampler.start()
    started = time.perf_counter()
    try:
        yield usage
    finally:
        if cuda:
            torch.cuda.synchronize()
            usage.peak_vram_bytes = int(torch.cuda.max_memory_allocated())
        usage.seconds = time.perf_counter() - started
        sampler.stop()
        usage.peak_rss_bytes = sampler.peak or None
