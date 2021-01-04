from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.field import Field
from poke_env.environment.status import Status
from poke_env.environment.side_condition import SideCondition
from enum import Enum, unique, auto

from typing import Optional
import random
import numpy as np
import itertools

# This represents an action that a single Pokemon can take -- it can either be a switch or a move
class Action:
    _actor, _action, _targets = None, None, None

    def __init__(self, actor=None, action=None, affected_targets=None):
        self._actor = actor
        self._action = action # action is either a Move or a Pokemon
        self._affected_targets = affected_targets

    def isEmpty(self) -> bool:
        """
        :return: Whether the Action has been set to anything, or is an empty action (default)
        :rtype: bool
        """
        return self._actor == None and self._action == None and self._affected_targets == None

    def isMove(self) -> bool:
        """
        :return: Whether this action represents a move. If empty, will return False
        :rtype: bool
        """
        return self._action is not None and isinstance(self._action, Move)

    def isSwitch(self) -> bool:
        """
        :return: Whether this action represents a switch. If empty, will return False
        :rtype: bool
        """
        return self._action is not None and isinstance(self._action, Pokemon)

    # Turn this action into a showdown command. If there is more than one target, we do not need to specify the target
    def showdownify(self) -> str:
        """
        :return: The Showdown message we should return for this Action. You still have to do some work to get this move to work w/ others (eg include "/choose" and ",")
        :rtype: str
        """
        if self.isEmpty(): return "default"
        elif self.isMove():
            to_return = "move " + str(self.move.id)

            # If we have to return a target for a move, return the target
            if self.move.deduced_target in ['adjacentAlly', 'adjacentAllyOrSelf', 'any', 'normal']: to_return += " " + str(self.affected_targets[0])
            return to_return
        else: return "switch " + self.switch.species

    def doesDamage(self):
        """
        :return: Whether the move does damage. Returns false if this is a Switch
        :rtype: bool
        """
        return self.isMove() and (self.move.base_power > 0 or self.move.damage)

    @property
    def affected_targets(self) -> Optional[int]:
        """
        :return: The target of the move, if there is one (self does not count), otherwise, return None
        :rtype: List[Int]
        """
        return self._affected_targets

    @affected_targets.setter
    def affected_targets(self, affected_targets: Optional[int]):
        self._affected_targets = affected_targets

    @property
    def move(self) -> Optional[Move]:
        """
        :return: Move if the action is a Move, otherwise None
        :rtype: Move
        """
        return self._action if self.isMove() and not self.isEmpty() else None

    @property
    def switch(self) -> Optional[Pokemon]:
        """
        :return: Pokemon that the user wants to Switch to, if the action is a Switch, otherwise None
        :rtype: Move
        """
        return self._action if not self.isMove() and not self.isEmpty() else None

    @property
    def actor(self) -> Pokemon:
        """
        :return: Pokemon that is doing the action (either the switching or using a move)
        :rtype: Pokemon
        """
        return self._actor

    def __str__(self):
        if self.isMove():
            return "Actor: " + self._actor.species + ",Move: " + str(self._action.id) + (",Target:" + str(self._affected_targets) if self._affected_targets is not None else "")
        elif self.isSwitch(): return "Actor: " + self._actor.species + ",Switch: " + str(self._action.species)
        else: return "Empty Action"

    def __repr__(self):
        return self.__str__()

# This is an enum for all the target types you can have
class TargetType(Enum):
    """Enumeration, represent a non null field in a battle."""

    ADJACENT = auto()
    ADJACENT_ALLY_OR_SELF = auto()
    ADJACENT_FOE = auto()
    ALL = auto()
    ALL_ADJACENT = auto()
    ALLIES = auto()
    ALLY_SIDE = auto()
    ALLY_TEAM = auto()
    ANY = auto()
    FOE_SIDE = auto()
    NORMAL = auto()
    RANDOM_NORMAL = auto()
    SCRIPTED = auto()
    SELF = auto()

    def __str__(self) -> str:
        return f"{self.name} (field) object"

