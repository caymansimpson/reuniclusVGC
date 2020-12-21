import sys
import random
import itertools

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from helpers.doubles_utils import *
import numpy as np

# Random Bot that doesn't self-hit
class MaxDamagePlayer(Player):
    def choose_move(self, battle):

        # If we're not being forced to switch and are choosing our moves
        if not any(battle.force_switch):

            # Go through and get actions, filter them down to what's possible, and then eliminate ones that dont make sense
            first_moves = get_possible_moves(battle, battle.active_pokemon[0])
            second_moves = get_possible_moves(battle, battle.active_pokemon[1])

            all_possible_moves = itertools.product(first_moves, second_moves)
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
            reasonable_moves = filter_to_reasonable_moves(battle, filtered_moves)

            # Iterate through all actions to pick best short-term move. These are our stored values
            action1, action2, most_damage, best_switch_multiplier = Action(), Action(), 0, 0

            # Go through every move and pick high damage moves and multipliers of switch
            for a1, a2 in (reasonable_moves if len(reasonable_moves) > 0 else filtered_moves):
                damage, switch_multiplier = 0, 0

                # Add damage Im probably going to do
                for action in [a1, a2]:

                    # TODO: for each a1 and a2, rack up damage for all possible targets (subtract damage if youre the target)
                    if action.doesDamage():
                        for target in aaaA:
                        damage += action.move.base_power*action.move.type.damage_multiplier(*battle.active_pokemon[a1.target].types)*(1.5 if a1.move.type in a1.actor.types else 1)
                if a2.doesDamage(): damage += a2.move.base_power*a2.move.type.damage_multiplier(*battle.active_pokemon[a2.target].types)*(1.5 if a2.move.type in a2.actor.types else 1)

                # Calculate average type advantage if I switch
                if a1.isSwitch(): switch_multiplier += np.mean([compute_type_advantage(a1.actor, opp) for opp in battle.opponent_team.values()])
                if a2.isSwitch(): switch_multiplier += np.mean([compute_type_advantage(a2.actor, opp) for opp in battle.opponent_team.values()])

                # Choose move if it does highest damage, and then if tied, the one that has the best switch
                if damage > best_damage: action1, action2, most_damage, best_switch_multiplier = a1, a2, damage, switch_multiplier
                elif damage == best_damage and switch_multiper >= best_switch_multiplier: action1, action2, most_damage, best_switch_multiplier = a1, a2, damage, switch_multiplier


            # Order actions when a pokemon is fainted so that the only action goes first
            if battle.active_pokemon[0] is None: action1, action2 = action2, action1

            order = "/choose " + action1.showdownify() + "," + action2.showdownify()

        # Force Switch situation; pick switch that has the best type advantage against the opponent's active mons
        else:
            moves = get_possible_moves(battle, battle.active_pokemon[0 if battle.force_switch[0] else 1])
            all_possible_moves = itertools.product(moves, [Action()])
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)

            # Go through every possible switch and choose one that has best type advantage against opponent's mon
            best_switch, multiplier = Action(), -np.inf
            for action, _ in filtered_moves:
                if not action.isSwitch(): continue

                # Store the score if there's a better switch
                multipliers = []
                for opp in battle.opponent_active_pokemon:
                    if opp is not None: multipliers.append(compute_type_advantage(action.actor, opp))

                if np.mean(multipliers) > multiplier: best_switch, multiplier = action, np.mean(multipliers)

            order = "/choose " + best_switch.showdownify()

        return order

    # Choose mons who have the best average performance of the other team
    def teampreview(self, battle):
        mon_performance = {}

        # For each of our pokemons
        for i, mon in enumerate(battle.team.values()):

            # We store their average performance against the opponent team
            mon_performance[i] = np.mean([compute_type_advantage(mon, opp) for opp in battle.opponent_team.values()])

        # We sort our mons by performance
        ordered_mons = sorted(mon_performance, key=lambda k: -mon_performance[k])

        # We start with the one we consider best overall
        # We use i + 1 as python indexes start from 0
        #  but showdown's indexes start from 1
        return "/team " + "".join([str(i + 1) for i in ordered_mons])

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

    # Our performance metric is the product between the two
    return a_on_b - b_on_a
