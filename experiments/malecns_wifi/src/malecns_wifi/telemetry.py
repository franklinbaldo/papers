"""Optional live telemetry (Weights & Biases) for the staged pipeline.

Everything is a no-op unless ``WANDB_API_KEY`` is set and ``wandb`` imports, so
local runs and CI stay silent. Runs are grouped by ``WANDB_RUN_GROUP`` (the
executor sets it to the GitHub run id) so the three stages of one pipeline run
land together. Metrics are engineering telemetry only; no benchmark labels.
"""

from __future__ import annotations

import os
import time
from typing import Any


class Telemetry:
    def __init__(self, stage: str, *, config: dict[str, Any] | None = None, tags: tuple[str, ...] = ()):
        self.stage = stage
        self.run = None
        self.started = time.perf_counter()
        self._last_flush = 0.0
        if not os.environ.get("WANDB_API_KEY"):
            return
        try:
            import wandb
        except ImportError:  # pragma: no cover
            return
        group = os.environ.get("WANDB_RUN_GROUP") or None
        self.run = wandb.init(
            project=os.environ.get("WANDB_PROJECT", "malecns-multieurlex21"),
            entity=os.environ.get("WANDB_ENTITY") or None,
            group=group,
            name=f"{group}-{stage}" if group else stage,
            job_type=stage,
            tags=[stage, *tags],
            config=config or {},
            reinit=True,
        )

    @property
    def active(self) -> bool:
        return self.run is not None

    def log(self, metrics: dict[str, Any], *, min_interval: float = 0.0) -> None:
        if self.run is None:
            return
        now = time.perf_counter()
        if min_interval and now - self._last_flush < min_interval:
            return
        self._last_flush = now
        self.run.log({**metrics, "elapsed_s": now - self.started})

    def summary(self, values: dict[str, Any]) -> None:
        if self.run is None:
            return
        for key, value in values.items():
            self.run.summary[key] = value

    def finish(self) -> None:
        if self.run is not None:
            self.run.finish()
            self.run = None


def progress_fields(done: int, total: int, started: float, unit: str) -> dict[str, Any]:
    elapsed = max(time.perf_counter() - started, 1e-9)
    rate = done / elapsed
    return {
        f"{unit}_done": done,
        f"{unit}_total": total,
        "progress": done / total if total else 1.0,
        f"{unit}_per_s": rate,
        "eta_s": (total - done) / rate if rate > 0 else None,
    }