# This is an enum for all the Volatile Statuses you can have
class VolatileStatus(Enum):
    """Enumeration, represent a non null field in a battle."""
    OBSTRUCT = auto()
    OCTOLOCK = auto()
    LEECH_SEED = auto()
    MIRACLE_EYE = auto()
    MAX_GUARD = auto()
    PARTIALLY_TRAPPED = auto()
    FOCUS_ENERGY = auto()
    MAGNET_RISE = auto()
    TORMENT = auto()
    POWDER = auto()
    SPIKY_SHIELD = auto()
    POWER_TRICK = auto()
    ATTRACT = auto()
    SUBSTITUTE = auto()
    KINGS_SHIELD = auto()
    CURSE = auto()
    INGRAIN = auto()
    UPROAR = auto()
    ELECTRIFY = auto()
    NIGHTMARE = auto()
    FOLLOW_ME = auto()
    CHARGE = auto()
    STOCKPILE = auto()
    TAUNT = auto()
    LOCKED_MOVE = auto()
    CONFUSION = auto()
    FLINCH = auto()
    DESTINY_BOND = auto()
    MUST_RECHARGE = auto()
    EMBARGO = auto()
    TARSHOT = auto()
    RAGE_POWDER = auto()
    BANEFUL_BUNKER = auto()
    ROOST = auto()
    PROTECT = auto()
    SNATCH = auto()
    YAWN = auto()
    NO_RETREAT = auto()
    GASTRO_ACID = auto()
    TELEKINESIS = auto()
    LASER_FOCUS = auto()
    AQUA_RING = auto()
    GRUDGE = auto()
    MAGIC_COAT = auto()
    RAGE = auto()
    SMACK_DOWN = auto()
    HEAL_BLOCK = auto()
    HELPING_HAND = auto()
    FORESIGHT = auto()
    MINIMIZE = auto()
    DISABLE = auto()
    ENDURE = auto()
    IMPRISON = auto()
    DEFENSE_CURL = auto()
    BIDE = auto()
    SPOTLIGHT = auto()
    ENCORE = auto()

    def __str__(self) -> str:
        return f"{self.name} (field) object"

# Given a boost level, returns the modifier
def statMod(statStage):
    if statStage == 0: multiplier = 1
    elif statStage == 1: multiplier = 1.5
    elif statStage == -1: multiplier = 2.0/3
    elif statStage == 2: multiplier = 2
    elif statStage == -2: multiplier = 1.0/2
    elif statStage == 3: multiplier = 2.5
    elif statStage == -3: multiplier = 0.4
    elif statStage == 4: multiplier = 3
    elif statStage == -4: multiplier = 1.0/3
    elif statStage == 5: multiplier = 3.5
    elif statStage == -5: multiplier = 2.0/7
    elif statStage == 6: multiplier = 4
    elif statStage == -6: multiplier = 1.0/4
    return multiplier

# This is how we translate active pokemon to showdown targets returned from the Battle object
# Confirrmed that the opponent mapping is correct
def active_pokemon_to_showdown_target(i, opp=False):
    """
    :return: Given an index of the mon in active_pokemon or opponent_active_pokemon, returns the showdown int that we need to give for a showdown action
    :rtype: int
    """
    if opp: return {0: 1, 1: 2}[i]
    else: return {0: -1, 1: -2}[i]

# This is how we translate showdown targets pokemon to active pokemon returned from the Battle object
def showdown_target_to_active_pokemon(i, opp=False):
    """
    :return: Given a showdown target, returns the index that the pokemon is in active_pokemon or opponent_active_pokemon
    :rtype: int
    """
    if opp: return {1: 0, 2: 1}[i]
    else: return {-1: 0, -2: 1}[i]

