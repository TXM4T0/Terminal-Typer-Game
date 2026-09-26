"""
Cinematic animations, Fake BIOS POST sequence, Title Screen,
and HEX-8 Operator transmissions.
"""

import sys
import time
from terminaltyper.core.terminal import Terminal
from terminaltyper.core.sound import sound
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_MAGENTA, BRIGHT_WHITE, visible_len
)

TITLE_ASCII = """
  _______ _____ _____  __  __ _____ _   _          _      
 |__   __|_   _|  __ \\|  \\/  |_   _| \\ | |   /\\   | |     
    | |    | | | |__) | \\  / | | | |  \\| |  /  \\  | |     
    | |    | | |  ___/| |\\/| | | | | . ` | / /\\ \\ | |     
    | |   _| |_| |    | |  | |_| |_| |\\  |/ ____ \\| |____ 
    |_|  |_____|_|    |_|  |_|_____|_| \\_/_/    \\_\\______|
"""


def typewriter(text: str, delay: float = 0.015, sound_click: bool = True) -> None:
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        if sound_click and ch not in (' ', '\n', '\t'):
            sound.key_click()
        if delay > 0:
            if Terminal.is_key_pressed():
                Terminal.get_char()
            else:
                time.sleep(delay)


def run_bios_post_sequence(fast_mode: bool = False) -> None:
    Terminal.clear_screen()
    delay = 0.005 if fast_mode else 0.02
    pause = 0.05 if fast_mode else 0.25

    header = (
        f"{BRIGHT_WHITE}BIOS-ROM (C) 1998 PROTO-LOGIC SYSTEMS INC.{RESET}\n"
        "CPU: TYPE-R 486DX @ 66MHz | SYSTEM MEMORY: 640KB BASE, 15360KB EXTENDED\n"
        "PORT 0x3F8: KEYBOARD CONTROLLER DETECTED (BUFF_LEN: 128 BYTES)\n\n"
    )
    typewriter(header, delay=delay, sound_click=False)
    time.sleep(pause)

    ok_steps = [
        'INITIALIZING TERMINAL BUFFER (80x25)',
        'MOUNTING VIRTUAL FILE SYSTEM: /dev/tty0',
        'CALIBRATING KEYSTROKE LATENCY CLOCK (perf_counter_ns)',
        'PARSING DICTIONARY CORPUS (WORDS: 4,096 ENTRIES)',
        'COMPILING ASCII SPRITE CACHES (7 BOSS TARGETS LOADED)',
    ]

    for step in ok_steps:
        if Terminal.is_key_pressed():
            Terminal.get_char()
            pause = 0.0
            delay = 0.0

        sys.stdout.write(f"[{BRIGHT_GREEN}  OK  {RESET}] {step}\n")
        sys.stdout.flush()
        sound.key_click()
        time.sleep(pause)

    print('\nLOADING BATTLE PROTOCOL SUBSYSTEMS:')

    p1 = f"[{BRIGHT_CYAN}{'█' * 28}{DIM}{'░' * 10}{RESET}] 72% (Loading Combat Audio Emulation)\n"
    sys.stdout.write(p1)
    sys.stdout.flush()
    time.sleep(0.05 if fast_mode else 0.35)

    p2 = f"[{BRIGHT_GREEN}{'█' * 38}{RESET}] 100% PROTOCOL SYNCHRONIZED.\n\n"
    sys.stdout.write(p2)
    sys.stdout.flush()
    sound.menu_select()
    time.sleep(0.05 if fast_mode else 0.2)

    prompt = f"{BRIGHT_YELLOW}PRESS [ENTER] TO INITIALIZE TERMINAL LINK...{RESET}"
    sys.stdout.write(prompt)
    sys.stdout.flush()

    Terminal.flush_input()
    Terminal.wait_for_enter()
    sound.menu_select()


def render_title_screen(settings=None) -> None:
    Terminal.clear_screen()
    print(f"{BRIGHT_CYAN}{TITLE_ASCII}{RESET}")
    print(f"  {BRIGHT_WHITE}========================================================{RESET}")
    print(f"             {BRIGHT_YELLOW}--- B A T T L E   P R O T O C O L ---{RESET}")
    print(f"  {BRIGHT_WHITE}========================================================{RESET}")
    print(f"            {BRIGHT_GREEN}[1] NEW RUN{RESET}        {BRIGHT_CYAN}[2] SETTINGS{RESET}")
    print(f"            {BRIGHT_YELLOW}[3] TYPING TEST{RESET}    {BRIGHT_RED}[4] QUIT{RESET}\n")
    if settings:
        diff_str = settings.difficulty.name
        ctrl_str = settings.control_scheme.name
        print(f"  {DIM}DIFFICULTY: [{diff_str}] | CONTROLS: [{ctrl_str}] | VER: 1.0.4a{RESET}\n")
    else:
        print(f"  {DIM}CURRENT DRIVER: ANSI-COLOR-80COL | VER: 1.0.4a{RESET}\n")
    sys.stdout.write(f"  {BRIGHT_WHITE}SELECT OPTION [1-4] > {RESET}")
    sys.stdout.flush()


