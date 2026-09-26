"""
Unit tests for Section 5 mathematical engine and formulas.
"""

import unittest
from terminaltyper.core.metrics import calculate_metrics
from terminaltyper.core.models import ActionType


class TestCombatMetrics(unittest.TestCase):
    def test_perfect_typing_metrics(self):
        # Target: 5 characters, typed in 1.5 seconds (0.025 minutes)
        # Gross WPM = (5 / 5.0) / 0.025 = 40.0 WPM
        metrics = calculate_metrics("slash", "slash", 1.5)
        self.assertEqual(metrics.matching_chars, 5)
        self.assertEqual(metrics.accuracy, 1.0)
        self.assertAlmostEqual(metrics.gross_wpm, 40.0, places=2)
        self.assertAlmostEqual(metrics.net_wpm, 40.0, places=2)
        self.assertFalse(metrics.is_crit)  # Net WPM < 70
        self.assertEqual(metrics.crit_multiplier, 1.0)

    def test_critical_strike_trigger(self):
        # Target: 10 chars, typed in 1.2 seconds -> (10/5.0) / (1.2/60.0) = 2.0 / 0.02 = 100 WPM
        metrics = calculate_metrics("shatterxyz", "shatterxyz", 1.2)
        self.assertEqual(metrics.accuracy, 1.0)
        self.assertAlmostEqual(metrics.net_wpm, 100.0, places=2)
        self.assertTrue(metrics.is_crit)  # Net WPM >= 70 and Acc == 100%
        self.assertEqual(metrics.crit_multiplier, 1.5)

    def test_accuracy_and_net_wpm_with_typos(self):
        # Target: "freeze", Typed: "frezzz"
        # Length = 6, Matching at i=0,1,2,4 ('f','r','e','z') -> 4 matches
        # matching = 4, max_len = 6 -> accuracy = 4 / 6 = 0.6667
        metrics = calculate_metrics("freeze", "frezzz", 2.0)
        self.assertEqual(metrics.matching_chars, 4)
        self.assertAlmostEqual(metrics.accuracy, 4 / 6, places=2)
        # Gross WPM = (6 / 5.0) / (2.0 / 60.0) = 1.2 / 0.03333 = 36.0
        self.assertAlmostEqual(metrics.gross_wpm, 36.0, places=2)
        # Net WPM = 36.0 * (4 / 6) = 24.0
        self.assertAlmostEqual(metrics.net_wpm, 24.0, places=2)
        self.assertFalse(metrics.is_crit)

    def test_accuracy_with_unequal_lengths(self):
        # Target: "flash", Typed: "flas" (incomplete)
        # Matching: 4, max_len = 5 -> accuracy = 4/5 = 0.80
        metrics = calculate_metrics("flash", "flas", 1.0)
        self.assertEqual(metrics.matching_chars, 4)
        self.assertAlmostEqual(metrics.accuracy, 0.80, places=2)

        # Target: "bolt", Typed: "bolter" (overshot)
        # Matching: 4, max_len = 6 -> accuracy = 4/6 = 0.6667
        metrics_over = calculate_metrics("bolt", "bolter", 1.0)
        self.assertEqual(metrics_over.matching_chars, 4)
        self.assertAlmostEqual(metrics_over.accuracy, 4 / 6, places=2)

    def test_zero_time_guard(self):
        # Ensure no ZeroDivisionError on 0.0 seconds
        metrics = calculate_metrics("test", "test", 0.0)
        self.assertGreater(metrics.gross_wpm, 0.0)
        self.assertEqual(metrics.accuracy, 1.0)

    def test_action_thresholds(self):
        # Check thresholds defined in Section 5.2
        self.assertEqual(ActionType.JAB.accuracy_threshold, 0.70)
        self.assertEqual(ActionType.HEAVY.accuracy_threshold, 0.80)
        self.assertEqual(ActionType.PARRY.accuracy_threshold, 0.90)
        self.assertEqual(ActionType.REST.accuracy_threshold, 0.85)
        self.assertEqual(ActionType.RECOVERY.accuracy_threshold, 0.70)


if __name__ == "__main__":
    unittest.main()
