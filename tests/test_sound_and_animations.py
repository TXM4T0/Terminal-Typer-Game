"""
Unit tests for retro sound manager, WAV playback, and visual animations.
"""

import io
import os
import unittest
from unittest.mock import patch

from terminaltyper.core.models import ActionType, Boss, BossMove, GameSettings, Player
from terminaltyper.core.sound import SoundManager, sound
from terminaltyper.data.loader import DataLoader
from terminaltyper.game.battle import BattleSession
from terminaltyper.ui.animations import animate_sector_warp, generate_dissolved_art


class TestSoundAndAnimations(unittest.TestCase):
    def test_sfx_wav_files_integrity(self):
        sfx_dir = sound._sfx_dir
        self.assertTrue(sfx_dir.is_dir(), f"SFX directory does not exist: {sfx_dir}")

        expected_files = [
            "click.wav", "error.wav", "select.wav", "jab.wav", "heavy.wav",
            "crit.wav", "parry.wav", "heal.wav", "fumble.wav", "boss_attack.wav",
            "boss_crit.wav", "victory.wav", "game_over.wav", "alert.wav", "tick.wav"
        ]
        for fname in expected_files:
            wav_path = sfx_dir / fname
            self.assertTrue(wav_path.is_file(), f"Missing SFX file: {fname}")
            with open(wav_path, "rb") as f:
                header = f.read(4)
                self.assertEqual(header, b"RIFF", f"{fname} is not a valid RIFF WAV file")

    def test_sound_manager_playback_methods(self):
        # Verify all methods execute without error
        sound_methods = [
            sound.key_click,
            sound.key_error,
            sound.menu_select,
            sound.jab_hit,
            sound.heavy_hit,
            sound.critical_hit,
            sound.parry_defend,
            sound.heal_rest,
            sound.fumble,
            sound.boss_attack,
            sound.boss_crit,
            sound.victory_fanfare,
            sound.game_over_tune,
            sound.status_alert,
            sound.hp_drain_tick,
        ]
        for method in sound_methods:
            try:
                method()
            except Exception as e:
                self.fail(f"Sound method {method.__name__} raised exception: {e}")

    def test_generate_dissolved_art(self):
        sample_art = [
            "  (o_o)  ",
            " ( > < ) ",
            "  - - -  "
        ]
        # Step 0: matches original
        step0 = generate_dissolved_art(sample_art, step=0, total_steps=4)
        self.assertEqual(step0, sample_art)

        # Step 2: partially dissolved
        step2 = generate_dissolved_art(sample_art, step=2, total_steps=4)
        self.assertEqual(len(step2), len(sample_art))
        # Ensure spaces are preserved
        self.assertEqual(step2[0][0], " ")
        self.assertEqual(step2[0][1], " ")

        # Final step: fully dissolved into spaces
        final_step = generate_dissolved_art(sample_art, step=4, total_steps=4)
        for line in final_step:
            self.assertTrue(line.isspace() or line == "")

    def test_animate_sector_warp(self):
        with patch("terminaltyper.core.terminal.Terminal.clear_screen", return_value=None), \
             patch("time.sleep", return_value=None), \
             patch("sys.stdout", new=io.StringIO()):
            animate_sector_warp(sector_num=1, total_sectors=7, enabled=True)
            animate_sector_warp(sector_num=2, total_sectors=7, enabled=False)

    def test_battle_session_animations(self):
        loader = DataLoader()
        boss = loader.get_all_bosses()[0]
        player = Player(name="TEST", level=1, max_hp=100, current_hp=100)
        settings = GameSettings(sound_enabled=False, screen_shake=False, animations_enabled=True)
        session = BattleSession(boss, player, loader, settings)

        with patch.object(session, "_draw_frame", return_value=None), \
             patch("time.sleep", return_value=None):
            # Test strike animations
            for action in [ActionType.JAB, ActionType.HEAVY, ActionType.PARRY, ActionType.REST, ActionType.RECOVERY]:
                session._animate_strike(action, is_crit=True)

            # Test HP drain animation
            session._animate_hp_drain(boss, start_hp=100, target_hp=50)
            self.assertEqual(boss.current_hp, 50)

            # Test boss defeat dissolve
            session._animate_boss_defeat_dissolve()

            # Test boss attack animation
            session._animate_boss_attack(boss.moves[0], is_crit=False)


if __name__ == "__main__":
    unittest.main()
