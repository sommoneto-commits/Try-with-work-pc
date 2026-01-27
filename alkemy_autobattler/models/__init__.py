"""
Models module - Core game entities.

This module contains the fundamental classes that make up the game:
- Card: Individual unit on the board
- Player: Human or AI player
- Board: Player's battlefield
- Shop: The tavern where units are purchased

These classes are designed to be:
1. Immutable where possible (stats are mutable during combat)
2. Decoupled from game logic (systems handle logic)
3. Easy to serialize/deserialize for future save/load
"""

from .card import Card
from .player import Player, AIPlayer
from .board import Board
from .shop import Shop

__all__ = [
    'Card',
    'Player',
    'AIPlayer',
    'Board',
    'Shop'
]
