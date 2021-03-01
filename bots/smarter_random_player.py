import sys
import random
import itertools
import re
from typing import Optional, Union, List

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.environment.double_battle import DoubleBattle
from poke_env.player.battle_order import DoubleBattleOrder, DefaultDoubleBattleOrder, BattleOrder
from poke_env.player.random_player import RandomPlayer
from helpers.doubles_utils import *
from bots.random_doubles_player import RandomDoublesPlayer

# Random Bot that doesn't self-hit
# TODO: there are some errors when you put edgecase teams against edgecase teams
class SmarterRandomPlayer(Player):

    def choose_move(self, battle):

        orders = self.get_all_doubles_moves(battle)
        order = None

        # If we're not being forced to switch and are choosing our moves
        if not any(battle.force_switch):

            filtered_orders = list(filter(lambda x: DoubleBattleOrder.is_valid(battle, x), orders))
            reasonable_orders = self._filter_to_reasonable_moves(battle, filtered_orders)

            if reasonable_orders: order =  random.choice(reasonable_orders)
            if len(filtered_orders) > 0: order = random.choice(filtered_orders)
            else: order = DefaultDoubleBattleOrder()

            return order.message

        # Force Switch situation
        else: return random.choice(orders).message

    # Filters all orders to reasonable moves
    def _filter_to_reasonable_moves(self, battle: List[DoubleBattle], orders: List[DoubleBattleOrder]):
        """
        :return: A list of tuples that contain reasonable orders
        :rtype: List[DoubleBattleOrder]
        """
        reasonable_moves = []

        for order in orders:
            if order.first_order and order.first_order.is_move() and order.first_order.order.current_pp == 0: continue
            if order.second_order and order.second_order.is_move() and order.second_order.order.current_pp == 0: continue

            if self._useless_self_boost(order.first_order) or self._useless_self_boost(order.second_order): continue
            if self._useless_battle_condition(battle, order.first_order) or self._useless_battle_condition(battle, order.second_order): continue
            if self._useless_self_hit(battle, order.first_order) or self._useless_self_hit(battle, order.second_order): continue

            reasonable_moves.append(order)

        return reasonable_moves

    # Return if the self-boost is inneffectual
    def _useless_self_boost(self, order: BattleOrder):
        if order and order.is_move():

            # Only consider self- or ally-boosting moves if you have boosts left, or if you dont, if the other pokemon has sucker punch
            if order.order.boosts and order.order.target == 'self':
                num_failed = 0
                for stat in order.order.boosts:
                    if (order.actor.boosts[stat] == 6 and order.order.boosts[stat] > 0) or (order.order.boosts[stat] == -6 and order.order.boosts[stat] < 0): num_failed += 1
                if num_failed < len(order.order.boosts):
                    return True
        return False

    # Return if side condition move is useless. This should eventually return False for everything when we learn better (e.g. Torkoal switch-ins)
    def _useless_battle_condition(self, battle, order: BattleOrder):
        if not order or not order.is_move(): return False

        if order.order.side_condition and order.order.side_condition in battle.side_conditions: return True
        if order.order.weather and battle.weather and order.order.weather == battle.weather: return True
        if order.order.terrain and battle.fields and order.order.terrain in battle.fields: return True
        if order.order.pseudo_weather and battle.fields and order.order.pseudo_weather in battle.fields: return True
        return False

    # Method to help reduce state space (will eventually default to 0). Here's the cases in which a self-hit is valid:
    # Can default to False to eliminate self-hits, and True to not eliminate anything
    def _useless_self_hit(self, battle, order: BattleOrder):

        # Eliminate easy conditions in which this is not a useless self hit
        if not order or not order.is_move(): return False
        if not (order.order.damage or order.order.base_power > 0): return False
        if order.order.self_switch: return False

        # If it's a self-hit
        affected_targets = BattleOrder.get_affected_targets(battle, order)
        if affected_targets and min(affected_targets) < 0:

            # Get the mon who is going to be hit
            target_mon = battle.active_pokemon[min(affected_targets)]

            # Only allow this as a potential move under these conditions
            if target_mon.item == 'weaknesspolicy' and order.order.type.damage_multiplier(*target_mon.types) >= 2: return True
            elif target_mon.ability == 'Berserk': return False
            elif target_mon.ability == 'Justified' and order.order.type == 'DARK': return False
            elif target_mon.ability == 'Water Absorb' and order.order.type == 'WATER': return False
            elif target_mon.ability == 'Volt Absorb' and order.order.type == 'ELECTRIC': return False
            elif target_mon.ability == 'Flash Fire' and order.order.type == 'FIRE': return False
            else: return True

        return False

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
