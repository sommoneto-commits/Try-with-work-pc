"""
Player Model - Represents a human or AI player.

The Player class manages:
- Health and game-over state
- Gold economy
- Hand (purchased but not placed units)
- Board (units in combat)
- Shop tier progression

Design decisions:
- AIPlayer inherits from Player for code reuse
- Economy logic is centralized here
- Board and hand are managed separately
"""

from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
import random

from .board import Board
from .card import Card

if TYPE_CHECKING:
    from .shop import Shop


class Player:
    """
    Represents a player in the game.

    Attributes:
        name: Display name
        health: Current health points
        max_health: Maximum health
        gold: Current gold
        max_gold: Maximum gold per turn (increases with rounds)
        tier: Current tavern tier (affects shop pool)
        max_tier: Maximum achievable tier
        board: The player's battlefield
        hand: Cards bought but not placed
        is_alive: Whether the player is still in the game
    """

    # Game constants
    STARTING_HEALTH = 30
    STARTING_GOLD = 3
    MAX_HAND_SIZE = 10
    MAX_TIER = 6

    # Gold costs
    TIER_UP_COSTS = {
        1: 5,   # Cost to go from tier 1 to 2
        2: 7,   # Cost to go from tier 2 to 3
        3: 8,   # Cost to go from tier 3 to 4
        4: 9,   # Cost to go from tier 4 to 5
        5: 10,  # Cost to go from tier 5 to 6
    }

    REROLL_COST = 1
    SELL_BASE_VALUE = 1

    def __init__(self, name: str = "Player"):
        self.name = name
        self.health = self.STARTING_HEALTH
        self.max_health = self.STARTING_HEALTH
        self.gold = 0
        self.max_gold = self.STARTING_GOLD
        self.tier = 1
        self.board = Board()
        self.hand: List[Card] = []
        self.is_alive = True

        # Stats tracking
        self.wins = 0
        self.losses = 0
        self.rounds_played = 0

    def start_round(self, round_number: int) -> None:
        """
        Called at the start of each round.
        Increases max gold and refills gold.
        """
        self.rounds_played = round_number

        # Gold increases each round, capped at 10
        self.max_gold = min(10, self.STARTING_GOLD + round_number - 1)
        self.gold = self.max_gold

    def can_afford(self, cost: int) -> bool:
        """Check if player can afford a cost."""
        return self.gold >= cost

    def spend_gold(self, amount: int) -> bool:
        """
        Spend gold if possible.
        Returns True if successful.
        """
        if amount <= 0:
            return True
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def gain_gold(self, amount: int) -> None:
        """Add gold to player's pool."""
        if amount > 0:
            self.gold += amount

    # === Card management ===

    def add_to_hand(self, card: Card) -> bool:
        """
        Add a card to hand.
        Returns False if hand is full.
        """
        if len(self.hand) >= self.MAX_HAND_SIZE:
            return False
        self.hand.append(card)
        return True

    def remove_from_hand(self, card: Card) -> bool:
        """Remove a card from hand."""
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False

    def play_card(self, card: Card, position: Optional[int] = None) -> bool:
        """
        Move a card from hand to board.
        Returns False if card not in hand or board full.
        """
        if card not in self.hand:
            return False
        if self.board.is_full():
            return False

        self.hand.remove(card)
        return self.board.add_unit(card, position)

    def sell_card(self, card: Card) -> int:
        """
        Sell a card from hand or board.
        Returns gold gained (0 if card not found).
        """
        # Check if card is on board
        if card in self.board.units:
            self.board.remove_unit(card)
            gold = card.sell_value
            self.gain_gold(gold)
            return gold

        # Check if card is in hand
        if card in self.hand:
            self.hand.remove(card)
            gold = card.sell_value
            self.gain_gold(gold)
            return gold

        return 0

    # === Shop interaction ===

    def buy_card(self, card: Card, shop: Shop) -> bool:
        """
        Buy a card from the shop.
        Returns True if purchase successful.
        """
        if not self.can_afford(card.cost):
            return False

        if len(self.hand) >= self.MAX_HAND_SIZE and self.board.is_full():
            return False  # No space for the card

        if not shop.remove_card(card):
            return False  # Card not in shop

        self.spend_gold(card.cost)

        # Try to add to hand first, then board
        if not self.add_to_hand(card):
            if not self.board.add_unit(card):
                # Shouldn't happen, but safety check
                shop.add_card(card)
                self.gold += card.cost
                return False

        return True

    def reroll_shop(self, shop: Shop) -> bool:
        """
        Reroll the shop for new cards.
        Returns True if successful.
        """
        if not self.can_afford(self.REROLL_COST):
            return False

        self.spend_gold(self.REROLL_COST)
        shop.refresh(self.tier)
        return True

    def tier_up(self) -> bool:
        """
        Upgrade tavern tier if possible.
        Returns True if successful.
        """
        if self.tier >= self.MAX_TIER:
            return False

        cost = self.TIER_UP_COSTS.get(self.tier, 999)
        if not self.can_afford(cost):
            return False

        self.spend_gold(cost)
        self.tier += 1
        return True

    def get_tier_up_cost(self) -> int:
        """Get cost to upgrade to next tier."""
        return self.TIER_UP_COSTS.get(self.tier, 0)

    # === Combat ===

    def take_damage(self, amount: int) -> None:
        """
        Apply damage to player's health.
        Checks for game over.
        """
        if amount <= 0:
            return

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_alive = False

    def calculate_combat_damage(self, enemy_board: Board) -> int:
        """
        Calculate damage dealt to enemy after winning combat.
        Damage = player tier + sum of enemy unit tiers
        """
        remaining_units = self.board.get_alive_units()
        if not remaining_units:
            return 0

        damage = self.tier
        for unit in remaining_units:
            damage += unit.tier

        return damage

    # === Utility ===

    def get_hand_card(self, index: int) -> Optional[Card]:
        """Get card from hand by index."""
        if 0 <= index < len(self.hand):
            return self.hand[index]
        return None

    def get_board_card(self, index: int) -> Optional[Card]:
        """Get card from board by index."""
        return self.board.get_unit_at(index)

    def get_all_cards(self) -> List[Card]:
        """Get all cards (board + hand)."""
        return list(self.board.units) + self.hand

    def __str__(self) -> str:
        return f"{self.name} (HP: {self.health}, Gold: {self.gold}, Tier: {self.tier})"


