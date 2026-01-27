"""
Unit Configuration - Data-driven unit/card definitions.

This is the main content file for the game. All units are defined here.
To add a new unit, simply add an entry to the UNITS dict.

Unit Structure:
- id: Unique identifier (string)
- name: Display name
- tribe: TribeType enum value
- tier: Shop tier (1-6), determines when unit appears
- attack: Base attack value
- health: Base health value
- cost: Gold cost to buy
- sell_value: Gold gained when selling (usually 1)
- ability: Ability ID from abilities.py (or "none")
- is_token: If True, not available in shop (summoned only)

Tier Guidelines (following Battlegrounds pattern):
- Tier 1: Basic units, simple stats (1-3 cost)
- Tier 2: Slightly stronger, some abilities (3 cost)
- Tier 3: Medium power, more abilities (3 cost)
- Tier 4: Strong units, synergy enablers (4 cost)
- Tier 5: Powerful units, strong abilities (5 cost)
- Tier 6: Legendary, game-changing effects (6 cost)
"""

from typing import Dict, Any
from .tribes import TribeType


# ============================================================================
# UNIT DEFINITIONS - Add new units here!
# ============================================================================

UNITS: Dict[str, Dict[str, Any]] = {

    # ========================================================================
    # TIER 1 UNITS - Basic starter units
    # ========================================================================

    # --- Management ---
    "account_owner": {
        "id": "account_owner",
        "name": "Account Owner",
        "tribe": TribeType.MANAGEMENT,
        "tier": 1,
        "attack": 2,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Staff ---
    "office_assistant": {
        "id": "office_assistant",
        "name": "Office Assistant",
        "tribe": TribeType.STAFF,
        "tier": 1,
        "attack": 1,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "death_buff_ally",  # Deathrattle: buff an ally
        "is_token": False
    },

    # --- Consulting ---
    "junior_consultant": {
        "id": "junior_consultant",
        "name": "Junior Consultant",
        "tribe": TribeType.CONSULTING,
        "tier": 1,
        "attack": 3,
        "health": 1,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Data & Analytics ---
    "data_intern": {
        "id": "data_intern",
        "name": "Data Intern",
        "tribe": TribeType.DATA_ANALYTICS,
        "tier": 1,
        "attack": 1,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "on_attack_buff",  # Gains attack when attacking
        "is_token": False
    },

    # --- Marketing & Media ---
    "social_media_intern": {
        "id": "social_media_intern",
        "name": "Social Media Intern",
        "tribe": TribeType.MARKETING_MEDIA,
        "tier": 1,
        "attack": 2,
        "health": 1,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Brand Experience ---
    "junior_designer": {
        "id": "junior_designer",
        "name": "Junior Designer",
        "tribe": TribeType.BRAND_EXPERIENCE,
        "tier": 1,
        "attack": 1,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "sell_gold_bonus",  # Extra gold when sold
        "is_token": False
    },

    # --- Tech ---
    "junior_developer": {
        "id": "junior_developer",
        "name": "Junior Developer",
        "tribe": TribeType.TECH,
        "tier": 1,
        "attack": 2,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Neutral ---
    "freelancer": {
        "id": "freelancer",
        "name": "Freelancer",
        "tribe": TribeType.NEUTRAL,
        "tier": 1,
        "attack": 2,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # ========================================================================
    # TIER 2 UNITS - Slightly stronger with some abilities
    # ========================================================================

    # --- Management ---
    "anna_cappa": {
        "id": "anna_cappa",
        "name": "Anna Cappa",
        "tribe": TribeType.MANAGEMENT,
        "tier": 2,
        "attack": 1,
        "health": 5,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Staff ---
    "hr_specialist": {
        "id": "hr_specialist",
        "name": "HR Specialist",
        "tribe": TribeType.STAFF,
        "tier": 2,
        "attack": 1,
        "health": 4,
        "cost": 3,
        "sell_value": 1,
        "ability": "death_summon",  # Summons token on death
        "is_token": False
    },

    # --- Consulting ---
    "business_analyst": {
        "id": "business_analyst",
        "name": "Business Analyst",
        "tribe": TribeType.CONSULTING,
        "tier": 2,
        "attack": 3,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "on_kill_buff",  # Gets stronger on kills
        "is_token": False
    },

    # --- Data & Analytics ---
    "data_analyst": {
        "id": "data_analyst",
        "name": "Data Analyst",
        "tribe": TribeType.DATA_ANALYTICS,
        "tier": 2,
        "attack": 2,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Marketing & Media ---
    "content_creator": {
        "id": "content_creator",
        "name": "Content Creator",
        "tribe": TribeType.MARKETING_MEDIA,
        "tier": 2,
        "attack": 2,
        "health": 2,
        "cost": 3,
        "sell_value": 1,
        "ability": "aura_adjacent_buff",  # Buffs adjacent units
        "is_token": False
    },

    # --- Brand Experience ---
    "event_coordinator": {
        "id": "event_coordinator",
        "name": "Event Coordinator",
        "tribe": TribeType.BRAND_EXPERIENCE,
        "tier": 2,
        "attack": 2,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Tech ---
    "backend_developer": {
        "id": "backend_developer",
        "name": "Backend Developer",
        "tribe": TribeType.TECH,
        "tier": 2,
        "attack": 3,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # ========================================================================
    # TIER 3 UNITS - Medium power with more abilities
    # ========================================================================

    # --- Management ---
    "industry_leader": {
        "id": "industry_leader",
        "name": "Industry Leader",
        "tribe": TribeType.MANAGEMENT,
        "tier": 3,
        "attack": 4,
        "health": 5,
        "cost": 4,
        "sell_value": 1,
        "ability": "none",
        "is_token": False
    },

    # --- Staff ---
    "office_manager": {
        "id": "office_manager",
        "name": "Office Manager",
        "tribe": TribeType.STAFF,
        "tier": 3,
        "attack": 2,
        "health": 5,
        "cost": 3,
        "sell_value": 1,
        "ability": "death_buff_ally",
        "is_token": False
    },

    # --- Consulting ---
    "senior_consultant": {
        "id": "senior_consultant",
        "name": "Senior Consultant",
        "tribe": TribeType.CONSULTING,
        "tier": 3,
        "attack": 4,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "on_attack_buff",
        "is_token": False
    },

    # --- Data & Analytics ---
    "data_scientist": {
        "id": "data_scientist",
        "name": "Data Scientist",
        "tribe": TribeType.DATA_ANALYTICS,
        "tier": 3,
        "attack": 3,
        "health": 4,
        "cost": 3,
        "sell_value": 1,
        "ability": "start_combat_buff_all",
        "is_token": False
    },

    # --- Marketing & Media ---
    "marketing_manager": {
        "id": "marketing_manager",
        "name": "Marketing Manager",
        "tribe": TribeType.MARKETING_MEDIA,
        "tier": 3,
        "attack": 3,
        "health": 3,
        "cost": 3,
        "sell_value": 1,
        "ability": "aura_adjacent_buff",
        "is_token": False
    },

    # --- Brand Experience ---
    "creative_director": {
        "id": "creative_director",
        "name": "Creative Director",
        "tribe": TribeType.BRAND_EXPERIENCE,
        "tier": 3,
        "attack": 3,
        "health": 4,
        "cost": 3,
        "sell_value": 1,
        "ability": "divine_shield",  # Immune to first damage
        "is_token": False
    },

    # --- Tech ---
    "senior_developer": {
        "id": "senior_developer",
        "name": "Senior Developer",
        "tribe": TribeType.TECH,
        "tier": 3,
        "attack": 4,
        "health": 4,
        "cost": 3,
        "sell_value": 1,
        "ability": "start_combat_buff_tribe",  # Buffs Tech allies
        "is_token": False
    },

    # ========================================================================
    # TIER 4 UNITS - Strong units, synergy enablers
    # ========================================================================

    # --- Management ---
    "oscar_zoggia": {
        "id": "oscar_zoggia",
        "name": "Oscar Zoggia",
        "tribe": TribeType.MANAGEMENT,
        "tier": 4,
        "attack": 5,
        "health": 6,
        "cost": 5,
        "sell_value": 2,
        "ability": "none",
        "is_token": False
    },

    "silvia_bosani": {
        "id": "silvia_bosani",
        "name": "Silvia Bosani",
        "tribe": TribeType.MANAGEMENT,
        "tier": 4,
        "attack": 3,
        "health": 7,
        "cost": 5,
        "sell_value": 2,
        "ability": "none",
        "is_token": False
    },

    # --- Tech ---
    "tech_lead": {
        "id": "tech_lead",
        "name": "Tech Lead",
        "tribe": TribeType.TECH,
        "tier": 4,
        "attack": 5,
        "health": 4,
        "cost": 4,
        "sell_value": 2,
        "ability": "on_kill_buff",
        "is_token": False
    },

    # --- Consulting ---
    "strategy_director": {
        "id": "strategy_director",
        "name": "Strategy Director",
        "tribe": TribeType.CONSULTING,
        "tier": 4,
        "attack": 5,
        "health": 5,
        "cost": 4,
        "sell_value": 2,
        "ability": "taunt",
        "is_token": False
    },

    # ========================================================================
    # TIER 5 UNITS - Powerful late game
    # ========================================================================

    # --- Tech ---
    "cto": {
        "id": "cto",
        "name": "CTO",
        "tribe": TribeType.TECH,
        "tier": 5,
        "attack": 6,
        "health": 5,
        "cost": 5,
        "sell_value": 2,
        "ability": "start_combat_buff_tribe",
        "is_token": False
    },

    # ========================================================================
    # TIER 6 UNITS - Legendary game-changers
    # ========================================================================

    # --- Management ---
    "duccio_vitali": {
        "id": "duccio_vitali",
        "name": "Duccio Vitali",
        "tribe": TribeType.MANAGEMENT,
        "tier": 6,
        "attack": 6,
        "health": 10,
        "cost": 6,
        "sell_value": 3,
        "ability": "none",
        "is_token": False
    },

    # ========================================================================
    # TOKEN UNITS - Not in shop, summoned by abilities
    # ========================================================================

    "intern_token": {
        "id": "intern_token",
        "name": "Intern",
        "tribe": TribeType.NEUTRAL,
        "tier": 1,
        "attack": 1,
        "health": 1,
        "cost": 0,
        "sell_value": 0,
        "ability": "none",
        "is_token": True
    },
}


def get_unit(unit_id: str) -> Dict[str, Any]:
    """
    Get unit configuration by ID.
    Raises KeyError if unit doesn't exist.
    """
    return UNITS[unit_id].copy()


def get_units_by_tier(tier: int) -> Dict[str, Dict[str, Any]]:
    """Get all units available at a specific tier (non-token units)."""
    return {
        k: v for k, v in UNITS.items()
        if v["tier"] <= tier and not v.get("is_token", False)
    }


def get_units_by_tribe(tribe: TribeType) -> Dict[str, Dict[str, Any]]:
    """Get all units of a specific tribe."""
    return {
        k: v for k, v in UNITS.items()
        if v["tribe"] == tribe
    }


def get_shop_pool(tier: int) -> list:
    """
    Get list of unit IDs available for shop at given tier.
    Returns list that can be used for random selection.
    """
    return [
        unit_id for unit_id, unit in UNITS.items()
        if unit["tier"] <= tier and not unit.get("is_token", False)
    ]