# Given a battle state, mon and a move, return a list of list of targets that could be affected
def get_possible_affected_targets(battle, move, mon):
    """
    :return: Given a battle state, move and the mon using the move, returns all possible showdown targets for that move
    :rtype: List(List(int))
    """
    potential_affected_targets = []

    # Go through method that is provided to us, but change to make sure every target returned is actually a list of affected_targets that are affected by the move
    for target in battle.get_possible_showdown_targets(move, mon):

        # the method battle.get_possible_showdown_targets returns 0 if a move affects multiple mons. Handle this case and returns a list of affected_targets
        # (represented by ints) that are affected
        if target == 0:
            potentials = []

            # Add all pokemon who could be affected for moves like Surf or Earthquake
            if move.deduced_target == 'allAdjacent':
                for i, potential_mon in enumerate(battle.active_pokemon):
                    if potential_mon is not None and mon != potential_mon: potentials.append(active_pokemon_to_showdown_target(i, opp=False))

                for i, potential_mon in enumerate(battle.opponent_active_pokemon):
                    if potential_mon is not None: potentials.append(active_pokemon_to_showdown_target(i, opp=True))

            # For moves like Heatwave that affect all opponents, ensure that we list all potential affected opponents
            elif move.deduced_target in ['foeSide', 'allAdjacentFoes']:
                for i, potential_mon in enumerate(battle.opponent_active_pokemon):
                    if potential_mon is not None: potentials.append(active_pokemon_to_showdown_target(i, opp=True))

            # For moves that affect our side of the field
            elif move.deduced_target in ['allies', 'allySide', 'allyTeam']:
                for i, potential_mon in enumerate(battle.active_pokemon):
                    if potential_mon is not None and mon != potential_mon: potentials.append(active_pokemon_to_showdown_target(i, opp=True))

            # For moves that don't have targets (like self-moves)
            else: potentials.append(None)

            potential_affected_targets.append(potentials)
        else:
            # If this is a one-target move, and there is one pokemon left, technically both opponent targets work in Showdown, since there's only one valid
            # target. For our purposes, we only want to return the right target (where the mon is) so that we can retrieve the mon later without hassle
            if battle.opponent_active_pokemon[(showdown_target_to_active_pokemon(target, opp=target > 0))] is not None:
                potential_affected_targets.append([target])

    return potential_affected_targets

# Gets all possible moves for a Pokemon
def get_possible_moves(battle, mon):
    """
    :return: A list of all actions a pokemon can do in its position for the battle
    :rtype: List[Action]
    """
    actions = []

    # If we somehow don't have any active pokemon or the mon is None, return None
    if battle is None or not (battle.active_pokemon) or mon is None:
        return [Action()]

    # Find index of the mon, and if the mon passsed in isn't active, we raise a problem
    index = 0 if battle.active_pokemon[0] is not None and mon.species == battle.active_pokemon[0].species else 1
    if all(battle.active_pokemon) and mon.species != battle.active_pokemon[0].species and mon.species != battle.active_pokemon[1].species:
        raise("you passed in a mon that doesnt exist!")

    # Iterate through available moves
    for move in battle.available_moves[index]:

        # Add all available move to list against all targets
        for affected_targets in get_possible_affected_targets(battle, move, mon):
            actions.append(Action(mon, move, affected_targets))

    # Add all available switches to this list, if either the pokemon isn't trapped or we're forced to switch
    if not battle.trapped[index] or battle.force_switch[index]:
        for pokemon in battle.available_switches[index]:
            actions.append(Action(mon, pokemon))

    # Always return an empty action if there are none available
    return actions if len(actions) > 0 else [Action()]

# Filter tuples of moves to ones that are possible
def filter_to_possible_moves(battle, actions):
    """
    :return: A list of tuples that contain possible actions
    :rtype: List[(Action, Action)]
    """
    filtered_moves = []

    # Iterate through every action
    for action1, action2 in actions:

        # Can't switch to the same mon
        if action1.isSwitch() and action2.isSwitch() and action1.switch.species == action2.switch.species: continue

        # Can't use a move w/ no PP
        if (action1.isMove() and action1.move.current_pp == 0) or (action2.isMove() and action2.move.current_pp == 0): continue

        filtered_moves.append((action1, action2))

    return filtered_moves