class AIPlayer(Player):
    """
    AI-controlled player.

    The AI uses simple heuristics for decision making:
    - Buys cards to fill board
    - Tiers up when appropriate
    - Rerolls when looking for upgrades

    AI difficulty can be adjusted by modifying decision weights.
    """

    # AI behavior weights (adjust for difficulty)
    TIER_UP_PRIORITY = 0.3      # Chance to prioritize tier up
    REROLL_THRESHOLD = 0.2      # Chance to reroll when board not full
    AGGRESSION = 0.5            # Affects stat vs ability preference

    def __init__(self, name: str = "AI Opponent", difficulty: str = "normal"):
        super().__init__(name)
        self.difficulty = difficulty
        self._adjust_for_difficulty()

    def _adjust_for_difficulty(self) -> None:
        """Adjust AI behavior based on difficulty."""
        if self.difficulty == "easy":
            self.TIER_UP_PRIORITY = 0.1
            self.REROLL_THRESHOLD = 0.1
        elif self.difficulty == "hard":
            self.TIER_UP_PRIORITY = 0.4
            self.REROLL_THRESHOLD = 0.3
        # Normal uses default values

    def take_shop_actions(self, shop: Shop) -> List[str]:
        """
        Execute AI's shop phase decisions.
        Returns list of action descriptions for logging.
        """
        actions = []

        # Simple AI loop: spend all gold
        while self.gold > 0:
            action = self._decide_action(shop)
            if action == "done":
                break
            elif action == "tier_up":
                if self.tier_up():
                    actions.append(f"Tiered up to {self.tier}")
                    shop.refresh(self.tier)  # Refresh after tier up
                else:
                    break
            elif action == "buy":
                card = self._choose_card_to_buy(shop)
                if card and self.buy_card(card, shop):
                    actions.append(f"Bought {card.name}")
                    # Play card to board if in hand and board not full
                    if card in self.hand and not self.board.is_full():
                        self.play_card(card)
                        actions.append(f"Played {card.name}")
                else:
                    break
            elif action == "reroll":
                if self.reroll_shop(shop):
                    actions.append("Rerolled shop")
                else:
                    break

        # Place any remaining hand cards
        while self.hand and not self.board.is_full():
            card = self.hand[0]
            self.play_card(card)
            actions.append(f"Played {card.name} from hand")

        return actions

    def _decide_action(self, shop: Shop) -> str:
        """Decide what action to take."""
        # Check if we can do anything
        if self.gold <= 0:
            return "done"

        # Priority: fill board first
        if not self.board.is_full() and shop.available_cards:
            affordable_cards = [c for c in shop.available_cards if c.cost <= self.gold]
            if affordable_cards:
                return "buy"

        # Consider tier up
        tier_cost = self.get_tier_up_cost()
        if self.tier < self.MAX_TIER and self.gold >= tier_cost:
            if random.random() < self.TIER_UP_PRIORITY or self.board.is_full():
                return "tier_up"

        # Consider reroll
        if self.gold >= self.REROLL_COST and not self.board.is_full():
            if random.random() < self.REROLL_THRESHOLD:
                return "reroll"

        # Try to buy something
        if shop.available_cards:
            affordable_cards = [c for c in shop.available_cards if c.cost <= self.gold]
            if affordable_cards:
                return "buy"

        return "done"

    def _choose_card_to_buy(self, shop: Shop) -> Optional[Card]:
        """Choose which card to buy from shop."""
        affordable = [c for c in shop.available_cards if c.cost <= self.gold]
        if not affordable:
            return None

        # Simple heuristic: prefer higher stat total
        def card_value(card: Card) -> float:
            stat_value = card.base_attack + card.base_health
            tier_value = card.tier * 0.5
            return stat_value + tier_value

        return max(affordable, key=card_value)
