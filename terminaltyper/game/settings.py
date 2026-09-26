"""
Settings and configuration management for Terminal Typer.
"""

import sys
from terminaltyper.core.terminal import Terminal
from terminaltyper.core.models import GameSettings, DifficultyMode, ControlScheme
from terminaltyper.core.sound import sound
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_WHITE
)


def configure_settings(settings: GameSettings) -> None:
    """Interactive Settings menu."""
    while True:
        Terminal.clear_screen()
        diff_name = settings.difficulty.name
        if diff_name == "BABY":
            diff_color = BRIGHT_GREEN
        elif diff_name == "HARD":
            diff_color = BRIGHT_RED
        elif diff_name == "KING_HELL":
            diff_color = BRIGHT_MAGENTA
        else:
            diff_color = BRIGHT_CYAN
        diff_display = f"{diff_color}{settings.difficulty.label}{RESET}"

        controls_display = f"{BRIGHT_WHITE}{settings.control_scheme.label}{RESET}"
        sound_status = f"{BRIGHT_GREEN}ENABLED{RESET}" if settings.sound_enabled else f"{BRIGHT_RED}DISABLED{RESET}"
        shake_status = f"{BRIGHT_GREEN}ENABLED{RESET}" if settings.screen_shake else f"{BRIGHT_RED}DISABLED{RESET}"
        anim_status = f"{BRIGHT_GREEN}ENABLED{RESET}" if settings.animations_enabled else f"{BRIGHT_RED}DISABLED{RESET}"

        if settings.text_speed_delay == 0.0:
            speed_str = "INSTANT"
        elif settings.text_speed_delay <= 0.008:
            speed_str = "FAST"
        else:
            speed_str = "RETRO (Normal)"

        if settings.timer_multiplier >= 1.4:
            timer_mode = "RELAXED (+50% Window)"
        elif settings.timer_multiplier <= 0.8:
            timer_mode = "HARDCORE (-25% Window)"
        else:
            timer_mode = "STANDARD (Normal)"

        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}")
        print(f"{BRIGHT_CYAN}| [TERMINAL PROTOCOL SETTINGS & SYSTEM CONFIG]                                |{RESET}")
        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}\n")

        print(f"   [{BRIGHT_GREEN}1{RESET}] Difficulty Mode         : {diff_display}")
        print(f"   [{BRIGHT_GREEN}2{RESET}] Alternative Controls   : {controls_display}")
        print(f"   [{BRIGHT_GREEN}3{RESET}] Audio / 8-Bit SFX       : {sound_status}")
        print(f"   [{BRIGHT_GREEN}4{RESET}] Narrative Text Speed    : {BRIGHT_WHITE}{speed_str}{RESET}")
        print(f"   [{BRIGHT_GREEN}5{RESET}] Combat Timer Scaling    : {BRIGHT_WHITE}{timer_mode}{RESET}")
        print(f"   [{BRIGHT_GREEN}6{RESET}] Screen Flash / Impact   : {shake_status}")
        print(f"   [{BRIGHT_GREEN}7{RESET}] Combat & VFX Animations : {anim_status}")
        print(f"   [{BRIGHT_YELLOW}R{RESET}] Reset to Default Settings")
        print(f"   [{BRIGHT_RED}0{RESET}] Save & Return to Main Menu\n")

        sys.stdout.write(f"{BRIGHT_WHITE}Configure Option > {RESET}")
        sys.stdout.flush()

        Terminal.flush_input()
        ch = Terminal.get_char()
        if ch is None:
            continue
        ch = ch.strip().upper()

        if ch == "0":
            sound.menu_select()
            break
        elif ch == "1":
            sound.menu_select()
            if settings.difficulty == DifficultyMode.BABY:
                settings.difficulty = DifficultyMode.NORMAL
            elif settings.difficulty == DifficultyMode.NORMAL:
                settings.difficulty = DifficultyMode.HARD
            elif settings.difficulty == DifficultyMode.HARD:
                settings.difficulty = DifficultyMode.KING_HELL
            else:
                settings.difficulty = DifficultyMode.BABY
        elif ch == "2":
            sound.menu_select()
            if settings.control_scheme == ControlScheme.HYBRID:
                settings.control_scheme = ControlScheme.ARROWS
            elif settings.control_scheme == ControlScheme.ARROWS:
                settings.control_scheme = ControlScheme.WASD
            else:
                settings.control_scheme = ControlScheme.HYBRID
        elif ch == "3":
            settings.sound_enabled = not settings.sound_enabled
            sound.enabled = settings.sound_enabled
            if sound.enabled:
                sound.menu_select()
        elif ch == "4":
            sound.menu_select()
            if settings.text_speed_delay == 0.0:
                settings.text_speed_delay = 0.015
            elif settings.text_speed_delay >= 0.012:
                settings.text_speed_delay = 0.005
            else:
                settings.text_speed_delay = 0.0
        elif ch == "5":
            sound.menu_select()
            if settings.timer_multiplier == 1.0:
                settings.timer_multiplier = 1.5
            elif settings.timer_multiplier > 1.0:
                settings.timer_multiplier = 0.75
            else:
                settings.timer_multiplier = 1.0
        elif ch == "6":
            sound.menu_select()
            settings.screen_shake = not settings.screen_shake
        elif ch == "7":
            sound.menu_select()
            settings.animations_enabled = not settings.animations_enabled
        elif ch == "R":
            sound.menu_select()
            settings.sound_enabled = True
            sound.enabled = True
            settings.text_speed_delay = 0.015
            settings.timer_multiplier = 1.0
            settings.screen_shake = True
            settings.animations_enabled = True
            settings.difficulty = DifficultyMode.NORMAL
            settings.control_scheme = ControlScheme.HYBRID
