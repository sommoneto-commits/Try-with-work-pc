"""
Configuration module - Data-driven definitions for game content.

This module contains all configurable game data:
- Tribes: The 7 factions in the game
- Units: All playable cards with their stats
- Abilities: Special effects that units can have

To add new content:
1. Add tribe definitions to tribes.py
2. Add unit definitions to units.py
3. Add ability definitions to abilities.py

The game automatically loads and validates this configuration at startup.
"""

from .tribes import TRIBES, TribeType
from .units import UNITS
from .abilities import ABILITIES, AbilityTrigger, AbilityType

__all__ = [
    'TRIBES',
    'TribeType',
    'UNITS',
    'ABILITIES',
    'AbilityTrigger',
    'AbilityType'
]
