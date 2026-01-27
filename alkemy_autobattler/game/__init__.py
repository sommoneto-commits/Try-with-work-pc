"""
Game module - Main game loop and flow control.

This module orchestrates the entire game:
- Game initialization
- Round progression
- Phase transitions (shop -> combat)
- Win/lose conditions
"""

from .game_loop import Game, GamePhase

__all__ = ['Game', 'GamePhase']
