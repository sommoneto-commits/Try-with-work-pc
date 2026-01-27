"""
Combat System - Automatic combat resolution.

The combat system handles:
- Turn-by-turn attack resolution
- Ability triggers (deathrattle, on-attack, etc.)
- Damage calculation and unit death
- Combat result determination

Combat Flow:
1. Pre-combat setup (apply auras, synergies)
2. Start of combat triggers
3. Attack loop until one board is empty
4. Determine winner and damage

Design decisions:
- Combat uses cloned boards to preserve originals
- Attacks alternate between players
- Simultaneous damage (attacker and defender both deal damage)
- Comprehensive logging for visibility
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING
from enum import Enum, auto
import random

from ..models.board import Board
from ..models.card import Card
from ..config.abilities import AbilityTrigger, AbilityType, ABILITIES
from ..config.tribes import TribeType, get_tribe_synergy
from ..config.units import UNITS

if TYPE_CHECKING:
    from ..models.player import Player


class CombatOutcome(Enum):
    """Possible outcomes of combat."""
    PLAYER_WIN = auto()
    ENEMY_WIN = auto()
    DRAW = auto()


@dataclass
class CombatLog:
    """
    Records combat events for display.
    Each entry is a string describing what happened.
    """
    entries: List[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        """Add a log entry."""
        self.entries.append(message)

    def add_separator(self) -> None:
        """Add a visual separator."""
        self.entries.append("-" * 40)

    def get_all(self) -> List[str]:
        """Get all log entries."""
        return self.entries

    def __str__(self) -> str:
        return "\n".join(self.entries)


@dataclass
class CombatResult:
    """
    Result of a combat encounter.

    Attributes:
        outcome: Who won (PLAYER_WIN, ENEMY_WIN, DRAW)
        damage_to_player: Damage dealt to the player
        damage_to_enemy: Damage dealt to the enemy
        log: Combat log with details
        surviving_player_units: Units left on player's board
        surviving_enemy_units: Units left on enemy's board
    """
    outcome: CombatOutcome
    damage_to_player: int = 0
    damage_to_enemy: int = 0
    log: CombatLog = field(default_factory=CombatLog)
    surviving_player_units: int = 0
    surviving_enemy_units: int = 0


class CombatResolver:
    """
    Resolves combat between two boards.

    This is the core combat engine. It operates on cloned boards
    to avoid modifying original player state until combat is complete.
    """

    MAX_TURNS = 100  # Safety limit to prevent infinite loops

    def __init__(self):
        self.log = CombatLog()

    def resolve_combat(
        self,
        player_board: Board,
        enemy_board: Board,
        player_tier: int = 1,
        enemy_tier: int = 1
    ) -> CombatResult:
        """
        Resolve combat between two boards.

        Args:
            player_board: The human player's board
            enemy_board: The enemy (AI) board
            player_tier: Player's tavern tier (for damage calc)
            enemy_tier: Enemy's tavern tier (for damage calc)

        Returns:
            CombatResult with outcome, damage, and log
        """
        self.log = CombatLog()

        # Clone boards to avoid modifying originals
        p_board = player_board.clone_for_combat()
        e_board = enemy_board.clone_for_combat()

        self.log.add("=== COMBAT BEGINS ===")
        self.log.add(f"Player: {p_board.size()} units")
        self.log.add(f"Enemy:  {e_board.size()} units")
        self.log.add_separator()

        # Pre-combat: Apply synergies and auras
        self._apply_pre_combat_effects(p_board, "Player")
        self._apply_pre_combat_effects(e_board, "Enemy")

        # Trigger start of combat abilities
        self._trigger_start_of_combat(p_board, "Player")
        self._trigger_start_of_combat(e_board, "Enemy")

        # Reset combat state
        p_board.reset_for_combat()
        e_board.reset_for_combat()

        # Determine who attacks first (random)
        player_turn = random.choice([True, False])
        turn_count = 0

        # Main combat loop
        while not p_board.is_empty() and not e_board.is_empty():
            turn_count += 1
            if turn_count > self.MAX_TURNS:
                self.log.add("Combat timeout - forcing draw")
                break

            # Get attacker and defender boards
            if player_turn:
                attacker_board, defender_board = p_board, e_board
                attacker_name = "Player"
            else:
                attacker_board, defender_board = e_board, p_board
                attacker_name = "Enemy"

            # Get next attacker
            attacker = attacker_board.get_next_attacker()
            if not attacker:
                # All units attacked, reset for next round
                attacker_board.reset_attack_flags()
                attacker = attacker_board.get_next_attacker()

            if not attacker:
                player_turn = not player_turn
                continue

            # Get defender
            defender = defender_board.get_random_target()
            if not defender:
                break

            # Perform attack
            self._perform_attack(
                attacker, defender,
                attacker_board, defender_board,
                attacker_name
            )

            # Process deaths
            self._process_deaths(p_board, e_board)

            # Alternate turns
            player_turn = not player_turn

        # Determine outcome
        return self._determine_result(
            p_board, e_board,
            player_tier, enemy_tier
        )

    def _apply_pre_combat_effects(self, board: Board, owner: str) -> None:
        """Apply tribe synergies and auras before combat."""
        # Apply auras
        board.apply_auras()

        # Apply tribe synergies
        tribe_counts = board.get_tribe_counts()
        for tribe, count in tribe_counts.items():
            synergy = get_tribe_synergy(tribe, count)
            if synergy:
                self._apply_synergy(board, tribe, synergy, owner)

    def _apply_synergy(
        self,
        board: Board,
        tribe: TribeType,
        synergy: dict,
        owner: str
    ) -> None:
        """Apply a tribe synergy bonus."""
        synergy_type = synergy.get("type", "")
        attack_buff = synergy.get("attack", 0)
        health_buff = synergy.get("health", 0)

        if synergy_type == "buff_all":
            for unit in board.units:
                unit.temporary_buff(attack_buff, health_buff)
            if attack_buff or health_buff:
                self.log.add(
                    f"{owner}: {tribe.name} synergy buffs all units "
                    f"+{attack_buff}/+{health_buff}"
                )

        elif synergy_type == "buff_tribe":
            for unit in board.get_units_by_tribe(tribe):
                unit.temporary_buff(attack_buff, health_buff)

    def _trigger_start_of_combat(self, board: Board, owner: str) -> None:
        """Trigger all START_OF_COMBAT abilities."""
        for unit in board.units:
            if unit.has_ability_trigger(AbilityTrigger.START_OF_COMBAT):
                self._execute_ability(unit, board, owner, AbilityTrigger.START_OF_COMBAT)

    def _perform_attack(
        self,
        attacker: Card,
        defender: Card,
        attacker_board: Board,
        defender_board: Board,
        attacker_name: str
    ) -> None:
        """
        Execute an attack between two units.
        Both units deal damage to each other simultaneously.
        """
        attacker.has_attacked = True

        # Trigger on-attack abilities
        if attacker.has_ability_trigger(AbilityTrigger.ON_ATTACK):
            self._execute_ability(
                attacker, attacker_board, attacker_name,
                AbilityTrigger.ON_ATTACK
            )

        # Calculate damage
        attacker_damage = attacker.current_attack
        defender_damage = defender.current_attack

        # Log the attack
        self.log.add(
            f"{attacker_name}'s {attacker.name} ({attacker.current_attack}/"
            f"{attacker.current_health}) attacks "
            f"{defender.name} ({defender.current_attack}/{defender.current_health})"
        )

        # Apply damage (simultaneous)
        actual_damage_to_defender = defender.take_damage(attacker_damage)
        actual_damage_to_attacker = attacker.take_damage(defender_damage)

        # Log results
        if actual_damage_to_defender == 0 and defender.has_divine_shield is False:
            self.log.add(f"  {defender.name}'s Divine Shield absorbs the damage!")
        if actual_damage_to_attacker == 0 and attacker.has_divine_shield is False:
            self.log.add(f"  {attacker.name}'s Divine Shield absorbs the damage!")

        # Check for kills
        defender_died = not defender.is_alive()
        attacker_died = not attacker.is_alive()

        if defender_died:
            self.log.add(f"  {defender.name} dies!")
        if attacker_died:
            self.log.add(f"  {attacker.name} dies!")

        # Trigger on-kill if applicable
        if defender_died and attacker.is_alive():
            if attacker.has_ability_trigger(AbilityTrigger.ON_KILL):
                self._execute_ability(
                    attacker, attacker_board, attacker_name,
                    AbilityTrigger.ON_KILL
                )

    def _process_deaths(self, p_board: Board, e_board: Board) -> None:
        """Process all dead units and trigger deathrattles."""
        # Get dead units before removing
        p_dead = [u for u in p_board.units if not u.is_alive()]
        e_dead = [u for u in e_board.units if not u.is_alive()]

        # Trigger deathrattles
        for unit in p_dead:
            if unit.has_ability_trigger(AbilityTrigger.ON_DEATH):
                self._execute_ability(
                    unit, p_board, "Player",
                    AbilityTrigger.ON_DEATH, enemy_board=e_board
                )

        for unit in e_dead:
            if unit.has_ability_trigger(AbilityTrigger.ON_DEATH):
                self._execute_ability(
                    unit, e_board, "Enemy",
                    AbilityTrigger.ON_DEATH, enemy_board=p_board
                )

        # Remove dead units
        p_board.remove_dead_units()
        e_board.remove_dead_units()

    def _execute_ability(
        self,
        unit: Card,
        friendly_board: Board,
        owner: str,
        trigger: AbilityTrigger,
        enemy_board: Optional[Board] = None
    ) -> None:
        """
        Execute a unit's ability.
        This is the main ability resolution function.
        """
        ability = unit.get_ability()
        if not ability:
            return

        ability_type = ability.get("type")
        params = ability.get("params", {})
        ability_name = ability.get("name", "Unknown")

        self.log.add(f"  >> {owner}'s {unit.name} triggers '{ability_name}'")

        # Handle each ability type
        if ability_type == AbilityType.BUFF_SELF:
            attack = params.get("attack", 0)
            health = params.get("health", 0)
            unit.buff(attack, health)
            self.log.add(f"     Gained +{attack}/+{health}")

        elif ability_type == AbilityType.BUFF_TARGET:
            target_type = params.get("target", "random_ally")
            attack = params.get("attack", 0)
            health = params.get("health", 0)

            if target_type == "random_ally":
                allies = [u for u in friendly_board.units if u != unit and u.is_alive()]
                if allies:
                    target = random.choice(allies)
                    target.buff(attack, health)
                    self.log.add(f"     {target.name} gains +{attack}/+{health}")

        elif ability_type == AbilityType.BUFF_ALL_ALLIES:
            attack = params.get("attack", 0)
            health = params.get("health", 0)
            for ally in friendly_board.units:
                if ally != unit:
                    ally.temporary_buff(attack, health)
            self.log.add(f"     All allies gain +{attack}/+{health}")

        elif ability_type == AbilityType.BUFF_TRIBE:
            tribe_name = params.get("tribe", "NEUTRAL")
            attack = params.get("attack", 0)
            health = params.get("health", 0)
            try:
                tribe = TribeType[tribe_name]
                for ally in friendly_board.get_units_by_tribe(tribe):
                    ally.temporary_buff(attack, health)
                self.log.add(f"     All {tribe_name} allies gain +{attack}/+{health}")
            except KeyError:
                pass

        elif ability_type == AbilityType.DEAL_DAMAGE:
            target_type = params.get("target", "random_enemy")
            damage = params.get("damage", 1)

            if target_type == "random_enemy" and enemy_board:
                target = enemy_board.get_random_unit()
                if target:
                    target.take_damage(damage)
                    self.log.add(f"     Deals {damage} damage to {target.name}")

        elif ability_type == AbilityType.SUMMON_UNIT:
            unit_id = params.get("unit_id", "intern_token")
            count = params.get("count", 1)

            for _ in range(count):
                if not friendly_board.is_full():
                    if unit_id in UNITS:
                        token = Card.from_config(UNITS[unit_id])
                        position = friendly_board.get_unit_position(unit)
                        friendly_board.add_unit(token, position)
                        self.log.add(f"     Summons {token.name}")

    def _determine_result(
        self,
        p_board: Board,
        e_board: Board,
        player_tier: int,
        enemy_tier: int
    ) -> CombatResult:
        """Determine combat result and calculate damage."""
        self.log.add_separator()

        p_alive = p_board.size()
        e_alive = e_board.size()

        if p_alive > 0 and e_alive == 0:
            # Player wins
            damage = player_tier
            for unit in p_board.units:
                damage += unit.tier
            self.log.add(f"PLAYER WINS! Deals {damage} damage.")
            return CombatResult(
                outcome=CombatOutcome.PLAYER_WIN,
                damage_to_enemy=damage,
                damage_to_player=0,
                log=self.log,
                surviving_player_units=p_alive,
                surviving_enemy_units=0
            )

        elif e_alive > 0 and p_alive == 0:
            # Enemy wins
            damage = enemy_tier
            for unit in e_board.units:
                damage += unit.tier
            self.log.add(f"ENEMY WINS! Deals {damage} damage.")
            return CombatResult(
                outcome=CombatOutcome.ENEMY_WIN,
                damage_to_player=damage,
                damage_to_enemy=0,
                log=self.log,
                surviving_player_units=0,
                surviving_enemy_units=e_alive
            )

        else:
            # Draw
            self.log.add("DRAW! No damage dealt.")
            return CombatResult(
                outcome=CombatOutcome.DRAW,
                damage_to_player=0,
                damage_to_enemy=0,
                log=self.log,
                surviving_player_units=p_alive,
                surviving_enemy_units=e_alive
            )
