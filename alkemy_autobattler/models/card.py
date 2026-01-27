"""
Card Model - Represents a single unit/card in the game.

The Card class is the core entity that players buy, sell, and battle with.
Cards are mutable during combat (health changes) but created from immutable
config data.

Design decisions:
- Cards are created from config data, ensuring consistency
- Each card gets a unique instance_id for tracking
- Combat stats (current_health) are separate from base stats
- Abilities are referenced by ID and resolved at runtime
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid

from ..config.tribes import TribeType
from ..config.abilities import ABILITIES, AbilityType, AbilityTrigger


@dataclass
class Card:
    """
    Represents a single unit/card in the game.

    Attributes:
        instance_id: Unique identifier for this specific card instance
        unit_id: Reference to the unit type in config
        name: Display name
        tribe: Which tribe this unit belongs to
        tier: Shop tier (1-6)
        base_attack: Original attack value
        base_health: Original health value
        current_attack: Current attack (may be buffed)
        current_health: Current health (changes in combat)
        cost: Gold cost to purchase
        sell_value: Gold gained when selling
        ability_id: Reference to ability in config
        is_token: Whether this was summoned (not purchased)
        has_divine_shield: Active divine shield status
        has_taunt: Whether this unit has taunt
    """

    # Identity
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    unit_id: str = ""
    name: str = ""

    # Classification
    tribe: TribeType = TribeType.NEUTRAL
    tier: int = 1

    # Base stats (original values)
    base_attack: int = 1
    base_health: int = 1

    # Current stats (modified during game)
    current_attack: int = 1
    current_health: int = 1

    # Economy
    cost: int = 3
    sell_value: int = 1

    # Ability
    ability_id: str = "none"

    # Flags
    is_token: bool = False
    has_divine_shield: bool = False
    has_taunt: bool = False

    # Combat state
    has_attacked: bool = False

    @classmethod
    def from_config(cls, unit_config: Dict[str, Any]) -> Card:
        """
        Factory method to create a Card from configuration data.
        This is the preferred way to create cards.
        """
        ability_id = unit_config.get("ability", "none")

        # Check for special ability flags
        has_divine_shield = False
        has_taunt = False

        if ability_id in ABILITIES:
            ability = ABILITIES[ability_id]
            if ability.get("type") == AbilityType.DIVINE_SHIELD:
                has_divine_shield = True
            if ability.get("type") == AbilityType.TAUNT:
                has_taunt = True

        return cls(
            unit_id=unit_config["id"],
            name=unit_config["name"],
            tribe=unit_config["tribe"],
            tier=unit_config["tier"],
            base_attack=unit_config["attack"],
            base_health=unit_config["health"],
            current_attack=unit_config["attack"],
            current_health=unit_config["health"],
            cost=unit_config["cost"],
            sell_value=unit_config.get("sell_value", 1),
            ability_id=ability_id,
            is_token=unit_config.get("is_token", False),
            has_divine_shield=has_divine_shield,
            has_taunt=has_taunt
        )

    def is_alive(self) -> bool:
        """Check if this card is still alive."""
        return self.current_health > 0

    def take_damage(self, amount: int) -> int:
        """
        Apply damage to this card.
        Returns actual damage dealt (after divine shield).
        """
        if amount <= 0:
            return 0

        if self.has_divine_shield:
            self.has_divine_shield = False
            return 0  # Shield absorbed all damage

        self.current_health -= amount
        return amount

    def heal(self, amount: int) -> int:
        """
        Heal this card (up to base health).
        Returns actual healing done.
        """
        if amount <= 0:
            return 0

        old_health = self.current_health
        self.current_health = min(self.current_health + amount, self.base_health)
        return self.current_health - old_health

    def buff(self, attack: int = 0, health: int = 0) -> None:
        """
        Apply a permanent buff to this card.
        Buffs increase both base and current stats.
        """
        self.base_attack += attack
        self.current_attack += attack
        self.base_health += health
        self.current_health += health

    def temporary_buff(self, attack: int = 0, health: int = 0) -> None:
        """
        Apply a temporary buff (current stats only).
        Used for combat-only effects.
        """
        self.current_attack += attack
        self.current_health += health

    def reset_for_combat(self) -> None:
        """Reset combat-related state at start of combat."""
        self.has_attacked = False
        # Note: Divine shield doesn't reset between combats

    def get_ability(self) -> Optional[Dict[str, Any]]:
        """Get this card's ability configuration."""
        if self.ability_id == "none":
            return None
        return ABILITIES.get(self.ability_id)

    def has_ability_trigger(self, trigger: AbilityTrigger) -> bool:
        """Check if this card has an ability with the given trigger."""
        ability = self.get_ability()
        if not ability:
            return False
        return ability.get("trigger") == trigger

    def clone(self) -> Card:
        """
        Create a copy of this card with new instance_id.
        Used for summoning tokens or copying effects.
        """
        new_card = Card(
            unit_id=self.unit_id,
            name=self.name,
            tribe=self.tribe,
            tier=self.tier,
            base_attack=self.base_attack,
            base_health=self.base_health,
            current_attack=self.current_attack,
            current_health=self.current_health,
            cost=self.cost,
            sell_value=self.sell_value,
            ability_id=self.ability_id,
            is_token=self.is_token,
            has_divine_shield=self.has_divine_shield,
            has_taunt=self.has_taunt
        )
        return new_card

    def get_stats_string(self) -> str:
        """Get a formatted string of current stats."""
        shield = "🛡️" if self.has_divine_shield else ""
        taunt = "⚔️" if self.has_taunt else ""
        return f"{self.current_attack}/{self.current_health}{shield}{taunt}"

    def __str__(self) -> str:
        """String representation for display."""
        tribe_name = self.tribe.name[:4] if self.tribe != TribeType.NEUTRAL else "NEUT"
        return f"[{self.name}] ({self.get_stats_string()}) [{tribe_name}]"

    def __repr__(self) -> str:
        return f"Card({self.name}, {self.current_attack}/{self.current_health}, {self.tribe.name})"
