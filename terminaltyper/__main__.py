"""
Main entry point for Terminal Typer: Battle Protocol.
"""

import sys
from terminaltyper.core.terminal import Terminal
from terminaltyper.core.models import GameSettings
from terminaltyper.core.sound import sound
from terminaltyper.ui.animations import run_bios_post_sequence, render_title_screen
from terminaltyper.game.engine import GameEngine
from terminaltyper.game.settings import configure_settings
from terminaltyper.game.typing_test import run_typing_test


def main():
    settings = GameSettings()
    Terminal.hide_cursor()

    try:
        # 1. Fake Hardware POST & Loading Sequence (Section 2.1)
        run_bios_post_sequence(fast_mode=False)

        # 2. Main Title Menu Loop (Section 2.2)
        while True:
            render_title_screen(settings)
            Terminal.flush_input()
            choice = Terminal.get_char()
            if choice is None:
                continue

            choice = choice.strip()
            if choice == "1":
                # New Run / Campaign
                sound.menu_select()
                engine = GameEngine(settings)
                engine.run_campaign()
            elif choice == "2":
                # Settings
                sound.menu_select()
                configure_settings(settings)
            elif choice == "3":
                # Typing Test / Calibration
                sound.menu_select()
                run_typing_test()
            elif choice == "4":
                # Quit
                sound.menu_select()
                Terminal.clear_screen()
                print("\n  [SYSTEM SHUTDOWN: TERMINAL LINK SEVERED]\n")
                break
    except KeyboardInterrupt:
        Terminal.clear_screen()
        print("\n  [EMERGENCY ABORT: SESSION TERMINATED]\n")
    finally:
        Terminal.show_cursor()


if __name__ == "__main__":
    main()
