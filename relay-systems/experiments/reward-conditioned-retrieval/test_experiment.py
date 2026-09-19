from __future__ import annotations

import unittest

from experiment import EnvConfig, run_one


class RetrievalExperimentTests(unittest.TestCase):
    def test_candidate_recall_is_high(self) -> None:
        result = run_one(
            "cosine_only",
            seed=3,
            train_episodes=100,
            eval_episodes=500,
            top_k=4,
            env_config=EnvConfig(),
        )
        self.assertGreater(result.candidate_recall, 0.90)

    def test_reward_conditioned_beats_cosine(self) -> None:
        config = EnvConfig(n_contexts=12, chunks_per_context=4, dim=24)
        cosine = run_one(
            "cosine_only",
            seed=7,
            train_episodes=4_000,
            eval_episodes=1_000,
            top_k=4,
            env_config=config,
        )
        learned = run_one(
            "reward_conditioned",
            seed=7,
            train_episodes=4_000,
            eval_episodes=1_000,
            top_k=4,
            env_config=config,
        )
        self.assertGreater(learned.eval_reward, cosine.eval_reward + 0.35)
        self.assertGreater(learned.eval_reward, 0.75)

    def test_frozen_evaluation_is_reproducible(self) -> None:
        config = EnvConfig(n_contexts=8, chunks_per_context=4, dim=16)
        first = run_one(
            "reward_conditioned",
            seed=11,
            train_episodes=2_000,
            eval_episodes=400,
            top_k=4,
            env_config=config,
        )
        second = run_one(
            "reward_conditioned",
            seed=11,
            train_episodes=2_000,
            eval_episodes=400,
            top_k=4,
            env_config=config,
        )
        self.assertEqual(first.as_dict(), second.as_dict())


if __name__ == "__main__":
    unittest.main()
