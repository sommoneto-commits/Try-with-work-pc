"""
Game Loop - Main game orchestration.

This module contains the Game class which manages:
- Game state and phases
- Player/AI initialization
- Round progression
- Console UI for player interaction
- Win/lose conditions

The game follows this structure:
1. SETUP: Initialize players, shops
2. SHOP_PHASE: Player makes purchases, AI acts
3. COMBAT_PHASE: Automatic battle
4. CHECK_GAME_OVER: Determine if game continues
5. Repeat from step 2

Design decisions:
- Text-based console UI for simplicity
- Clear separation between input handling and game logic
- Comprehensive feedback to player
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Optional
import os

from ..models.player import Player, AIPlayer
from ..models.shop import Shop
from ..models.card import Card
from ..systems.combat import CombatResolver, CombatOutcome


class GamePhase(Enum):
    """Current phase of the game."""
    SETUP = auto()
    SHOP_PHASE = auto()
    COMBAT_PHASE = auto()
    GAME_OVER = auto()


class Game:
    """
    Main game controller.

    Manages the overall game flow, player interactions,
    and transitions between phases.
    """

    def __init__(self, player_name: str = "You", ai_difficulty: str = "normal"):
        """
        Initialize a new game.

        Args:
            player_name: Name for the human player
            ai_difficulty: AI difficulty ("easy", "normal", "hard")
        """
        self.player = Player(name=player_name)
        self.ai = AIPlayer(name="Alkemy AI", difficulty=ai_difficulty)
        self.player_shop = Shop(tier=1)
        self.ai_shop = Shop(tier=1)
        self.combat_resolver = CombatResolver()

        self.round_number = 0
        self.phase = GamePhase.SETUP
        self.game_over = False
        self.winner: Optional[str] = None

        # Settings
        self.show_combat_log = True
        self.auto_play_cards = True  # Auto-play purchased cards to board

    def run(self) -> None:
        """
        Main game loop.
        Runs until game over condition is met.
        """
        self.setup_game()

        while not self.game_over:
            self.round_number += 1
            self.start_round()

            # Shop phase
            self.phase = GamePhase.SHOP_PHASE
            self.shop_phase()

            if self.game_over:
                break

            # Combat phase
            self.phase = GamePhase.COMBAT_PHASE
            self.combat_phase()

            # Check game over
            self.check_game_over()

        # Game over
        self.phase = GamePhase.GAME_OVER
        self.display_game_over()

    def setup_game(self) -> None:
        """Initialize game state."""
        self.phase = GamePhase.SETUP
        self.clear_screen()
        self.display_welcome()
        input("\nPress Enter to start...")

    def start_round(self) -> None:
        """Start a new round - refresh gold and shops."""
        self.player.start_round(self.round_number)
        self.ai.start_round(self.round_number)

        self.player_shop.refresh(self.player.tier)
        self.ai_shop.refresh(self.ai.tier)

    def shop_phase(self) -> None:
        """
        Handle the shop phase.
        Player makes choices, then AI acts.
        """
        self.clear_screen()
        print(f"\n{'='*50}")
        print(f"  ROUND {self.round_number} - SHOP PHASE")
        print(f"{'='*50}\n")

        # Player shop phase
        self.player_shop_loop()

        # AI shop phase (automatic)
        print("\n--- AI is shopping... ---")
        ai_actions = self.ai.take_shop_actions(self.ai_shop)
        for action in ai_actions:
            print(f"  AI: {action}")
        print("--- AI finished ---")

        input("\nPress Enter to start combat...")

    def player_shop_loop(self) -> None:
        """Handle player's shop interactions."""
        while True:
            self.display_shop_state()
            action = self.get_player_action()

            if action == "end":
                # Play all hand cards to board before combat
                while self.player.hand and not self.player.board.is_full():
                    card = self.player.hand[0]
                    self.player.play_card(card)
                    print(f"Auto-played {card.name} to board.")
                break
            elif action == "quit":
                self.game_over = True
                self.winner = "AI"
                break
            elif action.startswith("buy "):
                self.handle_buy(action)
            elif action.startswith("sell "):
                self.handle_sell(action)
            elif action == "reroll":
                self.handle_reroll()
            elif action == "tierup":
                self.handle_tier_up()
            elif action.startswith("play "):
                self.handle_play(action)
            elif action == "freeze":
                self.handle_freeze()
            elif action == "help":
                self.display_help()
            else:
                print("Unknown command. Type 'help' for commands.")

    def display_shop_state(self) -> None:
        """Display current shop and player state."""
        print("\n" + "=" * 60)
        print(f" {self.player.name} | HP: {self.player.health}/{self.player.max_health} | "
              f"Gold: {self.player.gold} | Tier: {self.player.tier}")
        print("=" * 60)

        # Shop
        print(f"\n{self.player_shop}")

        # Board
        print(f"\n--- YOUR BOARD ({self.player.board.size()}/7) ---")
        if self.player.board.units:
            for i, unit in enumerate(self.player.board.units):
                print(f"  {i+1}. {unit}")
        else:
            print("  [Empty]")

        # Hand
        print(f"\n--- YOUR HAND ({len(self.player.hand)}/10) ---")
        if self.player.hand:
            for i, card in enumerate(self.player.hand):
                print(f"  {i+1}. {card}")
        else:
            print("  [Empty]")

        # Available actions
        print("\n--- ACTIONS ---")
        tier_cost = self.player.get_tier_up_cost()
        actions = [
            f"buy <1-{len(self.player_shop.available_cards)}>",
            "sell <b/h><1-N>",
            f"reroll (1G)",
            f"tierup ({tier_cost}G)" if self.player.tier < 6 else "",
            "play <1-N>",
            "freeze",
            "end",
            "help"
        ]
        print("  " + " | ".join([a for a in actions if a]))

    def get_player_action(self) -> str:
        """Get and parse player input."""
        try:
            action = input("\n> ").strip().lower()
            return action
        except (EOFError, KeyboardInterrupt):
            return "quit"

    def handle_buy(self, action: str) -> None:
        """Handle buy command."""
        try:
            parts = action.split()
            if len(parts) != 2:
                print("Usage: buy <number>")
                return

            index = int(parts[1]) - 1
            card = self.player_shop.get_card(index)

            if not card:
                print("Invalid card number.")
                return

            if not self.player.can_afford(card.cost):
                print(f"Not enough gold. Need {card.cost}G, have {self.player.gold}G.")
                return

            if len(self.player.hand) >= Player.MAX_HAND_SIZE and self.player.board.is_full():
                print("No space! Sell something first.")
                return

            if self.player.buy_card(card, self.player_shop):
                print(f"Bought {card.name}!")
                # Auto-play if enabled and board has space
                if self.auto_play_cards and not self.player.board.is_full():
                    if card in self.player.hand:
                        self.player.play_card(card)
                        print(f"Auto-played {card.name} to board.")
            else:
                print("Couldn't buy card.")

        except ValueError:
            print("Invalid number.")

    def handle_sell(self, action: str) -> None:
        """Handle sell command."""
        try:
            parts = action.split()
            if len(parts) != 2:
                print("Usage: sell <b/h><number> (b=board, h=hand)")
                return

            location = parts[1][0]  # 'b' or 'h'
            index = int(parts[1][1:]) - 1

            if location == 'b':
                card = self.player.get_board_card(index)
            elif location == 'h':
                card = self.player.get_hand_card(index)
            else:
                print("Use 'b' for board or 'h' for hand. E.g., 'sell b1'")
                return

            if not card:
                print("Invalid card.")
                return

            gold = self.player.sell_card(card)
            print(f"Sold {card.name} for {gold}G.")

        except (ValueError, IndexError):
            print("Invalid format. Use: sell b1 or sell h2")

    def handle_reroll(self) -> None:
        """Handle reroll command."""
        if self.player.reroll_shop(self.player_shop):
            print("Shop refreshed!")
        else:
            print(f"Not enough gold for reroll. Need {Player.REROLL_COST}G.")

    def handle_tier_up(self) -> None:
        """Handle tier up command."""
        cost = self.player.get_tier_up_cost()
        if self.player.tier_up():
            print(f"Upgraded to Tier {self.player.tier}!")
            self.player_shop.refresh(self.player.tier)
        else:
            if self.player.tier >= 6:
                print("Already at maximum tier!")
            else:
                print(f"Not enough gold. Need {cost}G.")

    def handle_play(self, action: str) -> None:
        """Handle play card from hand command."""
        try:
            parts = action.split()
            if len(parts) != 2:
                print("Usage: play <number>")
                return

            index = int(parts[1]) - 1
            card = self.player.get_hand_card(index)

            if not card:
                print("Invalid card number.")
                return

            if self.player.board.is_full():
                print("Board is full! Sell something first.")
                return

            if self.player.play_card(card):
                print(f"Played {card.name}!")
            else:
                print("Couldn't play card.")

        except ValueError:
            print("Invalid number.")

    def handle_freeze(self) -> None:
        """Handle freeze shop command."""
        frozen = self.player_shop.toggle_freeze()
        if frozen:
            print("Shop frozen! It won't refresh next turn.")
        else:
            print("Shop unfrozen.")

    def display_help(self) -> None:
        """Display help information."""
        print("\n" + "=" * 40)
        print("  COMMANDS")
        print("=" * 40)
        print("  buy <N>      - Buy card N from shop")
        print("  sell b<N>    - Sell card N from board")
        print("  sell h<N>    - Sell card N from hand")
        print("  play <N>     - Play card N from hand to board")
        print("  reroll       - Refresh shop (costs 1G)")
        print("  tierup       - Upgrade tavern tier")
        print("  freeze       - Freeze/unfreeze shop")
        print("  end          - End shop phase, start combat")
        print("  help         - Show this help")
        print("  quit         - Quit the game")
        print("=" * 40)
        input("Press Enter to continue...")

    def combat_phase(self) -> None:
        """Execute combat between player and AI."""
        self.clear_screen()
        print(f"\n{'='*50}")
        print(f"  ROUND {self.round_number} - COMBAT!")
        print(f"{'='*50}\n")

        print("--- YOUR BOARD ---")
        print(f"  {self.player.board}")
        print("\n--- ENEMY BOARD ---")
        print(f"  {self.ai.board}")
        print()

        # Resolve combat
        result = self.combat_resolver.resolve_combat(
            self.player.board,
            self.ai.board,
            self.player.tier,
            self.ai.tier
        )

        # Show combat log
        if self.show_combat_log:
            print("\n--- COMBAT LOG ---")
            for entry in result.log.get_all():
                print(f"  {entry}")
            print()

        # Apply damage
        if result.outcome == CombatOutcome.PLAYER_WIN:
            self.ai.take_damage(result.damage_to_enemy)
            self.player.wins += 1
            print(f"\nYOU WIN! Enemy takes {result.damage_to_enemy} damage.")
            print(f"Enemy HP: {self.ai.health}")

        elif result.outcome == CombatOutcome.ENEMY_WIN:
            self.player.take_damage(result.damage_to_player)
            self.player.losses += 1
            print(f"\nYOU LOSE! You take {result.damage_to_player} damage.")
            print(f"Your HP: {self.player.health}")

        else:
            print("\nDRAW! No damage dealt.")

        input("\nPress Enter to continue...")

    def check_game_over(self) -> None:
        """Check if game should end."""
        if not self.player.is_alive:
            self.game_over = True
            self.winner = "AI"
        elif not self.ai.is_alive:
            self.game_over = True
            self.winner = self.player.name

    def display_game_over(self) -> None:
        """Display game over screen."""
        self.clear_screen()
        print("\n" + "=" * 50)
        print("  GAME OVER")
        print("=" * 50)

        if self.winner == self.player.name:
            print(f"\n  🎉 VICTORY! 🎉")
            print(f"  You defeated the Alkemy AI!")
        else:
            print(f"\n  💀 DEFEAT 💀")
            print(f"  The AI has defeated you.")

        print(f"\n  Final Stats:")
        print(f"    Rounds Played: {self.round_number}")
        print(f"    Wins: {self.player.wins}")
        print(f"    Losses: {self.player.losses}")
        print(f"    Your HP: {self.player.health}")
        print(f"    Enemy HP: {self.ai.health}")
        print("\n" + "=" * 50)

    def display_welcome(self) -> None:
        """Display welcome screen."""
        print("\n" + "=" * 50)
        print("  ALKEMY AUTOBATTLER")
        print("  A Hearthstone Battlegrounds-inspired game")
        print("=" * 50)
        print("\n  Welcome to Alkemy!")
        print("  Build your team of corporate warriors,")
        print("  and defeat the AI opponent!")
        print("\n  TRIBES:")
        print("    - Management: Team buffers")
        print("    - Staff: Support and deathrattles")
        print("    - Consulting: High damage dealers")
        print("    - Data & Analytics: Scaling units")
        print("    - Marketing & Media: Adjacent buffs")
        print("    - Brand Experience: Creative effects")
        print("    - Tech: Long-game scaling")
        print("\n  TIP: Type 'help' during shop phase for commands")

    def clear_screen(self) -> None:
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Entry point for the game."""
    print("\nAlkemy Autobattler")
    print("-" * 30)

    name = input("Enter your name (or press Enter for 'Player'): ").strip()
    if not name:
        name = "Player"

    print("\nSelect difficulty:")
    print("  1. Easy")
    print("  2. Normal")
    print("  3. Hard")

    difficulty_choice = input("Choice (1-3): ").strip()
    difficulty_map = {"1": "easy", "2": "normal", "3": "hard"}
    difficulty = difficulty_map.get(difficulty_choice, "normal")

    game = Game(player_name=name, ai_difficulty=difficulty)
    game.run()

    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
