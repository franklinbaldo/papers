from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class RewardPlasticAdapter:
    """Tiny online-learning layer between MaleCNS body latent and screen controls.

    The connectome remains frozen.  Learning lives only in a 6x6 weight matrix.
    Exploration perturbs the six screen-control channels; a scalar reward then
    reinforces perturbations that co-occurred with useful generator activity.
    This is a simple reward-modulated node-perturbation / three-factor rule, not
    a claim about the fly's biological dopamine machinery.
    """

    weight: np.ndarray
    eligibility: np.ndarray
    baseline: float = 0.0
    learning_rate: float = 0.02
    exploration_sigma: float = 0.08
    eligibility_decay: float = 0.95
    baseline_rate: float = 0.02
    weight_clip: float = 3.0

    @classmethod
    def from_weight(
        cls,
        weight: np.ndarray,
        *,
        learning_rate: float = 0.02,
        exploration_sigma: float = 0.08,
        eligibility_decay: float = 0.95,
        baseline_rate: float = 0.02,
        weight_clip: float = 3.0,
    ) -> "RewardPlasticAdapter":
        weight = np.asarray(weight, dtype=np.float32)
        if weight.shape != (6, 6):
            raise ValueError(f"weight must be 6x6, got {weight.shape}")
        if learning_rate < 0:
            raise ValueError("learning_rate must be >= 0")
        if exploration_sigma <= 0:
            raise ValueError("exploration_sigma must be > 0")
        if not 0 <= eligibility_decay < 1:
            raise ValueError("eligibility_decay must be in [0,1)")
        if not 0 < baseline_rate <= 1:
            raise ValueError("baseline_rate must be in (0,1]")
        if weight_clip <= 0:
            raise ValueError("weight_clip must be > 0")
        return cls(
            weight=weight.copy(),
            eligibility=np.zeros((6, 6), dtype=np.float32),
            learning_rate=float(learning_rate),
            exploration_sigma=float(exploration_sigma),
            eligibility_decay=float(eligibility_decay),
            baseline_rate=float(baseline_rate),
            weight_clip=float(weight_clip),
        )

    def propose(self, latent: np.ndarray, noise: np.ndarray) -> np.ndarray:
        """Return six bounded screen-control channels for one generator state."""
        latent = np.asarray(latent, dtype=np.float32)
        noise = np.asarray(noise, dtype=np.float32)
        if latent.shape != (6,) or noise.shape != (6,):
            raise ValueError("latent and noise must both have shape (6,)")
        raw = latent @ self.weight + self.exploration_sigma * noise
        return np.tanh(raw).astype(np.float32)

    def update(self, latent: np.ndarray, noise: np.ndarray, reward: float) -> dict[str, float]:
        """Apply one reward-modulated node-perturbation update.

        `reward` should already be a bounded engineering reward (for example the
        tanh-scaled receiver excitation advantage over a matched uniform-TV
        control).  The eligibility trace carries credit across short reward
        delays without backpropagating through the frozen connectome.
        """
        latent = np.asarray(latent, dtype=np.float32)
        noise = np.asarray(noise, dtype=np.float32)
        if latent.shape != (6,) or noise.shape != (6,):
            raise ValueError("latent and noise must both have shape (6,)")
        reward = float(reward)
        advantage = reward - float(self.baseline)
        perturbation_credit = np.outer(latent, noise) / float(self.exploration_sigma)
        self.eligibility *= float(self.eligibility_decay)
        self.eligibility += perturbation_credit.astype(np.float32)
        self.weight += float(self.learning_rate) * advantage * self.eligibility
        np.clip(self.weight, -float(self.weight_clip), float(self.weight_clip), out=self.weight)
        self.baseline += float(self.baseline_rate) * (reward - float(self.baseline))
        return {
            "reward": reward,
            "baseline": float(self.baseline),
            "advantage": float(advantage),
            "weight_norm": float(np.linalg.norm(self.weight)),
            "eligibility_norm": float(np.linalg.norm(self.eligibility)),
        }
