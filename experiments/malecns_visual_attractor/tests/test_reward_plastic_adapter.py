from __future__ import annotations

import numpy as np

from reward_plastic_adapter import RewardPlasticAdapter


def test_reward_plastic_adapter_reinforces_rewarded_perturbation() -> None:
    adapter = RewardPlasticAdapter.from_weight(
        np.zeros((6, 6), dtype=np.float32),
        learning_rate=0.1,
        exploration_sigma=0.2,
        eligibility_decay=0.0,
        baseline_rate=0.1,
    )
    latent = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)
    noise = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)

    before = adapter.propose(latent, np.zeros(6, dtype=np.float32))[0]
    stats = adapter.update(latent, noise, reward=1.0)
    after = adapter.propose(latent, np.zeros(6, dtype=np.float32))[0]

    assert before == 0.0
    assert after > before
    assert adapter.weight[0, 0] > 0
    assert stats["advantage"] > 0
    assert stats["weight_norm"] > 0


def test_reward_plastic_adapter_punishes_bad_perturbation() -> None:
    adapter = RewardPlasticAdapter.from_weight(
        np.zeros((6, 6), dtype=np.float32),
        learning_rate=0.1,
        exploration_sigma=0.2,
        eligibility_decay=0.0,
        baseline_rate=0.1,
    )
    latent = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)
    noise = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)

    adapter.update(latent, noise, reward=-1.0)

    assert adapter.weight[0, 0] < 0


def test_reward_plastic_adapter_eligibility_carries_delayed_credit() -> None:
    adapter = RewardPlasticAdapter.from_weight(
        np.zeros((6, 6), dtype=np.float32),
        learning_rate=0.1,
        exploration_sigma=0.2,
        eligibility_decay=0.9,
        baseline_rate=0.1,
    )
    latent = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)
    noise = np.array([1.0, 0, 0, 0, 0, 0], dtype=np.float32)

    adapter.update(latent, noise, reward=0.0)
    adapter.update(np.zeros(6, dtype=np.float32), np.zeros(6, dtype=np.float32), reward=1.0)

    assert adapter.weight[0, 0] > 0
    assert adapter.eligibility[0, 0] > 0
