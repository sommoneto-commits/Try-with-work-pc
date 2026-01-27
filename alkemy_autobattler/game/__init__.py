"""
Game module - Main game loop and flow control.

This module orchestrates the entire game:
- Game initialization
- Round progression
- Phase transitions (shop -> combat)
- Win/lose conditions

Two interfaces available:
- Console: Text-based (game_loop.py)
- Web GUI: Browser-based (web_gui.py)
"""

from .game_loop import Game, GamePhase

__all__ = ['Game', 'GamePhase']
