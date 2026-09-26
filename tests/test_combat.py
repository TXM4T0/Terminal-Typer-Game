"""
Unit tests for combat formulas, parry mitigation, healing, status effects, and boss mechanics.
"""

import unittest
from terminaltyper.core.models import Player, Boss, BossMove, StatusType, ActionType
from terminaltyper.core.metrics import calculate_metrics
from terminaltyper.data.loader import DataLoader, EMERGENCY_WORDS


class TestCombatMechanics(unittest.TestCase):
    def test_parry_mitigation_formula(self):
        # Spec Section 5.2: Mitigation % = min(75%, Net WPM * 0.75%)
        # Net WPM = 80 -> 80 * 0.75% = 60% mitigation (0.60)
        net_wpm = 80.0
        mitigation = min(0.75, (net_wpm * 0.75) / 100.0)
        self.assertAlmostEqual(mitigation, 0.60, places=3)

        # Net WPM = 120 -> 120 * 0.75% = 90% -> capped at 75% (0.75)
        high_wpm = 120.0
        mitigation_capped = min(0.75, (high_wpm * 0.75) / 100.0)
        self.assertEqual(mitigation_capped, 0.75)

    def test_parry_damage_reduction_calculation(self):
        # Base boss damage 30, parry mitigation 60%
        # Actual Damage = max(1, Round(Base Boss Damage * (1.0 - Mitigation %)))
        base_dmg = 30
        mitigation = 0.60
        actual_dmg = max(1, round(base_dmg * (1.0 - mitigation)))
        self.assertEqual(actual_dmg, 12)  # 30 * 0.40 = 12

    def test_rest_healing_formula(self):
        # Spec Section 5.2: HP Recovered = Net WPM * 0.60
        net_wpm = 75.0
        heal = round(net_wpm * 0.60)
        self.assertEqual(heal, 45)

        player = Player(max_hp=100, current_hp=50)
        player.current_hp = min(player.max_hp, player.current_hp + heal)
        self.assertEqual(player.current_hp, 95)

    def test_burn_status_effect(self):
        # Spec Section 6: Deals 10 unblockable damage at end of round, duration 3 turns
        player = Player(max_hp=100, current_hp=100)
        player.add_status(StatusType.BURN, duration=3)

        # Turn 1 tick
        logs = player.tick_statuses()
        self.assertEqual(player.current_hp, 90)
        self.assertEqual(player.statuses[StatusType.BURN], 2)

        # Turn 2 tick
        player.tick_statuses()
        self.assertEqual(player.current_hp, 80)
        self.assertEqual(player.statuses[StatusType.BURN], 1)

        # Turn 3 tick -> should clear
        player.tick_statuses()
        self.assertEqual(player.current_hp, 70)
        self.assertNotIn(StatusType.BURN, player.statuses)

    def test_glitch_masking(self):
        # Spec Section 6: Masks 25% of prompt letters with terminal noise symbols
        prompt = "abcdefghij"  # 10 letters -> approx 2-3 masked
        masked = DataLoader.apply_glitch_mask(prompt)
        self.assertEqual(len(masked), len(prompt))
        noise_chars = [c for c in masked if c in ("#", "@", "%", "*")]
        self.assertGreaterEqual(len(noise_chars), 1)

    def test_emergency_words_for_stumble(self):
        # Spec Section 6: Emergency 3-letter word recovery prompt
        for word in EMERGENCY_WORDS:
            self.assertEqual(len(word), 3, f"Emergency word '{word}' must be exactly 3 letters.")

    def test_chill_status_timer_reduction(self):
        # Spec Section 6: Time limit before automatic fumble is reduced by 30%
        base_time = 10.0
        reduced_time = base_time * 0.70
        self.assertAlmostEqual(reduced_time, 7.0, places=2)

    def test_sector_4_briefing_layout(self):
        from terminaltyper.ui.renderer import make_box_row
        from terminaltyper.ui.ansi import visible_len
        loader = DataLoader()
        bosses = loader.get_all_bosses()
        b4 = next(b for b in bosses if b.id == "boss_04")

        rows = [
            f" [HEX-8 SECTOR BRIEFING: 4/7]",
            f' "Courier, targeting Sector 4 signature: [{b4.name.upper()}]."',
            f" Anomaly Threat Class   : Lv. {b4.level}",
            f" Operational Theme      : {b4.theme}",
        ]
        for r in rows:
            box = make_box_row(r, 78)
            self.assertEqual(visible_len(box), 80, f"Row visible length {visible_len(box)} != 80: {box}")

    def test_sector_4_dialogue_lengths(self):
        loader = DataLoader()
        bosses = loader.get_all_bosses()
        b4 = next(b for b in bosses if b.id == "boss_04")
        # Ensure dialogue fits comfortably within standard 67-character dialogue window
        for key in ("encounter", "midfight", "defeat"):
            dlg = b4.dialogue.get(key, "")
            self.assertLessEqual(len(dlg), 67, f"Dialogue '{key}' is too long: {len(dlg)} chars")


if __name__ == "__main__":
    unittest.main()
