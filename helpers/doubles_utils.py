from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from typing import Optional
import random

# This represents an action that a single Pokemon can take -- it can either be a switch or a move
class Action:
    _actor, _action, _target = None, None, None

    def __init__(self, actor=None, action=None, target=None):
        self._actor = actor
        self._action = action
        self._target = target

    def isMove(self) -> bool:
        return isinstance(self._action, Move)

    def showdownify(self) -> str:
        """
        :return: The Showdown message we should return for this Action. You still have to do some work to get this move to work w/ others (eg include "/choose" and ",")
        :rtype: str
        """
        order = ""
        if self.isMove():
            order += "move " + str(self.move.id)
            if self.target is not None: order += " " + str(self.target)
        else:
            order += "switch " + self.switch.species
        return order

    @property
    def target(self) -> Optional[int]:
        """
        :return: The target of the move, if there is one (self does not count), otherwise, return None
        :rtype: int
        """
        return self._target if self._target != 0 else None

    @target.setter
    def target(self, target: Optional[int]):
        self._target = target

    @property
    def move(self) -> Optional[Move]:
        """
        :return: Move if the action is a Move, otherwise None
        :rtype: Move
        """
        return self._action if self.isMove() else None

    @property
    def switch(self) -> Optional[Pokemon]:
        """
        :return: Pokemon that the user wants to Switch to, if the action is a Switch, otherwise None
        :rtype: Move
        """
        return self._action if not self.isMove() else None

    @property
    def actor(self) -> Pokemon:
        """
        :return: Pokemon that is doing the action (either the switching or using a move)
        :rtype: Pokemon
        """
        return self._actor

    def __str__(self):
        if self.isMove(): return "Actor: " + self._actor.species + ",Move: " + str(self._action.id) + (",Target:" + str(self._target) if self._target is not None else "")
        else: return "Actor: " + self._actor.species + ",Switch: " + str(self._action.species)

    def __repr__(self):
        return self.__str__()

# Gets all possible moves for a Pokemon
def get_possible_moves(battle, mon):
    actions = []

    # If we somehow don't have any active pokemon, return default
    if not (battle.active_pokemon):
        return [None]

    # Find index of the mon, and if the mon passsed in isn'ta ctive, we raise a problem
    index = 0 if battle.active_pokemon[0] is not None and mon.species == battle.active_pokemon[0].species else 1
    if battle.active_pokemon[1] is not None and mon.species != battle.active_pokemon[1].species: raise("hullabaloo")

    # Iterate through available moves of Pokemon_1
    for move in battle.available_moves[index]:

        # Add all available move to list against all targets
        for target in battle.get_possible_showdown_targets(move, mon):
            actions.append(Action(mon, move, target))

    # Add all available switches to this list, if either the pokemon isn't trapped or we're forced to switch
    if not battle.trapped[index] or battle.force_switch[index]:
        for pokemon in battle.available_switches[index]:
            actions.append(Actor(mon, pokemon))

    return actions if actions is not None else [Action(mon, Move('struggle'), target) for target in battle.get_possible_showdown_targets(move, mon)]

