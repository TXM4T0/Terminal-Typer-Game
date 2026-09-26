"""
Diagnostic Typing Test and WPM Calibration Mode.
Allows the player to warm up, test keyboard latency, and measure Net WPM across
all encounter word themes.
"""

import sys
import time
from terminaltyper.core.terminal import Terminal
from terminaltyper.core.metrics import calculate_metrics, TypingMetrics
from terminaltyper.core.sound import sound
from terminaltyper.ui.ansi import (
    RESET, BOLD, DIM, CYAN, GREEN, RED, YELLOW, MAGENTA,
    BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, BRIGHT_YELLOW, BRIGHT_WHITE,
    visible_len
)

TEST_SUITES = [
    {
        "id": "1",
        "title": "Home-Row Foundation (Slime Core)",
        "prompt": "flash glad half dash",
    },
    {
        "id": "2",
        "title": "Consonant Cadence (Iron Golem)",
        "prompt": "shatter hammer pillar bullet",
    },
    {
        "id": "3",
        "title": "High-Speed Bursts (Swift Falcon)",
        "prompt": "bolt dash wing wind gust dart",
    },
    {
        "id": "4",
        "title": "Reflections & Phantoms (Shadow Doppelgänger)",
        "prompt": "shattered mirror image reflection phantom double",
    },
    {
        "id": "5",
        "title": "Punctuation & Hyphens (Frost Lich)",
        "prompt": "ice-cold freeze-thaw it's crystal-clear",
    },
    {
        "id": "6",
        "title": "Mainframes & Architecture (Cyber Mech)",
        "prompt": "quantum mainframe overload circuit breaker disruption",
    },
    {
        "id": "7",
        "title": "Full Prose & Cadence (Void Sovereign)",
        "prompt": "The abyss looks back through broken glass.",
    },
    {
        "id": "8",
        "title": "Directional Protocol (Baby Mode Reflexes)",
        "prompt": "↑ ↑ ↓ ↓ ← → ← →",
    },
    {
        "id": "9",
        "title": "King Hell Warfare (Paragraph Trial)",
        "prompt": "The ancient mainframe trembles under pressure as surging voltage overloads the auxiliary cooling system and triggers emergency shutdown protocols.",
    },
]


def run_typing_test() -> None:
    """Main entry point for typing test and calibration."""
    while True:
        Terminal.clear_screen()
        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}")
        print(f"{BRIGHT_CYAN}| [DIAGNOSTIC TELEMETRY & TYPING CALIBRATION]                                 |{RESET}")
        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}\n")

        print(" Select a calibration suite to benchmark:\n")
        for item in TEST_SUITES:
            print(f"   [{BRIGHT_GREEN}{item['id']}{RESET}] {item['title']}")
        print(f"   [{BRIGHT_YELLOW}A{RESET}] Run Complete Comprehensive Benchmark (All Suites)")
        print(f"   [{BRIGHT_RED}0{RESET}] Return to Main Menu\n")

        sys.stdout.write(f"{BRIGHT_WHITE}Selection > {RESET}")
        sys.stdout.flush()

        Terminal.flush_input()
        choice = Terminal.get_char()
        if choice is None:
            continue

        choice = choice.strip().upper()
        if choice == "0":
            sound.menu_select()
            break
        elif choice == "A":
            sound.menu_select()
            _run_suite_sequence(TEST_SUITES)
        else:
            selected = next((s for s in TEST_SUITES if s["id"] == choice), None)
            if selected:
                sound.menu_select()
                _run_suite_sequence([selected])


def _run_suite_sequence(suites: list[dict]) -> None:
    results: list[TypingMetrics] = []

    for suite in suites:
        metric = _execute_single_test(suite["title"], suite["prompt"])
        results.append(metric)

    # Show aggregate report
    _display_diagnostic_report(results)


