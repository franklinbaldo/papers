"""Optional local dense-compute backend selection for MaleCNS experiments.

This module deliberately does not change any existing CUDA/Kaggle runner.  It is
used only by local experiments that want to benchmark or offload the small dense
trainable modules (channel adapters / flavour heads) while leaving the sparse
MaleCNS reservoir on CPU.

DirectML is imported lazily so Linux CI and CUDA environments do not need the
Windows-only package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch


@dataclass(frozen=True)
class DenseBackend:
    name: str
    device: Any
    device_name: str


def directml_available() -> bool:
    try:
        import torch_directml  # type: ignore

        _ = torch_directml.device()
        return True
    except Exception:
        return False


def _directml_backend() -> DenseBackend:
    try:
        import torch_directml  # type: ignore
    except Exception as exc:  # pragma: no cover - Windows-only dependency
        raise RuntimeError(
            "DirectML requested but torch-directml is not importable. "
            "Install it in an isolated Windows environment before using "
            "--dense-device directml."
        ) from exc

    device = torch_directml.device()
    try:
        name = str(torch_directml.device_name(0))
    except Exception:  # pragma: no cover - backend/version dependent
        name = "DirectML device 0"
    return DenseBackend(name="directml", device=device, device_name=name)


def resolve_dense_backend(requested: str) -> DenseBackend:
    requested = requested.lower().strip()
    if requested == "cpu":
        return DenseBackend(name="cpu", device=torch.device("cpu"), device_name="CPU")
    if requested == "directml":
        return _directml_backend()
    if requested == "auto":
        if directml_available():
            return _directml_backend()
        return DenseBackend(name="cpu", device=torch.device("cpu"), device_name="CPU")
    raise ValueError(f"unknown dense backend: {requested!r}; expected cpu, directml, or auto")


def barrier(value: torch.Tensor) -> None:
    """Force completion without relying on backend-specific synchronize APIs."""
    # A host read is intentionally used because torch-directml does not expose
    # the same synchronization API as CUDA across all supported versions.
    _ = float(value.detach().reshape(-1)[0].cpu())
