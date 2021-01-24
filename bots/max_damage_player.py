import sys
import random
import itertools

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.player.battle_order import DoubleBattleOrder, DefaultDoubleBattleOrder, BattleOrder
from helpers.doubles_utils import *
import numpy as np

# Random Bot that doesn't self-hit
class MaxDamagePlayer(Player):
    def choose_move(self, battle):

        best_order = DefaultDoubleBattleOrder()

        # If we're not being forced to switch and are choosing our moves
        if not any(battle.force_switch):

            # Go through and get actions, filter them down to what's possible, and then eliminate ones that dont make sense
            orders = self.get_all_doubles_moves(battle)
            filtered_orders = list(filter(lambda x: x and DoubleBattleOrder.is_valid(battle, x), orders))

            # Iterate through all actions to pick best short-term move. These are our stored values
            most_damage, best_switch_multiplier = 0, 0

            # Go through every reasonable pair of actions and pick the pair that does the most high damage moves and multipliers of switch
            for double_order in filtered_orders:
                damage, switch_multiplier = 0, 0

                # Add up damage I'm probably going to do and switch multipliers compared to active pokemon
                for order in [double_order.first_order, double_order.second_order]:
                    if not order: continue

                    # If damaging move, Gg through each potential target and add up damage (subtract if self-damage)
                    if order.is_move() and (order.order.damage or order.order.base_power > 0):
                        for target in BattleOrder.get_affected_targets(battle, order):
                            stab = 1.5 if order.order.type in order.actor.types else 1
                            target_mon = battle.showdown_target_to_mon(target)

                            effectiveness = order.order.type.damage_multiplier(*target_mon.types) if target_mon is not None else 1
                            base_power = order.order.base_power

                            damage += base_power*stab*effectiveness*(-1 if target < 0 else 1)

                    # Calculate whether we're going to switch into an good environment (wrt types)
                    elif order.is_switch():
                        switch_multiplier += np.mean([compute_type_advantage(order.actor, opp) for opp in filter(lambda x: x is not None, battle.opponent_active_pokemon)])

                # Choose move if it does highest damage, and then if tied, the one that has the best switch
                if damage > most_damage:
                    best_order, most_damage, best_switch_multiplier = double_order, damage, switch_multiplier
                elif damage == most_damage and switch_multiplier >= best_switch_multiplier:
                    best_order, most_damage, best_switch_multiplier = double_order, damage, switch_multiplier

        # Force Switch situation; pick switch that has the best type advantage against the opponent's active mons
        else:
            orders = self.get_all_doubles_moves(battle)
            filtered_orders = list(filter(lambda x: DoubleBattleOrder.is_valid(battle, x), orders))

            # Go through every possible switch and choose one that has best type advantage against opponent's mon
            multiplier = -np.inf
            for double_order in filtered_orders:
                if not double_order.first_order or not double_order.first_order.is_switch(): continue

                # Store the score if there's a better switch
                multipliers = []
                for opp in battle.opponent_active_pokemon:
                    if opp is not None: multipliers.append(compute_type_advantage(double_order.first_order.actor, opp))

                if np.mean(multipliers) > multiplier: best_order, multiplier = double_order, np.mean(multipliers)

        return best_order

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
        # We use i + 1 as python indexes start from 0 but showdown's indexes start from 1, and return the first 4 mons, in term of importance
        return "/team " + "".join([str(i + 1) for i in ordered_mons[:4]])
