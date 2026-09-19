import unittest

from colony import SpecialistReport
from recruitment_bandit import ContextualPolicyBandit, freshness_context


class RecruitmentBanditTests(unittest.TestCase):
    def test_freshness_context_uses_report_age(self):
        fresh = [SpecialistReport("a", "x", 0.0, 1.0, age_ms=20.0, modality="camera")]
        stale = [SpecialistReport("b", "x", 0.0, 1.0, age_ms=500.0, modality="camera")]
        self.assertEqual(freshness_context(fresh), "fresh")
        self.assertEqual(freshness_context(stale), "stale")

    def test_bandit_learns_better_action_for_context(self):
        bandit = ContextualPolicyBandit(("a", "b"), epsilon=0.0, seed=1)
        bandit.update("fresh", "a", -0.3)
        bandit.update("fresh", "b", -0.1)
        self.assertEqual(bandit.best_action("fresh"), "b")

    def test_incremental_mean(self):
        bandit = ContextualPolicyBandit(("a",), epsilon=0.0, seed=1)
        bandit.update("fresh", "a", 1.0)
        bandit.update("fresh", "a", 3.0)
        self.assertAlmostEqual(bandit.values[("fresh", "a")], 2.0)

    def test_unknown_action_is_rejected(self):
        bandit = ContextualPolicyBandit(("a",), epsilon=0.0, seed=1)
        with self.assertRaises(ValueError):
            bandit.update("fresh", "b", 0.0)


if __name__ == "__main__":
    unittest.main()