def _execute_single_test(title: str, target: str) -> TypingMetrics:
    Terminal.clear_screen()
    print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}")
    print(f"{BRIGHT_CYAN}| TARGET SUITE: {title[:60]:<62} |{RESET}")
    print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}\n")

    print(f" PROMPT : {BRIGHT_WHITE}{BOLD}{target}{RESET}")
    print(f" INPUT  : {DIM}Press ENTER when ready to begin typing...{RESET}\n")

    Terminal.flush_input()
    while True:
        ch = Terminal.get_char(timeout=0.1)
        if ch == "\n":
            sound.menu_select()
            break

    # Begin timed run
    Terminal.clear_screen()
    typed = ""
    start_time = time.perf_counter()
    is_arrow_mode = any(arrow in target for arrow in ("↑", "↓", "←", "→"))

    while True:
        elapsed = max(0.001, time.perf_counter() - start_time)
        cur_mins = elapsed / 60.0
        cur_wpm = (len(typed) / 5.0) / cur_mins

        Terminal.move_cursor(1, 1)
        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}")
        print(f"{BRIGHT_CYAN}| TARGET SUITE: {title[:60]:<62} |{RESET}")
        print(f"{BRIGHT_CYAN}+------------------------------------------------------------------------------+{RESET}")
        print(f" PROMPT : {BRIGHT_WHITE}{BOLD}{target}{RESET}")

        # Highlight input
        colored_input = ""
        for i, c in enumerate(typed):
            if i < len(target):
                if c == target[i]:
                    colored_input += f"{BRIGHT_GREEN}{c}{RESET}"
                else:
                    colored_input += f"{BRIGHT_RED}{c}{RESET}"
            else:
                colored_input += f"{BRIGHT_RED}{c}{RESET}"
        colored_input += f"{BRIGHT_WHITE}_{RESET}"

        print(f" INPUT  : {colored_input}")
        print(f"\n TIME: {elapsed:.2f}s | LIVE WPM: {cur_wpm:.1f} | LEN: {len(typed)}/{len(target)}")
        helper_text = "Use arrow keys or WASD" if is_arrow_mode else "Type prompt exactly and press ENTER when finished"
        print(f"{DIM}[{helper_text}]{RESET}")

        ch = Terminal.get_char(timeout=0.03)
        if ch is not None:
            if ch == "\n":
                sound.menu_select()
                break
            elif ch == "\b":
                if typed.endswith(" "):
                    typed = typed[:-2]
                elif len(typed) > 0:
                    typed = typed[:-1]
                sound.key_click()
            else:
                dir_arrow = None
                if is_arrow_mode:
                    dir_arrow = Terminal.normalize_directional_input(ch)

                if dir_arrow is not None:
                    typed += dir_arrow
                    if len(typed) < len(target) and target[len(typed)] == " ":
                        typed += " "
                    idx = len(typed) - (2 if typed.endswith(" ") else 1)
                    if idx < len(target) and typed[idx] == target[idx]:
                        sound.key_click()
                    else:
                        sound.key_error()
                    if typed == target:
                        time.sleep(0.05)
                        break
                elif len(ch) == 1 and ch.isprintable():
                    typed += ch
                    idx = len(typed) - 1
                    if idx < len(target) and typed[idx] == target[idx]:
                        sound.key_click()
                    else:
                        sound.key_error()

                    # If full match reached
                    if typed == target:
                        time.sleep(0.05)
                        break

    elapsed_final = time.perf_counter() - start_time
    metrics = calculate_metrics(target, typed, elapsed_final)
    return metrics


def _display_diagnostic_report(metrics_list: list[TypingMetrics]) -> None:
    Terminal.clear_screen()
    print(f"{BRIGHT_GREEN}+------------------------------------------------------------------------------+{RESET}")
    print(f"{BRIGHT_GREEN}| [DIAGNOSTIC CALIBRATION REPORT]                                              |{RESET}")
    print(f"{BRIGHT_GREEN}+------------------------------------------------------------------------------+{RESET}\n")

    total_gross = sum(m.gross_wpm for m in metrics_list) / len(metrics_list)
    total_acc = sum(m.accuracy for m in metrics_list) / len(metrics_list)
    total_net = sum(m.net_wpm for m in metrics_list) / len(metrics_list)

    print(f" {'TEST':<4} | {'TIME':<6} | {'GROSS WPM':<10} | {'ACCURACY':<9} | {'NET WPM':<9} | {'CRIT'}")
    print(" " + "-" * 72)

    for i, m in enumerate(metrics_list, 1):
        crit_str = f"{BRIGHT_YELLOW}YES (1.5x){RESET}" if m.is_crit else f"{DIM}NO{RESET}"
        acc_pct = f"{m.accuracy * 100:.1f}%"
        print(f" #{i:<3} | {m.elapsed_seconds:>5.2f}s | {m.gross_wpm:>9.1f}  | {acc_pct:>8}  | {m.net_wpm:>8.1f}  | {crit_str}")

    print(" " + "-" * 72)
    acc_total_pct = f"{total_acc * 100:.1f}%"
    print(f" AVG  | {'---':>6} | {total_gross:>9.1f}  | {acc_total_pct:>8}  | {total_net:>8.1f}  |\n")

    # Courier Rank calculation
    if total_net >= 90 and total_acc >= 0.98:
        rank = f"{BRIGHT_YELLOW}CYBER OPERATOR / PROTOCOL MASTER{RESET}"
    elif total_net >= 70 and total_acc >= 0.90:
        rank = f"{BRIGHT_GREEN}SENIOR SYNTAX COURIER{RESET}"
    elif total_net >= 45:
        rank = f"{BRIGHT_CYAN}STANDARD NETWORK RUNNER{RESET}"
    else:
        rank = f"{BRIGHT_WHITE}RECRUIT / IN TRAINING{RESET}"

    print(f" OPERATOR CLASSIFICATION: {rank}\n")
    print(f"{DIM}Press [ENTER] to return to menu...{RESET}")

    Terminal.flush_input()
    while True:
        ch = Terminal.get_char(timeout=0.1)
        if ch in ("\n", " "):
            sound.menu_select()
            break
