#!/usr/bin/env python3
"""
Alkemy Autobattler - Main Entry Point
======================================

A single-player auto-battler card game inspired by Hearthstone Battlegrounds,
set in the Alkemy company universe.

Run this file to start the game:
    python -m alkemy_autobattler.main

Or from the project root:
    python alkemy_autobattler/main.py

Architecture Overview:
---------------------
The game is built with a modular, data-driven architecture:

1. config/
   - tribes.py: Tribe definitions and synergies
   - units.py: All unit cards with stats and abilities
   - abilities.py: Ability system with triggers and effects

2. models/
   - card.py: Card/Unit class
   - player.py: Player and AIPlayer classes
   - board.py: Battlefield management
   - shop.py: Tavern/shop system

3. systems/
   - combat.py: Automatic combat resolution

4. game/
   - game_loop.py: Main game orchestration

Extensibility:
--------------
To add new content:

1. New Units:
   Add entries to config/units.py following the existing format.
   The unit will automatically appear in the shop.

2. New Tribes:
   Add to TribeType enum and TRIBES dict in config/tribes.py.
   Define synergy bonuses as needed.

3. New Abilities:
   Add to ABILITIES dict in config/abilities.py.
   For new ability types, implement handlers in systems/combat.py.

4. Boss Encounters (Future):
   Create a Boss class extending AIPlayer.
   Add boss-specific abilities and mechanics.

5. Advanced Mechanics (Future):
   - Golden units (triple merging)
   - Hero powers
   - Tavern upgrades
   - Secret abilities
"""

from game.game_loop import main

if __name__ == "__main__":
    main()
