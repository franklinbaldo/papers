from __future__ import annotations

from collections.abc import Iterable


def tail_window(text: str, *, max_chars: int) -> str:
    """Return a deterministic suffix window that preserves the newest trajectory text."""
    if max_chars < 1:
        raise ValueError("max_chars must be >= 1")
    return text[-max_chars:]


def tail_window_texts(texts: Iterable[str], *, max_chars: int) -> list[str]:
    """Apply the same frozen suffix observation window to every text state."""
    return [tail_window(text, max_chars=max_chars) for text in texts]


def require_observable_energy(
    *, observer: str, train_energy: float, test_energy: float, minimum: float
) -> None:
    """Reject a scientifically invalid run whose observer sees no trajectory motion."""
    if minimum < 0:
        raise ValueError("minimum must be >= 0")
    if train_energy <= minimum or test_energy <= minimum:
        raise RuntimeError(
            f"DGCT observability failure for {observer}: "
            f"train_energy={train_energy:.6g}, test_energy={test_energy:.6g}, "
            f"minimum={minimum:.6g}"
        )
