#!/usr/bin/env python3
"""
Package entry point for running as module.

Usage:
    python -m alkemy_autobattler
"""

from .game.game_loop import main

if __name__ == "__main__":
    main()
