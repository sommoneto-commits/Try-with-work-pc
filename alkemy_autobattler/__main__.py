#!/usr/bin/env python3
"""
Package entry point for running as module.

Usage:
    python -m alkemy_autobattler           # Web GUI (default)
    python -m alkemy_autobattler --console # Console text mode
"""

import sys


def main():
    if "--console" in sys.argv:
        from .game.game_loop import main as console_main
        console_main()
    else:
        from .game.web_gui import main as web_main
        web_main()


if __name__ == "__main__":
    main()
