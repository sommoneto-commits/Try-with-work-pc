"""
Shop Model - The tavern where players buy units.

The Shop provides:
- Random unit selection based on tavern tier
- Refresh/reroll functionality
- Unit pool management

Design decisions:
- Uses weighted random selection (higher tiers = rarer)
- Tier determines which units can appear
- Shop size increases with tier (like Battlegrounds)
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
import random

from .card import Card
from ..config.units import UNITS, get_shop_pool


class Shop:
    """
    The shop/tavern where players purchase units.

    Attributes:
        available_cards: Cards currently in the shop
        tier: Current tavern tier
        size: Number of cards to show in shop
    """

    # Shop sizes by tier
    SHOP_SIZES = {
        1: 3,
        2: 4,
        3: 4,
        4: 5,
        5: 5,
        6: 6,
    }

    # Weight multiplier for each tier (lower = rarer)
    TIER_WEIGHTS = {
        1: 100,
        2: 70,
        3: 50,
        4: 30,
        5: 15,
        6: 5,
    }

    def __init__(self, tier: int = 1):
        self.tier = tier
        self.available_cards: List[Card] = []
        self.frozen = False
        self.refresh(tier)

    def get_shop_size(self) -> int:
        """Get number of cards to show based on tier."""
        return self.SHOP_SIZES.get(self.tier, 3)

    def refresh(self, tier: int) -> None:
        """
        Refresh the shop with new random cards.

        Args:
            tier: Player's current tavern tier
        """
        if self.frozen:
            return

        self.tier = tier
        self.available_cards = []

        # Get available unit pool
        pool = get_shop_pool(tier)
        if not pool:
            return

        # Calculate weights for each unit in pool
        weighted_pool = self._build_weighted_pool(pool)

        # Select random cards
        shop_size = self.get_shop_size()
        for _ in range(shop_size):
            if weighted_pool:
                unit_id = self._weighted_random_choice(weighted_pool)
                unit_config = UNITS[unit_id]
                card = Card.from_config(unit_config)
                self.available_cards.append(card)

    def _build_weighted_pool(self, pool: List[str]) -> Dict[str, int]:
        """
        Build a weighted pool of unit IDs.
        Higher tier units are rarer.
        """
        weighted = {}
        for unit_id in pool:
            unit = UNITS[unit_id]
            unit_tier = unit["tier"]
            weight = self.TIER_WEIGHTS.get(unit_tier, 1)
            weighted[unit_id] = weight
        return weighted

    def _weighted_random_choice(self, weighted_pool: Dict[str, int]) -> str:
        """Choose a random unit ID based on weights."""
        total = sum(weighted_pool.values())
        r = random.random() * total
        cumulative = 0
        for unit_id, weight in weighted_pool.items():
            cumulative += weight
            if r <= cumulative:
                return unit_id
        # Fallback (shouldn't happen)
        return list(weighted_pool.keys())[0]

    def add_card(self, card: Card) -> None:
        """Add a card back to the shop (e.g., failed purchase)."""
        self.available_cards.append(card)

    def remove_card(self, card: Card) -> bool:
        """
        Remove a card from the shop (when bought).

        Returns:
            True if removed, False if not found
        """
        if card in self.available_cards:
            self.available_cards.remove(card)
            return True
        return False

    def get_card(self, index: int) -> Optional[Card]:
        """Get card by index in shop."""
        if 0 <= index < len(self.available_cards):
            return self.available_cards[index]
        return None

    def toggle_freeze(self) -> bool:
        """
        Toggle shop freeze status.
        When frozen, shop won't refresh next turn.

        Returns:
            New freeze state
        """
        self.frozen = not self.frozen
        return self.frozen

    def unfreeze(self) -> None:
        """Unfreeze the shop."""
        self.frozen = False

    def is_empty(self) -> bool:
        """Check if shop has no cards."""
        return len(self.available_cards) == 0

    def __str__(self) -> str:
        """String representation of shop."""
        if not self.available_cards:
            return "[Shop Empty]"

        lines = [f"=== SHOP (Tier {self.tier}) ==="]
        for i, card in enumerate(self.available_cards, 1):
            tribe_info = card.tribe.name[:4]
            ability_info = ""
            if card.ability_id != "none":
                ability = card.get_ability()
                if ability:
                    ability_info = f" [{ability.get('name', '')}]"
            lines.append(
                f"  {i}. {card.name} ({card.current_attack}/{card.current_health}) "
                f"[{tribe_info}] - {card.cost}G{ability_info}"
            )

        if self.frozen:
            lines.append("  [FROZEN]")

        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Shop(tier={self.tier}, cards={len(self.available_cards)})"
