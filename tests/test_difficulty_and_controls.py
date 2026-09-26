"""
Unit tests validating Difficulty Modes (BABY, NORMAL, HARD),
alternative control schemes (ARROWS, WASD, HYBRID),
and arrow-only attacks in Baby Mode.
"""

import unittest
from unittest.mock import patch

from terminaltyper.core.models import (
    DifficultyMode, ControlScheme, GameSettings, Player, ActionType, StatusType
)
from terminaltyper.core.terminal import Terminal, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
from terminaltyper.core.metrics import calculate_metrics
from terminaltyper.data.loader import DataLoader
from terminaltyper.game.battle import BattleSession
from terminaltyper.ui.renderer import BattleRenderer
from terminaltyper.ui.ansi import visible_len


class TestDifficultyAndControls(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.bosses = self.loader.get_all_bosses()

    def test_difficulty_properties(self):
        # Baby Mode specs
        self.assertEqual(DifficultyMode.BABY.timer_multiplier, 1.5)
        self.assertEqual(DifficultyMode.BABY.boss_damage_multiplier, 0.6)
        self.assertEqual(DifficultyMode.BABY.accuracy_offset, -0.10)
        self.assertEqual(DifficultyMode.BABY.crit_wpm_threshold, 35.0)

        # Normal Mode specs
        self.assertEqual(DifficultyMode.NORMAL.timer_multiplier, 1.0)
        self.assertEqual(DifficultyMode.NORMAL.boss_damage_multiplier, 1.0)
        self.assertEqual(DifficultyMode.NORMAL.accuracy_offset, 0.0)
        self.assertEqual(DifficultyMode.NORMAL.crit_wpm_threshold, 70.0)

        # Hard Mode specs
        self.assertEqual(DifficultyMode.HARD.timer_multiplier, 0.75)
        self.assertEqual(DifficultyMode.HARD.boss_damage_multiplier, 1.25)
        self.assertEqual(DifficultyMode.HARD.accuracy_offset, 0.05)
        self.assertEqual(DifficultyMode.HARD.crit_wpm_threshold, 75.0)

        # King Hell Mode specs
        self.assertEqual(DifficultyMode.KING_HELL.timer_multiplier, 0.55)
        self.assertEqual(DifficultyMode.KING_HELL.boss_damage_multiplier, 1.5)
        self.assertEqual(DifficultyMode.KING_HELL.accuracy_offset, 0.08)
        self.assertEqual(DifficultyMode.KING_HELL.crit_wpm_threshold, 80.0)

    def test_normalize_directional_input(self):
        # Physical arrow keys
        self.assertEqual(Terminal.normalize_directional_input(KEY_UP, ControlScheme.HYBRID), "↑")
        self.assertEqual(Terminal.normalize_directional_input(KEY_DOWN, ControlScheme.HYBRID), "↓")
        self.assertEqual(Terminal.normalize_directional_input(KEY_LEFT, ControlScheme.HYBRID), "←")
        self.assertEqual(Terminal.normalize_directional_input(KEY_RIGHT, ControlScheme.HYBRID), "→")

        # WASD alternative controls
        for up_key in ("w", "W"):
            self.assertEqual(Terminal.normalize_directional_input(up_key, ControlScheme.HYBRID), "↑")
        for down_key in ("s", "S"):
            self.assertEqual(Terminal.normalize_directional_input(down_key, ControlScheme.HYBRID), "↓")
        for left_key in ("a", "A"):
            self.assertEqual(Terminal.normalize_directional_input(left_key, ControlScheme.HYBRID), "←")
        for right_key in ("d", "D"):
            self.assertEqual(Terminal.normalize_directional_input(right_key, ControlScheme.HYBRID), "→")

        # Numpad controls
        self.assertEqual(Terminal.normalize_directional_input("8", ControlScheme.HYBRID), "↑")
        self.assertEqual(Terminal.normalize_directional_input("2", ControlScheme.HYBRID), "↓")
        self.assertEqual(Terminal.normalize_directional_input("4", ControlScheme.HYBRID), "←")
        self.assertEqual(Terminal.normalize_directional_input("6", ControlScheme.HYBRID), "→")

        # Windows console scancodes (Up='H', Down='P', Left='K', Right='M')
        self.assertEqual(Terminal.normalize_directional_input("H", ControlScheme.HYBRID), "↑")
        self.assertEqual(Terminal.normalize_directional_input("P", ControlScheme.HYBRID), "↓")
        self.assertEqual(Terminal.normalize_directional_input("K", ControlScheme.HYBRID), "←")
        self.assertEqual(Terminal.normalize_directional_input("M", ControlScheme.HYBRID), "→")
        self.assertEqual(Terminal.normalize_directional_input("H", ControlScheme.ARROWS), "↑")

        # Direct Unicode arrows passthrough
        for arrow in ("↑", "↓", "←", "→"):
            self.assertEqual(Terminal.normalize_directional_input(arrow, ControlScheme.HYBRID), arrow)

        # Scheme filtering
        # ARROWS scheme should reject WASD
        self.assertIsNone(Terminal.normalize_directional_input("w", ControlScheme.ARROWS))
        self.assertEqual(Terminal.normalize_directional_input(KEY_UP, ControlScheme.ARROWS), "↑")

        # WASD scheme should reject arrow keys
        self.assertIsNone(Terminal.normalize_directional_input(KEY_UP, ControlScheme.WASD))
        self.assertEqual(Terminal.normalize_directional_input("w", ControlScheme.WASD), "↑")

    def test_windows_scancode_action_selection(self):
        """Validates that action selection accepts Windows console scancodes directly (H=JAB, P=REST, etc.)."""
        boss = self.bosses[0]
        player = Player(name="OPERATOR", level=1, max_hp=100, current_hp=100)
        settings = GameSettings(control_scheme=ControlScheme.HYBRID)
        session = BattleSession(boss, player, self.loader, settings)

        with patch.object(session, "_draw_frame", return_value=None):
            # 'H' is Windows console Up Arrow scancode -> JAB
            with patch.object(Terminal, "get_char", return_value="H"):
                self.assertEqual(session._select_action(), ActionType.JAB)

            # 'P' is Windows console Down Arrow scancode -> REST
            with patch.object(Terminal, "get_char", return_value="P"):
                self.assertEqual(session._select_action(), ActionType.REST)

            # 'K' is Windows console Left Arrow scancode -> PARRY
            with patch.object(Terminal, "get_char", return_value="K"):
                self.assertEqual(session._select_action(), ActionType.PARRY)

            # 'M' is Windows console Right Arrow scancode -> HEAVY
            with patch.object(Terminal, "get_char", return_value="M"):
                self.assertEqual(session._select_action(), ActionType.HEAVY)

    def test_baby_mode_prompts_arrow_only(self):
        """Validates that for all 7 bosses, Baby Mode prompts consist ONLY of arrows and spaces."""
        allowed_chars = {"↑", "↓", "←", "→", " "}
        actions = [ActionType.JAB, ActionType.HEAVY, ActionType.PARRY, ActionType.REST, ActionType.RECOVERY]

        for boss in self.bosses:
            for action in actions:
                for _ in range(10):  # Sample multiple times
                    prompt = self.loader.get_prompt_for_action(boss, action, difficulty=DifficultyMode.BABY)
                    self.assertGreater(len(prompt), 0)
                    for ch in prompt:
                        self.assertIn(
                            ch, allowed_chars,
                            f"Boss {boss.name} {action.name} contains invalid character: {repr(ch)} in prompt: {repr(prompt)}"
                        )

    def test_baby_mode_palette_80_col(self):
        """Ensures the Baby Mode command palette strictly adheres to 80-column layout."""
        renderer = BattleRenderer(width=80)
        lines = renderer.render_command_palette(show_actions=True, baby_mode=True)
        for i, line in enumerate(lines):
            vlen = visible_len(line)
            self.assertEqual(vlen, 80, f"Line {i} visible length {vlen} != 80: {repr(line)}")
        self.assertIn("↑/1", lines[1])
        self.assertIn("→/2", lines[1])

    def test_baby_mode_combat_simulation_with_arrows(self):
        """Simulates full Baby Mode battle turn with arrow-only inputs."""
        boss = self.bosses[0]
        player = Player(name="BABY_OPERATOR", level=1, max_hp=100, current_hp=100)
        settings = GameSettings(
            sound_enabled=False,
            screen_shake=False,
            difficulty=DifficultyMode.BABY,
            control_scheme=ControlScheme.HYBRID
        )
        session = BattleSession(boss, player, self.loader, settings)

        # Verify that prompt is arrow only
        prompt = self.loader.get_prompt_for_action(boss, ActionType.JAB, difficulty=settings.difficulty)
        self.assertTrue(all(c in ("↑", "↓", "←", "→", " ") for c in prompt))

        # Test action selection using Arrow Up or 'w'
        with patch.object(session, "_draw_frame", return_value=None):
            with patch.object(Terminal, "get_char", return_value=KEY_UP):
                selected = session._select_action()
                self.assertEqual(selected, ActionType.JAB)

            with patch.object(Terminal, "get_char", return_value="w"):
                selected_wasd = session._select_action()
                self.assertEqual(selected_wasd, ActionType.JAB)

            with patch.object(Terminal, "get_char", return_value=KEY_RIGHT):
                selected_heavy = session._select_action()
                self.assertEqual(selected_heavy, ActionType.HEAVY)

    def test_calculate_metrics_with_custom_crit_threshold(self):
        # Baby Mode crit threshold is 35.0 WPM
        # Typing 40 WPM with 100% accuracy should trigger Crit on Baby Mode
        metrics_baby = calculate_metrics(
            target="↑ ↓ →",
            typed="↑ ↓ →",
            elapsed_seconds=1.5,
            crit_threshold=DifficultyMode.BABY.crit_wpm_threshold
        )
        self.assertEqual(metrics_baby.accuracy, 1.0)
        self.assertGreaterEqual(metrics_baby.net_wpm, 35.0)
        self.assertTrue(metrics_baby.is_crit)
        self.assertEqual(metrics_baby.crit_multiplier, 1.5)

        # In Normal Mode (70 WPM threshold), 40 WPM should NOT trigger Crit
        metrics_normal = calculate_metrics(
            target="↑ ↓ →",
            typed="↑ ↓ →",
            elapsed_seconds=1.5,
            crit_threshold=DifficultyMode.NORMAL.crit_wpm_threshold
        )
        self.assertFalse(metrics_normal.is_crit)
        self.assertEqual(metrics_normal.crit_multiplier, 1.0)

    def test_terminal_get_char_windows_scancodes(self):
        """Simulates Windows msvcrt prefix \xe0 followed by H/P/K/M, verifying KEY_UP/KEY_DOWN return."""
        import sys
        if sys.platform == "win32":
            import msvcrt
            # Mock msvcrt sequence for Up Arrow: \xe0 then 'H'
            with patch.object(msvcrt, "kbhit", side_effect=[True, True]):
                with patch.object(msvcrt, "getwch", side_effect=["\xe0", "H"]):
                    key = Terminal.get_char(timeout=0.2)
                    self.assertEqual(key, KEY_UP)

            # Mock msvcrt sequence for Down Arrow: \xe0 then 'P'
            with patch.object(msvcrt, "kbhit", side_effect=[True, True]):
                with patch.object(msvcrt, "getwch", side_effect=["\xe0", "P"]):
                    key = Terminal.get_char(timeout=0.2)
                    self.assertEqual(key, KEY_DOWN)

            # Mock msvcrt sequence for Left Arrow: \xe0 then 'K'
            with patch.object(msvcrt, "kbhit", side_effect=[True, True]):
                with patch.object(msvcrt, "getwch", side_effect=["\xe0", "K"]):
                    key = Terminal.get_char(timeout=0.2)
                    self.assertEqual(key, KEY_LEFT)

            # Mock msvcrt sequence for Right Arrow: \xe0 then 'M'
            with patch.object(msvcrt, "kbhit", side_effect=[True, True]):
                with patch.object(msvcrt, "getwch", side_effect=["\xe0", "M"]):
                    key = Terminal.get_char(timeout=0.2)
                    self.assertEqual(key, KEY_RIGHT)

    def test_no_randomized_capitals_or_symbols_in_bosses(self):
        """Verifies that all 7 bosses use only proper text without randomized capitals or random symbols."""
        forbidden_symbols = set("!@#$%^&*()_{}[]:;<>?~`|\\")
        for boss in self.bosses:
            for bank_name, words in boss.word_banks.items():
                for word in words:
                    # Check for forbidden symbols
                    found_symbols = [c for c in word if c in forbidden_symbols]
                    self.assertEqual(
                        found_symbols, [],
                        f"Boss {boss.name} {bank_name} has invalid symbols: {found_symbols} in '{word}'"
                    )
                    # Check for randomized capitals (e.g. eChO, DeFeAt, mIrRoR)
                    # In proper text, capital letters only appear at the start of sentences/proper nouns,
                    # not alternating like 'eChO' or 'PhAnToM' or 'SyNtAx'
                    for token in word.split():
                        # If a token has an uppercase letter after a lowercase letter (camelCase or alternating),
                        # it's randomized capital
                        has_lower_before_upper = any(
                            token[i].islower() and token[i + 1].isupper()
                            for i in range(len(token) - 1)
                        )
                        self.assertFalse(
                            has_lower_before_upper,
                            f"Boss {boss.name} {bank_name} token '{token}' in '{word}' has randomized capitals!"
                        )

    def test_king_hell_prompts_are_paragraphs(self):
        """Validates that for all 7 bosses, King Hell prompts are proper paragraphs (length > 50 chars)."""
        actions = [ActionType.JAB, ActionType.HEAVY, ActionType.PARRY, ActionType.REST, ActionType.RECOVERY]
        for boss in self.bosses:
            for action in actions:
                for _ in range(5):
                    prompt = self.loader.get_prompt_for_action(boss, action, difficulty=DifficultyMode.KING_HELL)
                    self.assertGreater(len(prompt), 50, f"Boss {boss.name} {action.name} paragraph prompt is too short: {prompt}")
                    # Verify proper English text: has spaces, ends with punctuation or proper word
                    self.assertIn(" ", prompt)
                    # Verify no forbidden symbols
                    for sym in ("#", "@", "%", "*", "$", "^", "&", "<", ">", "{", "}", "[", "]"):
                        self.assertNotIn(sym, prompt)

    def test_king_hell_paragraph_renderer_80_col(self):
        """Validates that multi-line paragraph rendering in execution box strictly conforms to 80 columns."""
        renderer = BattleRenderer(width=80)
        long_paragraph = (
            "Gathering all your kinetic momentum into a thunderous overhead blow, "
            "you drive your blade deep into the bubbling center. Caustic acid erupts "
            "in violent waves as the core ruptures under the overwhelming concussive force."
        )
        lines = renderer.render_execution_box(
            dialogue="[!] TARGET MATRIX SHATTERED",
            prompt=long_paragraph,
            typed="Gathering all your kinetic momentum into a thunderous overhead blow",
            target_original=long_paragraph,
            telemetry_line="TIME: [██████████] 15.0s | WPM: 85.0 | LEN: 67/206",
        )
        self.assertGreater(len(lines), 5, "Multi-line paragraph should wrap into multiple rows.")
        for idx, line in enumerate(lines):
            vlen = visible_len(line)
            self.assertEqual(vlen, 80, f"Execution box row {idx} visible length {vlen} != 80: {repr(line)}")

    def test_settings_difficulty_cycling(self):
        """Tests that settings menu difficulty cycles BABY -> NORMAL -> HARD -> KING_HELL -> BABY."""
        import io
        settings = GameSettings(difficulty=DifficultyMode.BABY)
        from terminaltyper.game.settings import configure_settings

        with patch("sys.stdout", new=io.StringIO()):
            # Cycle 1: BABY -> NORMAL
            with patch.object(Terminal, "clear_screen"), \
                 patch.object(Terminal, "flush_input"), \
                 patch.object(Terminal, "get_char", side_effect=["1", "0"]):
                configure_settings(settings)
                self.assertEqual(settings.difficulty, DifficultyMode.NORMAL)

            # Cycle 2: NORMAL -> HARD
            with patch.object(Terminal, "clear_screen"), \
                 patch.object(Terminal, "flush_input"), \
                 patch.object(Terminal, "get_char", side_effect=["1", "0"]):
                configure_settings(settings)
                self.assertEqual(settings.difficulty, DifficultyMode.HARD)

            # Cycle 3: HARD -> KING_HELL
            with patch.object(Terminal, "clear_screen"), \
                 patch.object(Terminal, "flush_input"), \
                 patch.object(Terminal, "get_char", side_effect=["1", "0"]):
                configure_settings(settings)
                self.assertEqual(settings.difficulty, DifficultyMode.KING_HELL)

            # Cycle 4: KING_HELL -> BABY
            with patch.object(Terminal, "clear_screen"), \
                 patch.object(Terminal, "flush_input"), \
                 patch.object(Terminal, "get_char", side_effect=["1", "0"]):
                configure_settings(settings)
                self.assertEqual(settings.difficulty, DifficultyMode.BABY)

    def test_king_hell_combat_simulation(self):
        """Simulates full King Hell combat turn where player attacks using a paragraph prompt."""
        boss = self.bosses[0]
        player = Player(name="KING_COURIER", level=1, max_hp=100, current_hp=100)
        settings = GameSettings(
            sound_enabled=False,
            screen_shake=False,
            difficulty=DifficultyMode.KING_HELL
        )
        session = BattleSession(boss, player, self.loader, settings)

        # Prompt should be a paragraph
        paragraph_prompt = self.loader.get_prompt_for_action(boss, ActionType.HEAVY, difficulty=settings.difficulty)
        self.assertGreater(len(paragraph_prompt), 50)

        # Simulate typing the paragraph accurately at 85 WPM (yielding critical strike!)
        def mock_typing_loop(target_original, displayed_prompt, time_limit, action):
            elapsed = (len(target_original) / 5.0) / (85.0 / 60.0)
            return target_original, elapsed

        with patch.object(session, "_draw_frame", return_value=None), \
             patch.object(session, "_wait_for_advance", return_value=None), \
             patch.object(session, "_select_action", return_value=ActionType.HEAVY), \
             patch.object(session, "_run_typing_loop", side_effect=mock_typing_loop):
            session._execute_player_turn()
            # Net WPM ~ 85 >= 80 crit threshold for KING_HELL -> Crit!
            # Heavy damage ~ 85 * 2.2 * 1.5 = ~280 damage -> slays boss!
            self.assertEqual(boss.current_hp, 0)
            self.assertGreater(player.total_damage_dealt, 100)
            self.assertEqual(player.total_crits, 1)


if __name__ == "__main__":
    unittest.main()
