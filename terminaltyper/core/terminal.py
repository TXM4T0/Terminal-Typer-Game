"""
Cross-platform terminal abstraction for raw keyboard telemetry,
ANSI terminal control, and screen management.
"""

import os
import sys
import time

# Ensure UTF-8 streams across all operating systems
for stream in (sys.stdout, sys.stderr, sys.stdin):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Windows console mode setup for ANSI escape codes and UTF-8
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    import msvcrt

    kernel32 = ctypes.windll.kernel32
    # Set Windows console code page to UTF-8 (65001)
    try:
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except Exception:
        pass

    # Enable ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004) and DISABLE_NEWLINE_AUTO_RETURN (0x0008)
    STD_OUTPUT_HANDLE = -11
    hOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    mode = wintypes.DWORD()
    if kernel32.GetConsoleMode(hOut, ctypes.byref(mode)):
        kernel32.SetConsoleMode(hOut, mode.value | 0x0004 | 0x0008)
else:
    import select
    import termios
    import tty


KEY_UP = "KEY_UP"
KEY_DOWN = "KEY_DOWN"
KEY_LEFT = "KEY_LEFT"
KEY_RIGHT = "KEY_RIGHT"


class Terminal:
    """Manages raw terminal I/O, cursor controls, and ANSI sequences."""

    KEY_UP = KEY_UP
    KEY_DOWN = KEY_DOWN
    KEY_LEFT = KEY_LEFT
    KEY_RIGHT = KEY_RIGHT

    @staticmethod
    def normalize_directional_input(ch: str | None, control_scheme=None) -> str | None:
        """
        Translates arrow keys, WASD, and numpad keys into standard directional arrow symbols (↑, ↓, ←, →).
        Respects ControlScheme settings (HYBRID, ARROWS, WASD).
        """
        if not ch:
            return None

        scheme_val = getattr(control_scheme, "value", str(control_scheme)) if control_scheme else "HYBRID"

        # Already a unicode arrow symbol
        if ch in ("↑", "↓", "←", "→"):
            return ch

        # Arrow keys / Windows console scancodes ('H'=Up, 'P'=Down, 'K'=Left, 'M'=Right)
        if scheme_val in ("HYBRID", "ARROWS"):
            if ch in (KEY_UP, "H"):
                return "↑"
            elif ch in (KEY_DOWN, "P"):
                return "↓"
            elif ch in (KEY_LEFT, "K"):
                return "←"
            elif ch in (KEY_RIGHT, "M"):
                return "→"

        # Alternative WASD keys
        if scheme_val in ("HYBRID", "WASD"):
            ch_low = ch.lower()
            if ch_low == "w":
                return "↑"
            elif ch_low == "s":
                return "↓"
            elif ch_low == "a":
                return "←"
            elif ch_low == "d":
                return "→"

        # Numpad / Vim keys in HYBRID
        if scheme_val == "HYBRID":
            if ch in ("8", "k"):
                return "↑"
            elif ch in ("2", "j"):
                return "↓"
            elif ch in ("4", "h"):  # Lowercase 'h' is Vim left; uppercase 'H' is Windows Up
                return "←"
            elif ch in ("6", "l"):
                return "→"

        return None

    @staticmethod
    def clear_screen() -> None:
        """Clears screen and moves cursor to home (1,1)."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def hide_cursor() -> None:
        """Hides the terminal cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show_cursor() -> None:
        """Restores the terminal cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    @staticmethod
    def move_cursor(row: int, col: int) -> None:
        """Moves cursor to 1-based (row, col)."""
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()

    @staticmethod
    def is_key_pressed() -> bool:
        """Non-blocking check if a keystroke is queued."""
        if sys.platform == "win32":
            return msvcrt.kbhit()
        else:
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            return bool(dr)

    @classmethod
    def get_char(cls, timeout: float | None = None) -> str | None:
        """
        Reads a single character from the console with optional timeout (in seconds).
        Returns None if timeout expires without input.
        Normalizes Enter (\r, \n) to '\n', Backspace (\x08, \x7f) to '\b',
        and Arrow Keys to KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT.
        """
        start = time.perf_counter()

        if sys.platform == "win32":
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    # Handle extended keys (arrow keys, function keys prefixes: \x00 or \xe0)
                    if ch in ("\x00", "\xe0"):
                        try:
                            # In Windows C runtime, getwch() directly reads the second scancode byte.
                            # Arrow keys emit: 'H' (Up), 'P' (Down), 'K' (Left), 'M' (Right).
                            ch2 = msvcrt.getwch()
                            if ch2 == "H":
                                return KEY_UP
                            elif ch2 == "P":
                                return KEY_DOWN
                            elif ch2 == "K":
                                return KEY_LEFT
                            elif ch2 == "M":
                                return KEY_RIGHT
                        except Exception:
                            pass
                        continue
                    # Handle ANSI escape sequences on Windows (e.g. Windows Terminal VT input)
                    if ch == "\x1b":
                        seq = ""
                        deadline = time.perf_counter() + 0.05
                        while time.perf_counter() < deadline and len(seq) < 2:
                            if msvcrt.kbhit():
                                seq += msvcrt.getwch()
                            else:
                                time.sleep(0.002)
                        if seq in ("[A", "OA"):
                            return KEY_UP
                        elif seq in ("[B", "OB"):
                            return KEY_DOWN
                        elif seq in ("[D", "OD"):
                            return KEY_LEFT
                        elif seq in ("[C", "OC"):
                            return KEY_RIGHT
                        if not seq:
                            return "\x1b"
                        continue
                    if ch in ("\r", "\n"):
                        return "\n"
                    if ch in ("\x08", "\x7f"):
                        return "\b"
                    if ch == "\x03":  # Ctrl+C
                        raise KeyboardInterrupt
                    return ch

                if timeout is not None:
                    if (time.perf_counter() - start) >= timeout:
                        return None
                time.sleep(0.005)

        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    remaining = None
                    if timeout is not None:
                        elapsed = time.perf_counter() - start
                        remaining = max(0.0, timeout - elapsed)
                        if remaining <= 0:
                            return None

                    rlist, _, _ = select.select([sys.stdin], [], [], remaining)
                    if rlist:
                        ch = sys.stdin.read(1)
                        if ch in ("\r", "\n"):
                            return "\n"
                        if ch in ("\x08", "\x7f"):
                            return "\b"
                        if ch == "\x03":  # Ctrl+C
                            raise KeyboardInterrupt
                        # Handle escape sequences (e.g. arrow keys)
                        if ch == "\x1b":
                            r, _, _ = select.select([sys.stdin], [], [], 0.05)
                            if r:
                                seq = sys.stdin.read(2)
                                if seq in ("[A", "OA"):
                                    return KEY_UP
                                elif seq in ("[B", "OB"):
                                    return KEY_DOWN
                                elif seq in ("[D", "OD"):
                                    return KEY_LEFT
                                elif seq in ("[C", "OC"):
                                    return KEY_RIGHT
                            continue
                        return ch
                    elif timeout is not None:
                        return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @classmethod
    def wait_for_enter(cls, prompt_msg: str = "PRESS [ENTER] TO CONTINUE...") -> None:
        """Waits until user presses Enter."""
        while True:
            ch = cls.get_char(timeout=0.1)
            if ch == "\n":
                return

    @classmethod
    def flush_input(cls) -> None:
        """Clears any queued unread keystrokes from the buffer."""
        if sys.platform == "win32":
            while msvcrt.kbhit():
                msvcrt.getwch()
        else:
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except Exception:
                pass
