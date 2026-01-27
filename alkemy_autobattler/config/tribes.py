"""
Tribe Configuration - Data-driven tribe definitions.

Each tribe represents a department/area within Alkemy.
Tribes can have synergy bonuses that activate when multiple units
of the same tribe are on the board.

To add a new tribe:
1. Add a new TribeType enum value
2. Add corresponding entry in TRIBES dict with:
   - name: Display name
   - description: Flavor text
   - synergy_bonus: Dict describing bonuses at different unit counts
"""

from enum import Enum, auto
from typing import Dict, Any


class TribeType(Enum):
    """
    Enumeration of all available tribes.
    Using Enum ensures type safety and prevents typos in tribe references.
    """
    MANAGEMENT = auto()
    STAFF = auto()
    CONSULTING = auto()
    DATA_ANALYTICS = auto()
    MARKETING_MEDIA = auto()
    BRAND_EXPERIENCE = auto()
    TECH = auto()
    NEUTRAL = auto()  # For units that don't belong to any specific tribe


# Data-driven tribe configuration
# Each tribe has metadata and potential synergy bonuses
TRIBES: Dict[TribeType, Dict[str, Any]] = {
    TribeType.MANAGEMENT: {
        "name": "Management",
        "description": "Leaders and decision makers. Boost overall team performance.",
        "color": "🟣",  # For console display
        "synergy_bonus": {
            # Number of units -> bonus effect
            2: {"type": "buff_all", "attack": 1, "health": 0},
            4: {"type": "buff_all", "attack": 2, "health": 1},
        }
    },
    TribeType.STAFF: {
        "name": "Staff",
        "description": "Support personnel. Strengthen allies on death.",
        "color": "🟢",
        "synergy_bonus": {
            2: {"type": "buff_random", "attack": 0, "health": 2},
            4: {"type": "buff_all", "attack": 1, "health": 2},
        }
    },
    TribeType.CONSULTING: {
        "name": "Consulting",
        "description": "Strategic advisors. Deal extra damage on attack.",
        "color": "🔵",
        "synergy_bonus": {
            2: {"type": "buff_attack", "attack": 1},
            4: {"type": "buff_attack", "attack": 3},
        }
    },
    TribeType.DATA_ANALYTICS: {
        "name": "Data & Analytics",
        "description": "Number crunchers. Gain stats based on board state.",
        "color": "🟡",
        "synergy_bonus": {
            2: {"type": "buff_self", "attack": 1, "health": 1},
            4: {"type": "buff_self", "attack": 2, "health": 2},
        }
    },
    TribeType.MARKETING_MEDIA: {
        "name": "Marketing & Media",
        "description": "Communicators. Buff adjacent units.",
        "color": "🟠",
        "synergy_bonus": {
            2: {"type": "buff_adjacent", "attack": 1, "health": 0},
            4: {"type": "buff_adjacent", "attack": 2, "health": 1},
        }
    },
    TribeType.BRAND_EXPERIENCE: {
        "name": "Brand Experience",
        "description": "Creative minds. Generate value on combat start.",
        "color": "🔴",
        "synergy_bonus": {
            2: {"type": "start_combat_buff", "attack": 1},
            4: {"type": "start_combat_buff", "attack": 2, "health": 1},
        }
    },
    TribeType.TECH: {
        "name": "Tech",
        "description": "Engineers and developers. Scale with game duration.",
        "color": "⚪",
        "synergy_bonus": {
            2: {"type": "per_round_buff", "attack": 0, "health": 1},
            4: {"type": "per_round_buff", "attack": 1, "health": 1},
        }
    },
    TribeType.NEUTRAL: {
        "name": "Neutral",
        "description": "Versatile units that work with any team.",
        "color": "⬜",
        "synergy_bonus": {}  # No synergy bonus
    }
}


def get_tribe_name(tribe_type: TribeType) -> str:
    """Get display name for a tribe."""
    return TRIBES[tribe_type]["name"]


def get_tribe_synergy(tribe_type: TribeType, count: int) -> Dict[str, Any]:
    """
    Get synergy bonus for a tribe at a given unit count.
    Returns empty dict if no bonus at that count.
    """
    synergies = TRIBES[tribe_type].get("synergy_bonus", {})
    # Find the highest applicable synergy level
    applicable_bonus = {}
    for threshold, bonus in sorted(synergies.items()):
        if count >= threshold:
            applicable_bonus = bonus
    return applicable_bonus
