"""
Unit tests ensuring 80-column fixed layout adherence across all screens and boxes.
"""

import unittest
from terminaltyper.core.models import Player, Boss, ActionType, StatusType
from terminaltyper.data.loader import DataLoader
from terminaltyper.ui.renderer import BattleRenderer
from terminaltyper.ui.ansi import visible_len


class TestRendererLayout(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.bosses = self.loader.get_all_bosses()
        self.renderer = BattleRenderer(width=80)

    def test_all_bosses_arena_width(self):
        player = Player(name="COURIER", level=14, max_hp=150, current_hp=150)

        for boss in self.bosses:
            arena_lines = self.renderer.render_arena(boss, player)
            for i, line in enumerate(arena_lines):
                vlen = visible_len(line)
                self.assertEqual(
                    vlen, 80,
                    f"Boss {boss.name} arena row {i} visible length {vlen} != 80: {repr(line)}"
                )

    def test_execution_box_width(self):
        test_dialogues = [
            'The Frost Lich whispers: "Your cadence is slowing to absolute zero"',
            'A very long dialogue line that needs truncation or padding properly across the entire terminal display safely without breaking',
            'Short'
        ]
        for dlg in test_dialogues:
            lines = self.renderer.render_execution_box(
                dialogue=dlg,
                prompt="freeze-thaw cycle",
                typed="freeze-thaw c",
                target_original="freeze-thaw cycle",
                telemetry_line="TIME: [██████████] 4.2s | WPM: 85.0 | ACC: 100%",
            )
            for i, line in enumerate(lines):
                vlen = visible_len(line)
                self.assertEqual(
                    vlen, 80,
                    f"Execution box row {i} visible length {vlen} != 80: {repr(line)}"
                )

    def test_command_palette_width(self):
        palette_lines = self.renderer.render_command_palette(show_actions=True)
        for i, line in enumerate(palette_lines):
            vlen = visible_len(line)
            self.assertEqual(
                vlen, 80,
                f"Command palette row {i} visible length {vlen} != 80: {repr(line)}"
            )

        status_lines = self.renderer.render_command_palette(
            status_msg="PRESS [ENTER] TO ADVANCE TURN...", show_actions=False
        )
        for i, line in enumerate(status_lines):
            vlen = visible_len(line)
            self.assertEqual(
                vlen, 80,
                f"Command palette status row {i} visible length {vlen} != 80: {repr(line)}"
            )

    def test_full_screen_composite_width(self):
        boss = self.bosses[4]  # Frost Lich
        player = Player(name="COURIER", level=15, max_hp=150, current_hp=120)
        player.add_status(StatusType.CHILL, 2)

        full_screen = self.renderer.render_full_screen(
            boss=boss,
            player=player,
            dialogue='The Frost Lich whispers: "Your cadence is slowing to absolute zero"',
            prompt="freeze-thaw cycle",
            typed="freeze-thaw c",
            target_original="freeze-thaw cycle",
            telemetry_line="TIME: [████████░░] 3.5s | WPM: 74.0 | LEN: 13/17",
            status_msg=None,
            show_actions=True,
        )

        rows = full_screen.split("\n")
        for idx, row in enumerate(rows):
            vlen = visible_len(row)
            self.assertEqual(
                vlen, 80,
                f"Full screen row {idx} visible length {vlen} != 80: {repr(row)}"
            )


if __name__ == "__main__":
    unittest.main()
