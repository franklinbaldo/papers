import pytest

from semantic_atlas.observation import (
    require_observable_energy,
    tail_window,
    tail_window_texts,
)


def test_tail_window_preserves_newest_text():
    text = "A" * 100 + "CHANGING-CONTINUATION"
    observed = tail_window(text, max_chars=32)

    assert len(observed) == 32
    assert observed.endswith("CHANGING-CONTINUATION")
    assert observed != text[:32]


def test_tail_window_is_applied_identically_to_batches():
    texts = ["prefix-" + "x" * 20 + "-one", "prefix-" + "y" * 20 + "-two"]

    assert tail_window_texts(texts, max_chars=12) == [
        tail_window(text, max_chars=12) for text in texts
    ]


def test_observability_gate_rejects_degenerate_observer():
    with pytest.raises(RuntimeError, match="transfer_observer"):
        require_observable_energy(
            observer="transfer_observer",
            train_energy=0.0,
            test_energy=0.0,
            minimum=1e-12,
        )


def test_observability_gate_accepts_nonzero_dynamics():
    require_observable_energy(
        observer="transfer_observer",
        train_energy=1e-4,
        test_energy=2e-4,
        minimum=1e-12,
    )
