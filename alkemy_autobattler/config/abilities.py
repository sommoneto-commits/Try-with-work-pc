"""
Ability Configuration - Data-driven ability system.

Abilities are special effects that units can have.
The system is designed to be extensible:
- AbilityTrigger: WHEN the ability activates
- AbilityType: WHAT the ability does

To add a new ability:
1. Define the trigger and type combination
2. Add to ABILITIES dict with parameters
3. Implement handler in systems/combat.py if new type

Current implementation includes simple abilities.
Future additions: Divine Shield, Taunt, Cleave, etc.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional


class AbilityTrigger(Enum):
    """
    When an ability triggers during gameplay.
    Extensible enum - add new triggers as needed.
    """
    # Combat triggers
    ON_ATTACK = auto()           # When this unit attacks
    ON_ATTACKED = auto()         # When this unit is attacked
    ON_DEAL_DAMAGE = auto()      # When this unit deals damage
    ON_TAKE_DAMAGE = auto()      # When this unit takes damage
    ON_DEATH = auto()            # Deathrattle - when this unit dies
    ON_KILL = auto()             # When this unit kills an enemy

    # Phase triggers
    START_OF_COMBAT = auto()     # At combat start
    END_OF_COMBAT = auto()       # At combat end
    START_OF_TURN = auto()       # At turn start (shop phase)
    END_OF_TURN = auto()         # At turn end

    # Board triggers
    ON_SUMMON = auto()           # When this unit is summoned/bought
    ON_SELL = auto()             # When this unit is sold
    ON_ALLY_SUMMON = auto()      # When another ally is summoned
    ON_ALLY_DEATH = auto()       # When another ally dies

    # Passive (always active)
    AURA = auto()                # Continuous effect while on board
    PASSIVE = auto()             # Permanent effect


class AbilityType(Enum):
    """
    What an ability does when triggered.
    Each type has specific parameters defined in ABILITIES.
    """
    # Stat modifications
    BUFF_SELF = auto()           # Increase own stats
    BUFF_TARGET = auto()         # Increase target's stats
    BUFF_ADJACENT = auto()       # Buff units next to this one
    BUFF_ALL_ALLIES = auto()     # Buff all friendly units
    BUFF_TRIBE = auto()          # Buff all units of a specific tribe

    # Damage effects
    DEAL_DAMAGE = auto()         # Deal direct damage
    DEAL_DAMAGE_ALL = auto()     # Deal damage to all enemies

    # Summoning
    SUMMON_UNIT = auto()         # Create a new unit

    # Resource effects
    GAIN_GOLD = auto()           # Gain gold

    # Special
    DIVINE_SHIELD = auto()       # Negate first damage instance
    TAUNT = auto()               # Must be attacked first
    CLEAVE = auto()              # Attack hits adjacent units too


# Ability definitions - data-driven configuration
# Each ability has:
# - id: Unique identifier
# - name: Display name
# - description: What it does
# - trigger: When it activates
# - type: What effect it has
# - params: Effect-specific parameters

ABILITIES: Dict[str, Dict[str, Any]] = {
    # === Deathrattle abilities ===
    "death_buff_ally": {
        "id": "death_buff_ally",
        "name": "Last Words",
        "description": "Deathrattle: Give a random ally +1/+1",
        "trigger": AbilityTrigger.ON_DEATH,
        "type": AbilityType.BUFF_TARGET,
        "params": {
            "target": "random_ally",
            "attack": 1,
            "health": 1
        }
    },
    "death_deal_damage": {
        "id": "death_deal_damage",
        "name": "Explosive Exit",
        "description": "Deathrattle: Deal 2 damage to a random enemy",
        "trigger": AbilityTrigger.ON_DEATH,
        "type": AbilityType.DEAL_DAMAGE,
        "params": {
            "target": "random_enemy",
            "damage": 2
        }
    },
    "death_summon": {
        "id": "death_summon",
        "name": "Knowledge Transfer",
        "description": "Deathrattle: Summon a 1/1 Intern",
        "trigger": AbilityTrigger.ON_DEATH,
        "type": AbilityType.SUMMON_UNIT,
        "params": {
            "unit_id": "intern_token",
            "count": 1
        }
    },

    # === Combat abilities ===
    "on_attack_buff": {
        "id": "on_attack_buff",
        "name": "Aggressive Strategy",
        "description": "When this attacks, gain +1 Attack",
        "trigger": AbilityTrigger.ON_ATTACK,
        "type": AbilityType.BUFF_SELF,
        "params": {
            "attack": 1,
            "health": 0
        }
    },
    "on_kill_buff": {
        "id": "on_kill_buff",
        "name": "Performance Bonus",
        "description": "When this kills an enemy, gain +2/+1",
        "trigger": AbilityTrigger.ON_KILL,
        "type": AbilityType.BUFF_SELF,
        "params": {
            "attack": 2,
            "health": 1
        }
    },

    # === Start of combat abilities ===
    "start_combat_buff_all": {
        "id": "start_combat_buff_all",
        "name": "Team Rally",
        "description": "Start of Combat: Give all allies +1 Attack",
        "trigger": AbilityTrigger.START_OF_COMBAT,
        "type": AbilityType.BUFF_ALL_ALLIES,
        "params": {
            "attack": 1,
            "health": 0
        }
    },
    "start_combat_buff_tribe": {
        "id": "start_combat_buff_tribe",
        "name": "Department Synergy",
        "description": "Start of Combat: Give all Tech allies +1/+1",
        "trigger": AbilityTrigger.START_OF_COMBAT,
        "type": AbilityType.BUFF_TRIBE,
        "params": {
            "tribe": "TECH",
            "attack": 1,
            "health": 1
        }
    },

    # === Aura abilities ===
    "aura_adjacent_buff": {
        "id": "aura_adjacent_buff",
        "name": "Inspiring Presence",
        "description": "Adjacent units have +1 Attack",
        "trigger": AbilityTrigger.AURA,
        "type": AbilityType.BUFF_ADJACENT,
        "params": {
            "attack": 1,
            "health": 0
        }
    },

    # === Special abilities ===
    "divine_shield": {
        "id": "divine_shield",
        "name": "Corporate Shield",
        "description": "Divine Shield: Immune to the first damage taken",
        "trigger": AbilityTrigger.PASSIVE,
        "type": AbilityType.DIVINE_SHIELD,
        "params": {}
    },
    "taunt": {
        "id": "taunt",
        "name": "Front Line",
        "description": "Taunt: Enemies must attack this unit first",
        "trigger": AbilityTrigger.PASSIVE,
        "type": AbilityType.TAUNT,
        "params": {}
    },

    # === Sell abilities ===
    "sell_gold_bonus": {
        "id": "sell_gold_bonus",
        "name": "Liquidation",
        "description": "When sold, gain +1 Gold",
        "trigger": AbilityTrigger.ON_SELL,
        "type": AbilityType.GAIN_GOLD,
        "params": {
            "amount": 1
        }
    },

    # Placeholder for no ability
    "none": {
        "id": "none",
        "name": "None",
        "description": "",
        "trigger": None,
        "type": None,
        "params": {}
    }
}


def get_ability(ability_id: str) -> Optional[Dict[str, Any]]:
    """
    Get ability configuration by ID.
    Returns None if ability doesn't exist.
    """
    return ABILITIES.get(ability_id)


def get_abilities_by_trigger(trigger: AbilityTrigger) -> Dict[str, Dict[str, Any]]:
    """Get all abilities with a specific trigger."""
    return {
        k: v for k, v in ABILITIES.items()
        if v.get("trigger") == trigger
    }