# Filters all actions to reasonable moves
def filter_to_reasonable_moves(battle, actions):
    """
    :return: A list of tuples that contain reasonable actions
    :rtype: List[(Action, Action)]
    """
    reasonable_moves = []

    for action1, action2 in actions:
        if (action1.isMove() and action1.move.current_pp == 0) or (action2.isMove() and action2.move.current_pp == 0): continue

        if _useless_self_boost(action1) or _useless_self_boost(action2): continue
        if _useless_battle_condition(battle, action1) or _useless_battle_condition(battle, action2): continue
        if _useless_self_hit(battle, action1) or _useless_self_hit(battle, action2): continue

        reasonable_moves.append((action1, action2))

    return reasonable_moves

# Return if the self-boost is inneffectual
def _useless_self_boost(action):
    if action.isMove():

        # Only consider self- or ally-boosting moves if you have boosts left, or if you dont, if the other pokemon has sucker punch
        if action.move.boosts and action.move.target == 'self':
            num_failed = 0
            for stat in action.move.boosts:
                if (action.actor.boosts[stat] == 6 and action.move.boosts[stat] > 0) or (action.move.boosts[stat] == -6 and action.move.boosts[stat] < 0): num_failed += 1
            if num_failed < len(action.move.boosts):
                return True
    return False

# Return if side condition move is useless. This should eventually return False for everything when we learn better (e.g. Torkoal switch-ins)
def _useless_battle_condition(battle, action):
    if not action.isMove(): return False

    if action.move.side_condition and action.move.side_condition in battle.side_conditions: return True
    if action.move.weather and battle.weather and action.move.weather == battle.weather: return True
    if action.move.terrain and battle.fields and action.move.terrain in battle.fields: return True
    if action.move.pseudo_weather and battle.fields and action.move.pseudo_weather in battle.fields: return True
    return False

# Method to help reduce state space (will eventually default to 0). Here's the cases in which a self-hit is valid:
# Can default to False to eliminate self-hits, and True to not eliminate anything
def _useless_self_hit(battle, action):

    # Eliminate easy conditions in which this is not a useless self hit
    if not action.isMove(): return False
    if not action.doesDamage(): return False
    if action.move.self_switch: return False

    # If it's a self-hit
    if action.affected_targets is not None and (-1 in action.affected_targets or -2 in action.affected_targets):

        # Get the mon who is going to be hit
        target_mon = battle.active_pokemon[min(action.affected_targets)]

        # Only allow this as a potential move under these conditions
        if target_mon.item == 'weaknesspolicy' and action.move.type.damage_multiplier(*target_mon.types) >= 2: return True
        elif target_mon.ability == 'Berserk': return False
        elif target_mon.ability == 'Justified' and action.move.type == 'DARK': return False
        elif target_mon.ability == 'Water Absorb' and action.move.type == 'WATER': return False
        elif target_mon.ability == 'Volt Absorb' and action.move.type == 'ELECTRIC': return False
        elif target_mon.ability == 'Flash Fire' and action.move.type == 'FIRE': return False
        else: return True

    return False

# We evaluate the performance on mon1 against mon2 by its type advantage
# We return how much better you can perform
def compute_type_advantage(mon1, mon2):

    a_on_b = b_on_a = -np.inf

    # Store the max damage multiplier that the mon can do
    for type_ in mon1.types:
        if type_: a_on_b = max(a_on_b, type_.damage_multiplier(*mon2.types))

    # Do the other way around
    for type_ in mon2.types:
        if type_: b_on_a = max(b_on_a, type_.damage_multiplier(*mon1.types))

    # Our performance metric is the difference between the two
    return a_on_b - b_on_a

