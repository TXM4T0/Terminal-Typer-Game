"""
80-Column ANSI layout engine for Terminal Typer: Battle Protocol.
Zone 1: Arena Viewport (Top)
Zone 2: Dialogue & Execution Box (Middle)
Zone 3: Command Palette (Bottom)
"""

from typing import List, Optional
from terminaltyper.core.models import Boss, Player, StatusType, ActionType
from terminaltyper.ui.ansi import (
    strip_ansi, visible_len, make_hp_bar,
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_WHITE
)

BORDER_LINE = "+" + "-" * 78 + "+"


def fit_line(text: str, width: int = 78) -> str:
    """Pads or cleanly trims text to exactly width visible characters."""
    vlen = visible_len(text)
    if vlen < width:
        return text + (" " * (width - vlen))
    elif vlen == width:
        return text
    else:
        # If longer, strip ANSI and slice to fit
        plain = strip_ansi(text)
        return plain[:width]


def make_box_row(content: str, width: int = 78) -> str:
    """Wraps content with side borders: |<content padded to 78>|"""
    return f"|{fit_line(content, width)}|"


def wrap_prompt_ranges(prompt: str, max_width: int = 66) -> List[tuple[int, int]]:
    """
    Splits prompt into slice ranges (start, end) where each slice has <= max_width chars,
    breaking preferentially at spaces.
    """
    if len(prompt) <= max_width:
        return [(0, len(prompt))]
    ranges = []
    idx = 0
    while idx < len(prompt):
        if len(prompt) - idx <= max_width:
            ranges.append((idx, len(prompt)))
            break
        chunk_end = idx + max_width
        space_idx = prompt.rfind(" ", idx, chunk_end + 1)
        if space_idx != -1 and space_idx > idx:
            ranges.append((idx, space_idx + 1))
            idx = space_idx + 1
        else:
            ranges.append((idx, chunk_end))
            idx = chunk_end
    return ranges


