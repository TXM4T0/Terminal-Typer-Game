"""
Simulated automated battle playthrough testing the end-to-end combat loop.
"""

import unittest
from unittest.mock import patch
from terminaltyper.core.models import Player, GameSettings, ActionType
from terminaltyper.data.loader import DataLoader
from terminaltyper.game.battle import BattleSession


class TestBattleSimulation(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.bosses = self.loader.get_all_bosses()
        self.settings = GameSettings(sound_enabled=False, screen_shake=False)

    def test_simulated_battle_victory(self):
        boss = self.bosses[0]  # Slime Core (HP 120)
        player = Player(name="TEST_COURIER", level=1, max_hp=100, current_hp=100)
        session = BattleSession(boss, player, self.loader, self.settings)

        # Mock player typing: accurate fast typing yielding high damage
        def mock_typing_loop(target_original, displayed_prompt, time_limit, action):
            return target_original, 0.8  # Perfect typing in 0.8s -> ~75 WPM, Crit!

        def mock_select_action():
            return ActionType.HEAVY  # Heavy attack deals ~75 * 2.2 * 1.5 = ~247 damage -> one-shots Slime Core!

        with patch.object(session, "_wait_for_advance", return_value=None), \
             patch.object(session, "_draw_frame", return_value=None), \
             patch.object(session, "_select_action", side_effect=mock_select_action), \
             patch.object(session, "_run_typing_loop", side_effect=mock_typing_loop):
            won = session.run_encounter()
            self.assertTrue(won)
            self.assertEqual(boss.current_hp, 0)
            self.assertGreater(player.total_damage_dealt, 100)
            self.assertGreater(player.total_crits, 0)

    def test_campaign_screens_and_transmission(self):
        import io
        from terminaltyper.ui.animations import show_hex8_transmission
        from terminaltyper.game.engine import GameEngine

        with patch('terminaltyper.core.terminal.Terminal.wait_for_enter', return_value=None), \
             patch('terminaltyper.core.terminal.Terminal.flush_input', return_value=None), \
             patch('sys.stdout', new=io.StringIO()):
            show_hex8_transmission(text_speed=0.0)

            engine = GameEngine(self.settings)
            player = Player(name="TEST_COURIER", level=1, max_hp=100, current_hp=100)
            boss = self.bosses[0]
            engine._show_sector_briefing(1, 7, boss, player)
            engine._show_sector_cleared(1, boss, player)
            engine._show_game_over(1, boss, player)
            engine._show_campaign_victory(player)


if __name__ == "__main__":
    unittest.main()
