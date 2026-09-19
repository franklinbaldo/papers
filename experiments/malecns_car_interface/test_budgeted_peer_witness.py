import unittest

from budgeted_peer_witness import (
    AcquisitionBudget,
    BudgetedPeerFirstPolicy,
    PeerFirstResolver,
    PeerToken,
)


class TestPeerWitness(unittest.TestCase):
    def test_budget_never_overspends(self) -> None:
        budget = AcquisitionBudget(total_units=6, remaining_units=6)
        self.assertTrue(budget.buy_peer())
        self.assertTrue(budget.buy_lidar())
        self.assertFalse(budget.buy_peer())
        self.assertEqual(budget.spent_total, 6)

    def test_fresh_confident_peer_can_support_camera(self) -> None:
        decision = PeerFirstResolver().resolve(
            pair_speed=12.0,
            camera_speed=10.0,
            token=PeerToken(10.1, 0.95, 0.05),
        )
        self.assertTrue(decision.resolved)
        self.assertEqual(decision.choice, "camera_peer")
        self.assertLess(decision.estimate, 10.2)

    def test_stale_or_low_confidence_peer_is_ambiguous(self) -> None:
        decision = PeerFirstResolver().resolve(
            pair_speed=12.0,
            camera_speed=10.0,
            token=PeerToken(10.0, 0.35, 0.25),
        )
        self.assertFalse(decision.resolved)
        self.assertEqual(decision.choice, "peer_ambiguous")

    def test_policy_does_not_buy_without_persistent_conflict(self) -> None:
        policy = BudgetedPeerFirstPolicy(budget_units=20)
        for _ in range(12):
            primary = policy.observe_primary(
                obd_speed=10.0,
                gnss_speed=10.1,
                camera_speed=10.05,
            )
            policy.resolve(
                primary=primary,
                camera_speed=10.05,
                peer_token=PeerToken(10.0, 0.95, 0.05),
                lidar_speed=10.0,
            )
        self.assertEqual(policy.budget.spent_total, 0)

    def test_mild_conflict_does_not_spend_lidar_after_ambiguous_peer(self) -> None:
        policy = BudgetedPeerFirstPolicy(
            budget_units=20,
            lidar_escalation_score_min=1.50,
        )
        for _ in range(8):
            primary = policy.observe_primary(
                obd_speed=11.1,
                gnss_speed=11.0,
                camera_speed=10.0,
            )
            policy.resolve(
                primary=primary,
                camera_speed=10.0,
                peer_token=PeerToken(10.5, 0.30, 0.20),
                lidar_speed=10.0,
            )
        self.assertEqual(policy.budget.spent_lidar, 0)
        self.assertGreater(policy.budget.spent_peer, 0)

    def test_ambiguous_peer_can_escalate_to_lidar(self) -> None:
        policy = BudgetedPeerFirstPolicy(budget_units=20)
        choice = ""
        for _ in range(8):
            primary = policy.observe_primary(
                obd_speed=12.0,
                gnss_speed=12.1,
                camera_speed=10.0,
            )
            _, choice = policy.resolve(
                primary=primary,
                camera_speed=10.0,
                peer_token=PeerToken(11.0, 0.30, 0.20),
                lidar_speed=10.1,
            )
        self.assertIn(choice, {"camera_aux", "pair_aux", "ambiguous_hold_pair"})
        self.assertGreater(policy.budget.spent_lidar, 0)


if __name__ == "__main__":
    unittest.main()
