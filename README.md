# Alkemy Autobattler

A single-player auto-battler card game inspired by Hearthstone Battlegrounds, set in the Alkemy company universe.

## Quick Start

```bash
cd Try-with-work-pc
python -m alkemy_autobattler
```

## Game Overview

### Objective
Defeat the AI opponent by building a strong team of corporate warriors. Reduce the AI's health to 0 before it does the same to you.

### Game Flow
1. **Shop Phase**: Buy units, sell units, upgrade your tavern tier
2. **Combat Phase**: Your units automatically fight the AI's units
3. **Damage**: The winner deals damage to the loser (tier + surviving units' tiers)
4. **Repeat** until someone reaches 0 health

### Commands (Shop Phase)
| Command | Description |
|---------|-------------|
| `buy <N>` | Buy card N from shop |
| `sell b<N>` | Sell card N from board |
| `sell h<N>` | Sell card N from hand |
| `play <N>` | Play card N from hand to board |
| `reroll` | Refresh shop (costs 1G) |
| `tierup` | Upgrade tavern tier |
| `freeze` | Freeze/unfreeze shop |
| `end` | End shop phase, start combat |
| `help` | Show commands |

## Tribes

| Tribe | Theme | Synergy |
|-------|-------|---------|
| **Management** | Leaders | Team buffs |
| **Staff** | Support | Deathrattles |
| **Consulting** | Damage dealers | Attack bonuses |
| **Data & Analytics** | Scalers | Self buffs |
| **Marketing & Media** | Adjacency | Adjacent unit buffs |
| **Brand Experience** | Creative | Combat start effects |
| **Tech** | Engineers | Per-round scaling |

## Project Architecture

```
alkemy_autobattler/
├── __init__.py          # Package init
├── __main__.py          # Entry point (python -m)
├── main.py              # Alternative entry point
├── config/              # Data-driven configuration
│   ├── tribes.py        # Tribe definitions
│   ├── units.py         # Unit/card definitions
│   └── abilities.py     # Ability system
├── models/              # Core game entities
│   ├── card.py          # Card/Unit class
│   ├── player.py        # Player & AI classes
│   ├── board.py         # Battlefield
│   └── shop.py          # Tavern/shop
├── systems/             # Game systems
│   └── combat.py        # Combat resolution
└── game/                # Game orchestration
    └── game_loop.py     # Main game loop
```

## Extensibility Guide

### Adding New Units

Edit `config/units.py`:

```python
"new_unit_id": {
    "id": "new_unit_id",
    "name": "New Unit Name",
    "tribe": TribeType.TECH,
    "tier": 2,
    "attack": 3,
    "health": 3,
    "cost": 3,
    "sell_value": 1,
    "ability": "none",  # or ability ID
    "is_token": False
}
```

### Adding New Abilities

Edit `config/abilities.py`:

```python
"new_ability": {
    "id": "new_ability",
    "name": "Ability Name",
    "description": "What it does",
    "trigger": AbilityTrigger.ON_DEATH,
    "type": AbilityType.BUFF_SELF,
    "params": {"attack": 2, "health": 1}
}
```

Then implement the handler in `systems/combat.py` if using a new `AbilityType`.

### Adding Boss Encounters (Future)

1. Create a `Boss` class extending `AIPlayer`
2. Add boss-specific abilities
3. Implement boss selection in game loop

### Adding New Tribes

1. Add to `TribeType` enum in `config/tribes.py`
2. Add tribe config to `TRIBES` dict
3. Create units for the new tribe

## Design Principles

1. **Data-Driven**: All content (units, abilities, tribes) is defined in config files
2. **Modular**: Systems are independent and can be extended
3. **Simple AI**: AI is functional but not optimal (good for single-player)
4. **Console-First**: Text-based UI, easy to understand and modify

## Future Enhancements

- [ ] Golden units (triple merging)
- [ ] Hero powers
- [ ] Boss encounters
- [ ] More abilities (Cleave, Windfury, etc.)
- [ ] Difficulty progression
- [ ] Save/load game state
- [ ] Web/GUI interface

## Requirements

- Python 3.8+
- No external dependencies (standard library only)

## License

Internal Alkemy project
