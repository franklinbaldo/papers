"""Low-rank residual channel flavorizer for multi-scale semantic text channels.

In the MaleCNS research programme (see ``semantic-flavour-pyramid.md`` and
``whole-brain-semantic-state.md``), a frozen connectome need not be a good
zero-shot transform of raw generic text embeddings (which were trained for cosine
similarity, not biological neural dynamics).

A trainable low-rank flavorizer learns to present semantic distinctions in
directions that the recurrent substrate (8,982 sensory neurons -> 165k brain)
can preserve, propagate, and amplify:
    C' = C + tanh(C @ V.T) @ U.T

Properties:
- Operates on cached multi-scale channel features (zero re-embedding of MiniLM/E5).
- U is zero-initialized: at step 0, C' = C (exact identity transformation).
- Low rank (rank=4 to rank=16): parameter footprint is under 300 KB.
- Both PyTorch (for GPU Stage B recurrence) and NumPy implementations provided.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ChannelFlavorizerConfig:
    semantic_dim: int
    rank: int = 8
    seed: int = 20260915

    def as_dict(self) -> dict[str, Any]:
        return {
            "semantic_dim": self.semantic_dim,
            "rank": self.rank,
            "seed": self.seed,
        }


class ChannelFlavorizer:
    """NumPy low-rank residual channel flavorizer."""

    def __init__(self, semantic_dim: int, rank: int = 8, seed: int = 20260915):
        self.semantic_dim = int(semantic_dim)
        self.rank = int(rank)
        self.seed = int(seed)
        rng = np.random.default_rng(seed)
        # V: down-projection (Gaussian scaled by 1/sqrt(dim))
        self.V = (rng.standard_normal((self.rank, self.semantic_dim)) / np.sqrt(self.semantic_dim)).astype(np.float32)
        # U: up-projection (zero-initialized for identity at start)
        self.U = np.zeros((self.semantic_dim, self.rank), dtype=np.float32)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Apply residual flavorizer: x + tanh(x @ V.T) @ U.T."""
        x = np.asarray(x, dtype=np.float32)
        h = np.tanh(x @ self.V.T)
        delta = h @ self.U.T
        return x + delta

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.forward(x)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            V=self.V,
            U=self.U,
            semantic_dim=self.semantic_dim,
            rank=self.rank,
            seed=self.seed,
        )

    @classmethod
    def load(cls, path: str | Path) -> ChannelFlavorizer:
        data = np.load(path, allow_pickle=False)
        obj = cls(
            semantic_dim=int(data["semantic_dim"]),
            rank=int(data["rank"]),
            seed=int(data["seed"]),
        )
        obj.V = data["V"]
        obj.U = data["U"]
        return obj


def make_torch_flavorizer(semantic_dim: int, rank: int = 8, seed: int = 20260915, device="cpu"):
    """Create PyTorch low-rank residual flavorizer module."""
    import torch
    import torch.nn as nn

    class TorchChannelFlavorizer(nn.Module):
        def __init__(self, sem_dim: int, r: int, s: int):
            super().__init__()
            self.semantic_dim = sem_dim
            self.rank = r
            rng = torch.Generator().manual_seed(s)
            v_init = torch.randn((r, sem_dim), generator=rng) / (sem_dim ** 0.5)
            self.V = nn.Parameter(v_init.to(torch.float32))
            self.U = nn.Parameter(torch.zeros((sem_dim, r), dtype=torch.float32))

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            h = torch.tanh(torch.matmul(x, self.V.T))
            return x + torch.matmul(h, self.U.T)

    mod = TorchChannelFlavorizer(semantic_dim, rank, seed)
    return mod.to(device)


def train_flavorizer(
    features: np.ndarray,
    labels: np.ndarray,
    *,
    semantic_dim: int,
    rank: int = 8,
    epochs: int = 5,
    lr: float = 0.005,
    batch_size: int = 512,
    seed: int = 20260915,
    device: str = "cpu",
) -> ChannelFlavorizer:
    """Train low-rank channel flavorizer to separate fine classes in channel space.

    Uses balanced cross-entropy with a lightweight linear projection head,
    encouraging V and U to amplify informative channel directions for the
    connectome before recurrent propagation.
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim

    mod = make_torch_flavorizer(semantic_dim, rank=rank, seed=seed, device=device)
    n_classes = int(labels.max()) + 1
    head = nn.Linear(semantic_dim, n_classes).to(device)

    # Class frequencies for balanced loss
    counts = np.bincount(labels, minlength=n_classes).astype(np.float32)
    weights = np.ones(n_classes, dtype=np.float32)
    non_zero = counts > 0
    weights[non_zero] = (counts.sum() / (n_classes * counts[non_zero])).clip(max=50.0)
    if n_classes > 1:
        weights[0] = 0.2
    weight_tensor = torch.as_tensor(weights, dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)

    optimizer = optim.Adam(list(mod.parameters()) + list(head.parameters()), lr=lr)

    n_samples = len(labels)
    rng = np.random.default_rng(seed)

    for _ in range(epochs):
        indices = rng.permutation(n_samples)
        for start in range(0, n_samples, batch_size):
            batch_idx = indices[start : start + batch_size]
            bx = torch.as_tensor(features[batch_idx], dtype=torch.float32, device=device)
            by = torch.as_tensor(labels[batch_idx], dtype=torch.int64, device=device)

            optimizer.zero_grad()
            flavorized = mod(bx)
            logits = head(flavorized)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()

    flav = ChannelFlavorizer(semantic_dim=semantic_dim, rank=rank, seed=seed)
    flav.V = mod.V.detach().cpu().numpy().astype(np.float32)
    flav.U = mod.U.detach().cpu().numpy().astype(np.float32)
    return flav

