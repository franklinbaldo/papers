from __future__ import annotations

import sys
from pathlib import Path

import torch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from fewnerd_malecns_ner_smoke import _token_logits  # noqa: E402


def test_token_logits_average_pre_softmax_byte_logits() -> None:
    byte_logits = torch.tensor(
        [
            [2.0, 0.0],
            [4.0, 2.0],
            [99.0, 99.0],  # separator: outside all token spans
            [0.0, 6.0],
        ]
    )
    got = _token_logits(byte_logits, ((0, 2), (3, 4)))
    expected = torch.tensor([[3.0, 1.0], [0.0, 6.0]])
    assert torch.equal(got, expected)
