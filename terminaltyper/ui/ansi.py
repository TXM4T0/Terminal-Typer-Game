"""
ANSI escape codes, color definitions, and layout string utilities.
"""

import re

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDERLINE = "\033[4m"
REVERSE = "\033[7m"

# Standard foregrounds
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright foregrounds
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Backgrounds
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

ANSI_REGEX = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Removes all ANSI escape codes from string."""
    return ANSI_REGEX.sub("", text)


def visible_len(text: str) -> int:
    """Calculates visible character count ignoring ANSI formatting."""
    return len(strip_ansi(text))


def cyan(text: str) -> str:
    return f"{BRIGHT_CYAN}{text}{RESET}"


def green(text: str) -> str:
    return f"{BRIGHT_GREEN}{text}{RESET}"


def red(text: str) -> str:
    return f"{BRIGHT_RED}{text}{RESET}"


def yellow(text: str) -> str:
    return f"{BRIGHT_YELLOW}{text}{RESET}"


def magenta(text: str) -> str:
    return f"{BRIGHT_MAGENTA}{text}{RESET}"


def dim(text: str) -> str:
    return f"{DIM}{text}{RESET}"


def bold(text: str) -> str:
    return f"{BOLD}{text}{RESET}"


def make_hp_bar(current: int, max_hp: int, bar_length: int = 20) -> str:
    """
    Renders an 8-bit style HP bar: [████████████░░░░░░░░]
    Colors dynamic based on HP percentage: Green (>50%), Yellow (25-50%), Red (<25%).
    """
    if max_hp <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, current / max_hp))

    filled_chars = int(round(ratio * bar_length))
    empty_chars = bar_length - filled_chars

    filled_str = "█" * filled_chars
    empty_str = "░" * empty_chars

    if ratio > 0.50:
        bar_color = BRIGHT_GREEN
    elif ratio > 0.25:
        bar_color = BRIGHT_YELLOW
    else:
        bar_color = BRIGHT_RED

    return f"[{bar_color}{filled_str}{RESET}{DIM}{empty_str}{RESET}]"