# We compute the speed of a pokemon, based on the battle conditions, the mon itself and
# whether it is an opponent mon. Does not take into account unburden
# TODO: test
def compute_effective_speed(battle, mon):
    speed = mon.stats['spe']

    # Abilities
    if battle.weather:
        if mon.ability == 'Slush Rush' and battle.weather.name == 'HAIL': speed *= 2
        elif mon.ability == 'Sand Rush' and battle.weather.name == 'SANDSTORM': speed *= 2
        elif mon.ability == 'Chlorophyll' and battle.weather.name in  ['SUNNYDAY', 'DESOLATELAND']: speed *= 2
        elif mon.ability == 'Swift Swim' and battle.weather.name in ['RAINDANCE', 'PRIMORDIALSEA']: speed *= 2
        elif mon.ability == 'Surge Surfer' and Field.ELECTRIC_TERRAIN in battle.fields: speed *= 2 # Field(1) corresponds to Electric Terrain

    # Incorporate boosts
    speed *= statMod(mon.boosts['spe'])

    # Incorporate status (Paralysis) if the mon doesnt have quickfeed
    if mon.ability == 'Quick Feet' and not mon.status: speed *= 1.5
    elif mon.status.name == 'PAR': speed *= .5 # Status(4) corresponds to paralysis

    # Held Items (choice scarf, iron ball)
    if mon.item == 'ironball': speed *= .5
    elif mon.item == 'choicescarf': speed *= 1.5

    # Side Conditions
    if Status.GRASS_PLEDGE in battle.side_conditions: speed *= .25 # GRASS_PLEDGE, or creating a swamp
    elif Status.TAILWIND in battle.side_conditions: speed *= 2 # TAILWIND

    return speed

# We compute the speed of an opponent pokemon in the worst case scenario
# TODO: implement, computed from base_stats, assuming best nature and EVs, possible_abilities
def compute_worst_case_scenario_speed(battle, mon):
    tr = Field.TRICK_ROOM in battle.fields

    # Use stat equation
    speed = (2*mon.base_stats['spe'] + 31 + 252/4)*mon.level/100 + 5

    # Natures modification
    speed *= .9 if tr else 1.1

    # Abilities; assuming that a mon would use their speed abilities
    if battle.weather:
        if 'Slush Rush' in mon.possible_abilities and battle.weather.name == 'HAIL': speed *= 2
        elif 'Sand Rush' in mon.possible_abilities and battle.weather.name == 'SANDSTORM': speed *= 2
        elif 'Chlorophyll' in mon.possible_abilities and battle.weather.name in  ['SUNNYDAY', 'DESOLATELAND']: speed *= 2
        elif 'Swift Swim' in mon.possible_abilities and battle.weather.name in ['RAINDANCE', 'PRIMORDIALSEA']: speed *= 2
        elif 'Surge Surfer' in mon.possible_abilities  and Field.ELECTRIC_TERRAIN in battle.fields: speed *= 2 # Field(1) corresponds to Electric Terrain

    # Incorporate boosts
    speed *= statMod(mon.boosts['spe'])

    # Incorporate status (Paralysis) if the mon doesnt have quickfeed
    if mon.ability == 'Quick Feet' and not mon.status: speed *= 1.5
    elif mon.status.name == 'PAR': speed *= .5 # Status(4) corresponds to paralysis

    # We don't take into account Held Items (choice scarf, iron ball) because it would make this reward useless
    # in situations where they aren't available. Eventually, we need to run code to use all battle cues (hail, sandstorm, mon order)
    # to guess speed number ranges
    # if mon.item == 'ironball': speed *= .5
    # elif mon.item == 'choicescarf': speed *= 1.5

    # Side Conditions
    if Status.GRASS_PLEDGE in battle.side_conditions: speed *= .25 # GRASS_PLEDGE, or creating a swamp
    elif Status.TAILWIND in battle.side_conditions: speed *= 2 # TAILWIND

    return speed