class BattleRenderer:
    def __init__(self, width: int = 80):
        self.width = width
        self.content_width = width - 2

    def render_arena(self, boss: Boss, player: Player) -> List[str]:
        """
        Renders the top Arena Viewport (Boss at top-right, Player at bottom-left).
        """
        lines = []
        lines.append(BORDER_LINE)

        # Boss info
        b_name = f"[{boss.name.upper()}]"
        b_lvl = f"Lv. {boss.level}"
        # Line 1: Boss Name & Level
        boss_hdr = f" {BRIGHT_RED}{b_name}{RESET}"
        boss_hdr_pad = " " * max(1, 48 - visible_len(boss_hdr))
        line_0_left = f"{boss_hdr}{boss_hdr_pad}{DIM}{b_lvl}{RESET}"

        # Boss HP
        boss_hp_bar = make_hp_bar(boss.current_hp, boss.max_hp, bar_length=20)
        boss_hp_str = f"{boss.current_hp}/{boss.max_hp}"
        line_1_left = f" HP: {boss_hp_bar} {boss_hp_str}"

        # Boss Status
        b_status = "NORMAL"
        line_2_left = f" STATUS: [{DIM}{b_status}{RESET}]"

        # Boss ASCII art on right side
        boss_ascii = [line for line in boss.ascii_art if line.strip()]

        # Prepare grid rows for the arena viewport (11 inner rows total)
        inner_rows: List[str] = ["" for _ in range(11)]

        # Place left side elements
        inner_rows[0] = line_0_left
        inner_rows[1] = line_1_left
        inner_rows[2] = line_2_left

        # Player block on bottom-left (rows 8, 9, 10)
        p_name = f"[{player.name.upper()}]"
        p_lvl = f"Lv. {player.level}"
        p_hp_bar = make_hp_bar(player.current_hp, player.max_hp, bar_length=20)
        p_hp_str = f"{player.current_hp}/{player.max_hp}"
        p_status_display = player.get_status_display()
        status_color = BRIGHT_RED if player.statuses else GREEN

        inner_rows[8] = f"   {BRIGHT_CYAN}{p_name}{RESET} {DIM}{p_lvl}{RESET}"
        inner_rows[9] = f"   HP: {p_hp_bar} {p_hp_str}"
        inner_rows[10] = f"   STATUS: [{status_color}{p_status_display}{RESET}]"

        # Overlay Boss ASCII art on right side (columns 48+)
        for i, art_line in enumerate(boss_ascii):
            if i + 2 < len(inner_rows):
                left_part = inner_rows[i + 2]
                left_vlen = visible_len(left_part)
                target_col = 48
                if left_vlen < target_col:
                    pad = " " * (target_col - left_vlen)
                    inner_rows[i + 2] = f"{left_part}{pad}{BRIGHT_WHITE}{art_line}{RESET}"
                else:
                    inner_rows[i + 2] = f"{left_part}  {BRIGHT_WHITE}{art_line}{RESET}"

        for row in inner_rows:
            lines.append(make_box_row(row, self.content_width))

        return lines

    def render_execution_box(
        self,
        dialogue: str,
        prompt: Optional[str] = None,
        typed: str = "",
        target_original: Optional[str] = None,
        telemetry_line: Optional[str] = None,
    ) -> List[str]:
        """
        Renders the middle Dialogue & Execution Box with real-time colored input.
        Supports clean multi-line wrapping for King Hell mode paragraphs.
        """
        lines = []
        lines.append(BORDER_LINE)

        # Dialogue line (clean wrapping if too long)
        dlg_prefix = " DIALOGUE: "
        avail_dlg = self.content_width - len(dlg_prefix)
        dlg_text = dialogue if len(dialogue) <= avail_dlg else dialogue[:avail_dlg - 3] + "..."
        lines.append(make_box_row(f"{YELLOW}{dlg_prefix}{RESET}{dlg_text}", self.content_width))

        # Prompt lines
        if prompt is not None:
            ranges = wrap_prompt_ranges(prompt, 66)
            for line_idx, (s, e) in enumerate(ranges):
                prefix = f" {CYAN}PROMPT  :{RESET} " if line_idx == 0 else "           "
                chunk_prompt = prompt[s:e]
                display_chunk = ""
                for ch in chunk_prompt:
                    if ch in ("#", "@", "%", "*"):
                        display_chunk += f"{BRIGHT_RED}{BOLD}{ch}{RESET}"
                    else:
                        display_chunk += ch
                lines.append(make_box_row(prefix + display_chunk, self.content_width))
        else:
            ranges = [(0, 0)]
            lines.append(make_box_row(" PROMPT  : ---", self.content_width))

        # Input lines with real-time character-by-character color comparison
        if prompt is not None:
            compare_target = target_original if target_original else prompt
            for line_idx, (s, e) in enumerate(ranges):
                prefix = f" {CYAN}INPUT   :{RESET} " if line_idx == 0 else "           "
                if len(typed) < s:
                    lines.append(make_box_row(prefix, self.content_width))
                else:
                    display_input = ""
                    end_typed_idx = min(len(typed), e)
                    for i in range(s, end_typed_idx):
                        char = typed[i]
                        if i < len(compare_target) and char == compare_target[i]:
                            display_input += f"{BRIGHT_GREEN}{char}{RESET}"
                        else:
                            display_input += f"{BRIGHT_RED}{char}{RESET}"

                    if s <= len(typed) < e:
                        display_input += f"{BRIGHT_WHITE}{BOLD}_{RESET}"
                    elif line_idx == len(ranges) - 1 and len(typed) >= len(compare_target):
                        for i in range(e, len(typed)):
                            display_input += f"{BRIGHT_RED}{typed[i]}{RESET}"
                        display_input += f"{BRIGHT_WHITE}{BOLD}_{RESET}"

                    lines.append(make_box_row(prefix + display_input, self.content_width))
        else:
            lines.append(make_box_row(" INPUT   : ---", self.content_width))

        # Bottom row: Telemetry preview / Timer bar or empty spacer row
        if telemetry_line:
            lines.append(make_box_row(f" {telemetry_line}", self.content_width))
        else:
            lines.append(make_box_row("", self.content_width))

        return lines

    def render_command_palette(
        self,
        status_msg: Optional[str] = None,
        show_actions: bool = True,
        baby_mode: bool = False
    ) -> List[str]:
        """
        Renders the bottom Command Palette.
        """
        lines = []
        lines.append(BORDER_LINE)

        if show_actions:
            if baby_mode:
                palette_text = (
                    f" {BRIGHT_CYAN}[↑/1] JAB (Fast){RESET}  "
                    f"{BRIGHT_YELLOW}[→/2] HEAVY (Power){RESET}  "
                    f"{BRIGHT_GREEN}[←/3] PARRY (Guard){RESET}  "
                    f"{BRIGHT_MAGENTA}[↓/4] REST (Heal){RESET}"
                )
            else:
                palette_text = (
                    f" {BRIGHT_CYAN}[1] JAB (Fast){RESET}     "
                    f"{BRIGHT_YELLOW}[2] HEAVY (Power){RESET}     "
                    f"{BRIGHT_GREEN}[3] PARRY (Guard){RESET}    "
                    f"{BRIGHT_MAGENTA}[4] REST (Heal){RESET}"
                )
            lines.append(make_box_row(palette_text, self.content_width))
        elif status_msg:
            lines.append(make_box_row(f" {status_msg}", self.content_width))
        else:
            lines.append(make_box_row(" [AWAITING NEXT COMMAND...]", self.content_width))

        lines.append(BORDER_LINE)
        return lines

    def render_full_screen(
        self,
        boss: Boss,
        player: Player,
        dialogue: str,
        prompt: Optional[str] = None,
        typed: str = "",
        target_original: Optional[str] = None,
        telemetry_line: Optional[str] = None,
        status_msg: Optional[str] = None,
        show_actions: bool = True,
        baby_mode: bool = False,
    ) -> str:
        """Assembles the complete 80-column battle arena display."""
        arena_lines = self.render_arena(boss, player)
        exec_lines = self.render_execution_box(
            dialogue=dialogue,
            prompt=prompt,
            typed=typed,
            target_original=target_original,
            telemetry_line=telemetry_line,
        )
        cmd_lines = self.render_command_palette(
            status_msg=status_msg,
            show_actions=show_actions,
            baby_mode=baby_mode,
        )

        all_lines = arena_lines + exec_lines + cmd_lines
        return "\n".join(all_lines)
