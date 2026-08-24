from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


FloatArray = NDArray[np.float64]


def additive_control(
    *,
    n_a: int = 4,
    n_b: int = 5,
    d: int = 6,
    seed: int = 0,
) -> FloatArray:
    """Strict additive null H(a,b)=u(a)+v(b)+c for Gate 0."""

    if n_a < 2 or n_b < 2 or d < 1:
        raise ValueError("n_a/n_b must be >=2 and d must be >=1")
    rng = np.random.default_rng(seed)
    u = rng.normal(size=(n_a, d))
    v = rng.normal(size=(n_b, d))
    c = rng.normal(size=(d,))
    return c[None, None, :] + u[:, None, :] + v[None, :, :]


def xor_control(*, interaction_scale: float = 2.0) -> tuple[FloatArray, NDArray[np.int64]]:
    """2×2 activation grid with explicit XOR-coded interaction.

    Dimensions 0 and 1 contain only factor main effects. Dimension 2 carries
    the joint XOR relation. This is a positive control for the extractor, not
    evidence for a semantic claim.
    """

    if interaction_scale <= 0:
        raise ValueError("interaction_scale must be positive")

    h = np.zeros((2, 2, 3), dtype=float)
    labels = np.zeros((2, 2), dtype=np.int64)
    for a in range(2):
        for b in range(2):
            y = a ^ b
            labels[a, b] = y
            h[a, b, 0] = -1.0 if a == 0 else 1.0
            h[a, b, 1] = -1.0 if b == 0 else 1.0
            h[a, b, 2] = interaction_scale * (-1.0 if y == 0 else 1.0)
    return h, labels
