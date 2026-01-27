"""
Board Model - Represents a player's battlefield.

The Board manages the units a player has in combat.
It handles:
- Unit positioning (important for adjacency effects)
- Tribe counting for synergies
- Combat-related queries (next attacker, valid targets)

Design decisions:
- Fixed maximum size (7 units, like Battlegrounds)
- Position-aware for future adjacency mechanics
- Provides helper methods for combat resolution
"""

from __future__ import annotations
from typing import List, Optional, Dict
import random

from .card import Card
from ..config.tribes import TribeType


class Board:
    """
    Represents a player's battlefield.

    Attributes:
        max_size: Maximum number of units allowed
        units: List of cards on the board (position matters)
    """

    MAX_BOARD_SIZE = 7  # Standard auto-battler board size

    def __init__(self, max_size: int = MAX_BOARD_SIZE):
        self.max_size = max_size
        self.units: List[Card] = []
        self._next_attacker_index = 0

    def add_unit(self, card: Card, position: Optional[int] = None) -> bool:
        """
        Add a unit to the board.

        Args:
            card: The card to add
            position: Optional position (None = end of list)

        Returns:
            True if added successfully, False if board is full
        """
        if self.is_full():
            return False

        if position is not None and 0 <= position <= len(self.units):
            self.units.insert(position, card)
        else:
            self.units.append(card)
        return True

    def remove_unit(self, card: Card) -> bool:
        """
        Remove a specific unit from the board.

        Returns:
            True if removed, False if not found
        """
        if card in self.units:
            index = self.units.index(card)
            self.units.remove(card)
            # Adjust attacker index if needed
            if index < self._next_attacker_index:
                self._next_attacker_index -= 1
            if self._next_attacker_index >= len(self.units):
                self._next_attacker_index = 0
            return True
        return False

    def remove_dead_units(self) -> List[Card]:
        """
        Remove all dead units from the board.

        Returns:
            List of removed (dead) cards for deathrattle processing
        """
        dead_units = [u for u in self.units if not u.is_alive()]
        for unit in dead_units:
            self.remove_unit(unit)
        return dead_units

    def get_unit_at(self, position: int) -> Optional[Card]:
        """Get unit at specific position, or None if invalid."""
        if 0 <= position < len(self.units):
            return self.units[position]
        return None

    def get_unit_position(self, card: Card) -> Optional[int]:
        """Get position of a card, or None if not on board."""
        if card in self.units:
            return self.units.index(card)
        return None

    def get_adjacent_units(self, card: Card) -> List[Card]:
        """Get units adjacent to the given card."""
        position = self.get_unit_position(card)
        if position is None:
            return []

        adjacent = []
        if position > 0:
            adjacent.append(self.units[position - 1])
        if position < len(self.units) - 1:
            adjacent.append(self.units[position + 1])
        return adjacent

    def is_full(self) -> bool:
        """Check if board is at maximum capacity."""
        return len(self.units) >= self.max_size

    def is_empty(self) -> bool:
        """Check if board has no units."""
        return len(self.units) == 0

    def size(self) -> int:
        """Get current number of units on board."""
        return len(self.units)

    def get_alive_units(self) -> List[Card]:
        """Get all living units on the board."""
        return [u for u in self.units if u.is_alive()]

    # === Tribe-related methods ===

    def count_tribe(self, tribe: TribeType) -> int:
        """Count units of a specific tribe."""
        return sum(1 for u in self.units if u.tribe == tribe)

    def get_tribe_counts(self) -> Dict[TribeType, int]:
        """Get count of each tribe on board."""
        counts: Dict[TribeType, int] = {}
        for unit in self.units:
            counts[unit.tribe] = counts.get(unit.tribe, 0) + 1
        return counts

    def get_units_by_tribe(self, tribe: TribeType) -> List[Card]:
        """Get all units of a specific tribe."""
        return [u for u in self.units if u.tribe == tribe]

    # === Combat-related methods ===

    def get_next_attacker(self) -> Optional[Card]:
        """
        Get the next unit to attack in combat.
        Uses round-robin from left to right.
        """
        alive = self.get_alive_units()
        if not alive:
            return None

        # Wrap around if needed
        if self._next_attacker_index >= len(self.units):
            self._next_attacker_index = 0

        # Find next alive unit from current position
        for i in range(len(self.units)):
            idx = (self._next_attacker_index + i) % len(self.units)
            if self.units[idx].is_alive() and not self.units[idx].has_attacked:
                self._next_attacker_index = idx + 1
                return self.units[idx]

        return None

    def get_taunt_units(self) -> List[Card]:
        """Get all units with taunt that are alive."""
        return [u for u in self.units if u.is_alive() and u.has_taunt]

    def get_valid_attack_targets(self) -> List[Card]:
        """
        Get valid targets for an attack.
        Must target taunt units first if any exist.
        """
        alive = self.get_alive_units()
        if not alive:
            return []

        taunt_units = self.get_taunt_units()
        if taunt_units:
            return taunt_units

        return alive

    def get_random_target(self) -> Optional[Card]:
        """Get a random valid attack target."""
        targets = self.get_valid_attack_targets()
        if not targets:
            return None
        return random.choice(targets)

    def get_random_unit(self) -> Optional[Card]:
        """Get a random living unit (ignoring taunt)."""
        alive = self.get_alive_units()
        if not alive:
            return None
        return random.choice(alive)

    def reset_for_combat(self) -> None:
        """Reset all units for a new combat phase."""
        self._next_attacker_index = 0
        for unit in self.units:
            unit.reset_for_combat()

    def reset_attack_flags(self) -> None:
        """Reset attack flags for a new round of attacks."""
        for unit in self.units:
            unit.has_attacked = False

    def has_attacked_all(self) -> bool:
        """Check if all alive units have attacked this round."""
        alive = self.get_alive_units()
        return all(u.has_attacked for u in alive) if alive else True

    # === Utility methods ===

    def clone_for_combat(self) -> Board:
        """
        Create a deep copy of the board for combat simulation.
        Original board is preserved.
        """
        new_board = Board(self.max_size)
        for unit in self.units:
            new_board.add_unit(unit.clone())
        return new_board

    def apply_auras(self) -> None:
        """
        Apply aura effects from units on the board.
        Called before combat starts.
        """
        from ..config.abilities import AbilityTrigger, AbilityType, ABILITIES

        for unit in self.units:
            if unit.ability_id == "none":
                continue

            ability = ABILITIES.get(unit.ability_id)
            if not ability:
                continue

            if ability.get("trigger") == AbilityTrigger.AURA:
                if ability.get("type") == AbilityType.BUFF_ADJACENT:
                    params = ability.get("params", {})
                    for adj in self.get_adjacent_units(unit):
                        adj.temporary_buff(
                            attack=params.get("attack", 0),
                            health=params.get("health", 0)
                        )

    def __str__(self) -> str:
        """String representation of the board."""
        if not self.units:
            return "[Empty Board]"

        unit_strs = [str(u) for u in self.units]
        return " | ".join(unit_strs)

    def __repr__(self) -> str:
        return f"Board(units={len(self.units)}/{self.max_size})"