def show_hex8_transmission(text_speed: float = 0.01) -> None:
    Terminal.clear_screen()
    border = "+------------------------------------------------------------------------------+"
    lines = [
        f" {BRIGHT_MAGENTA}[HEX-8 SYSTEM ADVISORY]{RESET}",
        "",
        ' "Courier, connection established. The Network Core has succumbed to syntax',
        ' corruption. Seven Anomalies have barricaded the root directory.',
        "",
        ' Standard weaponry will not register. Your interface converts pure keystroke',
        ' velocity and character accuracy into destructive resonant frequencies.',
        "",
        ' Rules of engagement:',
        f' 1. Strike fast to maximize impact velocity ({BRIGHT_GREEN}WPM{RESET}).',
        ' 2. Maintain perfect cadence: inaccuracies degrade your damage output.',
        ' 3. If you falter, the anomalies will retaliate without hesitation.',
        "",
        ' Sector 1 entrance detected. Purge the core, Courier."'
    ]

    print(f"{CYAN}{border}{RESET}")
    for raw in lines:
        vlen = visible_len(raw)
        pad = ' ' * max(0, 78 - vlen)
        print(f"{CYAN}|{RESET}{raw}{pad}{CYAN}|{RESET}")
    print(f"{CYAN}{border}{RESET}\n")

    prompt = f"{BRIGHT_YELLOW}PRESS [ENTER] TO COMMENCE PURGE PROTOCOL...{RESET}"
    sys.stdout.write(prompt)
    sys.stdout.flush()

    Terminal.flush_input()
    Terminal.wait_for_enter()
    sound.menu_select()


def flash_screen(color_bg: str = '\x1b[41m', duration: float = 0.06) -> None:
    sys.stdout.write(f"{color_bg}\x1b[2J\x1b[H")
    sys.stdout.flush()
    time.sleep(duration)
    sys.stdout.write(f"{RESET}\x1b[2J\x1b[H")
    sys.stdout.flush()


def animate_sector_warp(sector_num: int, total_sectors: int, enabled: bool = True) -> None:
    """Retro hyperspace warp drive animation when entering a sector."""
    if not enabled:
        return

    warp_frames = [
        ("INITIALIZING WARP DRIVE...", [
            "  .                                                             .            ",
            "         .                     .                 .                           ",
            "                  .                       .                        .         ",
            "        .                       .                       .                    ",
            "  .                                                                          ",
        ]),
        ("ALIGNING SECTOR RESONANCE MATRIX...", [
            "  --  -             -- -        -      - -             - --             --   ",
            "          - -           --                 - -               - -             ",
            "  -             -- -            -- -               - --            - -       ",
            "        -- -            - -            - -             -- -            - -   ",
            "  --            --              - -            --              - -           ",
        ]),
        ("MAXIMUM VELOCITY: HYPERSPACE LINK ESTABLISHED", [
            "  ==============================================================================",
            "  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
            "  ==============================================================================",
            "  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
            "  ==============================================================================",
        ]),
        (f"DROPPING FROM WARP: SECTOR {sector_num}/{total_sectors} REACHED", [
            "  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
            f"                     [ TARGET VECTOR LOCKED: SECTOR {sector_num} ]                    ",
            "  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
            "                                                                              ",
            "                                                                              ",
        ])
    ]

    colors = [CYAN, BRIGHT_CYAN, BRIGHT_YELLOW, BRIGHT_GREEN]
    for i, (status, rows) in enumerate(warp_frames):
        Terminal.clear_screen()
        c = colors[i % len(colors)]
        print(f"\n  {BRIGHT_WHITE}+--------------------------------------------------------------------------+{RESET}")
        print(f"  {BRIGHT_WHITE}|{RESET} {c}{status:<72}{RESET} {BRIGHT_WHITE}|{RESET}")
        print(f"  {BRIGHT_WHITE}+--------------------------------------------------------------------------+{RESET}\n")
        for r in rows:
            print(f"  {c}{r}{RESET}")
        sound.key_click()
        time.sleep(0.08)

    time.sleep(0.10)


def generate_dissolved_art(ascii_art: list[str], step: int, total_steps: int = 5) -> list[str]:
    """
    Procedurally dissolves ASCII art into glitch/noise particles over progressive steps.
    """
    if step <= 0:
        return list(ascii_art)
    if step >= total_steps:
        return [" " * len(line) for line in ascii_art]

    noise_palette = ["#", "@", "%", "*", "+", ".", " "]
    progress = step / float(total_steps)

    dissolved = []
    for line in ascii_art:
        chars = []
        for ch in line:
            if ch == " ":
                chars.append(" ")
            elif (hash((ch, line, step)) % 100) / 100.0 < progress:
                p_idx = min(len(noise_palette) - 1, int(progress * len(noise_palette)))
                chars.append(noise_palette[p_idx])
            else:
                chars.append(ch)
        dissolved.append("".join(chars))

    return dissolved