# Limits search space for now:
# Only consider self-hit moves if they are self-switch or if they are super effective and your other pokemon has weakness policy
# Only consider self- or ally-boosting moves if you have boosts left, or if you dont, if the other pokemon has sucker punch
# Only consider terrain/reflect/weather moves if they will have an effect, or if another pokemon can change them and will move first (e.g. via move or switch or dynamax)
# Returns Tuple of Actions for each mon
def get_reasonable_moves(battle):
    """
    :return: A list of tuples that contain possible actions
    :rtype: List[(Action, Action)]
    """
    first_orders = []

    # If we somehow don't have any active pokemon, return default
    if not any(battle.active_pokemon):
        return [(None, None)]

    # Store whether we filtered anything
    filtered = False

    ######################### FIRST POKEMON #########################
    # Make sure there's a pokemon in the slot
    first_mon = battle.active_pokemon[0]
    if first_mon is not None:

        # Go through each move the pokemon knows
        for move in battle.available_moves[0]:

            # If we're out of PP, it shouldn't be considered an available move
            if move.current_pp == 0: continue

            # Iterate through all targets
            for target in battle.get_possible_showdown_targets(move, first_mon):

                # Only consider self- or ally-boosting moves if you have boosts left, or if you dont, if the other pokemon has sucker punch
                if move.boosts and move.target == 'self':
                    num_failed = 0
                    for stat in move.boosts:
                        if (first_mon.boosts[stat] == 6 and move.boosts[stat] > 0) or (first_mon.boosts[stat] == -6 and move.boosts[stat] < 0): num_failed += 1
                    if num_failed < len(move.boosts):
                        first_orders.append(Action(first_mon, move, target))
                    else:
                        filtered = True

                # Only consider side_condition moves if they will have an effect
                elif move.side_condition or move.weather or move.terrain:
                    if move.side_condition not in battle.side_conditions: first_orders.append(Action(first_mon, move, target))
                    else: filtered = True

                # In all other cases, just add this to the list of possible moves
                else:
                    first_orders.append(Action(first_mon, move, target))

        # Consider switches
        if not battle.trapped[0] or battle.force_switch[0]:
            for possible_mon in battle.available_switches[0]:
                first_orders.append(Action(first_mon, possible_mon))

        # If we have no viable first_orders, then we add Struggle
        if len(first_orders) == 0 and not filtered:
            for target in battle.get_possible_showdown_targets(Move("struggle"), first_mon):
                first_orders.append(Action(first_mon, Move("struggle"), target))

    ######################### SECOND POKEMON #########################
    second_orders = []
    second_mon = battle.active_pokemon[1]
    filtered = False
    if second_mon is not None:

        # Go through each move the pokemon knows
        for move in battle.available_moves[1]:

            # If we're out of PP, it shouldn't be considered an available move
            if move.current_pp == 0: continue

            # Iterate through all targets
            for target in battle.get_possible_showdown_targets(move, second_mon):

                # Only consider self- or ally-boosting moves if you have boosts left, or if you dont, if the other pokemon has sucker punch
                if move.boosts and move.target == 'self':
                    num_failed = 0
                    for stat in move.boosts:
                        if (second_mon.boosts[stat] == 6 and move.boosts[stat] > 0) or (second_mon.boosts[stat] == -6 and move.boosts[stat] < 0): num_failed += 1
                    if num_failed < len(move.boosts):
                        second_orders.append(Action(second_mon, move, target))
                    else: filtered = True

                # Only consider side_condition moves if they will have an effect
                elif move.side_condition or move.weather or move.terrain:
                    if move.side_condition not in battle.side_conditions: second_orders.append(Action(second_mon, move, target))
                    else: filtered = True

                # In all other cases, just add this to the list of possible moves
                else:
                    second_orders.append(Action(second_mon, move, target))

        # Consider switches
        if not battle.trapped[1] or battle.force_switch[1]:
            for possible_mon in battle.available_switches[1]:
                second_orders.append(Action(second_mon, possible_mon))

        # If we have no viable first_orders, then we add Struggle
        if len(second_orders) == 0 and not filtered:
            for target in battle.get_possible_showdown_targets(Move("struggle"), first_mon):
                second_orders.append(Action(second_mon, Move("struggle"), target))

    # If there's only one mon left or if we're forced to switch, then we've already handled all the conditions
    if len(second_orders) == 0 or battle.force_switch[0]: return list(map(lambda x: (x, None), first_orders))
    if len(first_orders) == 0 or battle.force_switch[1]: return list(map(lambda x: (None, x), second_orders))

    # Now, given all the first and second orders, we eliminate the following conditions:
    # Self-targets on damaging moves (if not to self-switch or to activate weakness policies), or switching to the same mon
    reasonable_orders = []

    # Go through all the orders, and four cases: move/move, switch/move, move/switch, switch/switch
    for action1 in first_orders:
        for action2 in second_orders:

            # TODO: what would be better here is if action 1 does damage and is self-target; basePower or damage
            # move/move, if move is self-hit, ensure that you are self-switching w/ other mon or are activating weakness policy
            if action1.isMove() and action2.isMove():
                if doesDamage(action1.move) and not (_is_valid_self_hit(action1.move, action2.actor) or action2.move.self_switch): continue
                if doesDamage(action2.move)  and not (_is_valid_self_hit(action2.move, action1.actor) or action1.move.self_switch): continue

            # switch/move: if move is self-hit, ensure that incoming pokemon is either activating weakness policy, or it's a self-switch
            if not action1.isMove() and action2.move and action2.target is not None and action2.target < 0:
                if not _is_valid_self_hit(action2.move, action1.switch): continue

            # move/switch
            if action1.isMove() and not action2.isMove() and action1.target is not None and action1.target < 0:
                if not _is_valid_self_hit(action1.move, action2.switch): continue

            # switch/switch: if we switch to the same pokemon, eliminate
            if not action1.isMove() and not action2.isMove():
                if action1.switch.species == action2.switch.species: continue

            reasonable_orders.append((action1, action2))

    return reasonable_orders

# Method to help reduce state space (will eventually default to 0). Here's the cases in which a self-hit is valid:
# Activate Weakness Policy
# Activate Justified
# Activate Berserk
# Activate Anger Point/Water Absorb/Volt Absorb/flash fire
#
# Right now, defaults to False to eliminate self-hits
def _is_valid_self_hit(move, target_mon):
    # if not move.self_switch and not (target.item = 'weaknesspolicy' and move.type.damange_multiplier(*target.types)): continue
    return False

def doesDamage(move):
    return move.base_power > 0 or move.damage
