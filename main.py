#!/usr/bin/env python3
"""
Terminal Typer: Battle Protocol
Direct launcher script.
"""

import sys

for stream in (sys.stdout, sys.stderr, sys.stdin):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from terminaltyper.__main__ import main

if __name__ == "__main__":
    main()
