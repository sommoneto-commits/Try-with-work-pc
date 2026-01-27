"""
Systems module - Game logic and mechanics.

This module contains the core game systems:
- CombatResolver: Handles automatic combat between boards
- AI: Decision making for AI players (now in models/player.py)

Systems are designed to be stateless where possible,
operating on game models without storing state themselves.
"""

from .combat import CombatResolver, CombatResult, CombatLog

__all__ = [
    'CombatResolver',
    'CombatResult',
    'CombatLog'
]
