"""
Unit tests validating all 7 Boss encounters, moves, HP, and dialogue specs from Section 7.
"""

import unittest
from terminaltyper.data.loader import DataLoader
from terminaltyper.core.models import StatusType


class TestBossManifest(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.bosses = self.loader.get_all_bosses()

    def test_boss_count_and_names(self):
        self.assertEqual(len(self.bosses), 7)
        expected_names = [
            "Slime Core",
            "Iron Golem",
            "Swift Falcon",
            "Shadow Doppelgänger",
            "Frost Lich",
            "Cyber Mech",
            "Void Sovereign",
        ]
        actual_names = [b.name for b in self.bosses]
        self.assertEqual(actual_names, expected_names)

    def test_boss_hp_and_levels(self):
        # Section 7 stats
        expected_stats = {
            "Slime Core": (120, 3),
            "Iron Golem": (220, 6),
            "Swift Falcon": (180, 8),
            "Shadow Doppelgänger": (260, 11),
            "Frost Lich": (320, 15),
            "Cyber Mech": (400, 18),
            "Void Sovereign": (550, 20),
        }
        for b in self.bosses:
            exp_hp, exp_lvl = expected_stats[b.name]
            self.assertEqual(b.max_hp, exp_hp, f"Boss {b.name} HP mismatch")
            self.assertEqual(b.level, exp_lvl, f"Boss {b.name} Level mismatch")

    def test_swift_falcon_speed_limit(self):
        # Section 7 Boss 3: Swift Falcon strict time limit <= 2.5s
        falcon = next(b for b in self.bosses if b.name == "Swift Falcon")
        self.assertIsNotNone(falcon.speed_limit_seconds)
        self.assertLessEqual(falcon.speed_limit_seconds, 2.5)

    def test_boss_moves_and_weights(self):
        for b in self.bosses:
            total_weight = sum(m.weight for m in b.moves)
            self.assertEqual(total_weight, 100, f"Boss {b.name} move weights do not sum to 100")
            for m in b.moves:
                self.assertGreater(m.max_dmg, 0)
                self.assertLessEqual(m.min_dmg, m.max_dmg)

    def test_dialogue_keys(self):
        for b in self.bosses:
            self.assertIn("encounter", b.dialogue)
            self.assertIn("midfight", b.dialogue)
            self.assertIn("defeat", b.dialogue)

    def test_word_banks_present(self):
        for b in self.bosses:
            self.assertIn("jab", b.word_banks)
            self.assertIn("heavy", b.word_banks)
            self.assertIn("parry", b.word_banks)
            self.assertIn("rest", b.word_banks)
            self.assertGreater(len(b.word_banks["jab"]), 0)
            self.assertGreater(len(b.word_banks["heavy"]), 0)


if __name__ == "__main__":
    unittest.main()
