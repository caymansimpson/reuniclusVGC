# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import json
from math import comb
from poke_env.environment.move import Move


sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

from poke_env.environment.field import Field
from poke_env.environment.side_condition import SideCondition
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle

from helpers.doubles_utils import *

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

def embed_move(move):

    # If the move is None or empty, return a negative array (filled w/ -1's)
    if move is None or move.is_empty: return [-1]*172

    embeddings = []

    embeddings.append([
        move.accuracy,
        move.base_power,
        int(move.breaks_protect),
        move.crit_ratio,
        move.current_pp,
        move.damage,
        move.drain,
        move.expected_hits,
        int(move.force_switch),
        move.heal,
        int(move.ignore_ability),
        int(move.ignore_defensive),
        int(move.ignore_evasion),
        1 if move.ignore_immunity else 0,
        move.n_hit[0] if move.n_hit else 1, # minimum times the move hits
        move.n_hit[1] if move.n_hit else 1, # maximum times the move hits
        move.priority,
        move.recoil,
        int(move.self_destruct is not None),
        int(move.self_switch is not None),
        int(move.steals_boosts),
        int(move.thaws_target),
        int(move.use_target_offensive),
    ])

    # Add Category
    embeddings.append([1 if move.category == category else 0 for category in MoveCategory._member_map_.values()])

    # Add Defensive Category
    embeddings.append([1 if move.defensive_category == category else 0 for category in MoveCategory._member_map_.values()])

    # Add Move Type
    embeddings.append([1 if move.type == pokemon_type else 0 for pokemon_type in PokemonType._member_map_.values()])

    # Add Fields (bad coding -- assumes field name will be move name, and uses string manipulation)
    embeddings.append([1 if field.name.lower().replace("_", "") == move.id else 0 for field in Field._member_map_.values()])

    # Add Side Conditions (bad coding -- assumes field name will be move name, and uses string manipulation)
    embeddings.append([1 if sc.name.lower().replace("_", "") == move.id else 0 for sc in SideCondition._member_map_.values()])

    # Add Weathers (bad coding -- assumes field name will be move name, and uses string manipulation)
    embeddings.append([1 if weather.name.lower().replace("_", "") == move.id else 0 for weather in Weather._member_map_.values()])

    # Add Targeting Types (from double_utils.py); cardinality is 14
    embeddings.append([1 if tt.name.lower().replace("_", "") == move.deduced_target else 0 for tt in TargetType._member_map_.values()])

    # Add Volatility Statuses (from double_utils.py); cardinality is 57
    volatility_status_embeddings = []
    for vs in VolatileStatus._member_map_.values():
        if vs.name.lower().replace("_", "") == move.volatile_status: volatility_status_embeddings.append(1)
        elif vs.name.lower().replace("_", "") in list(map(lambda x: x.get('volatilityStatus', ''), move.secondary)): volatility_status_embeddings.append(1)
        else: volatility_status_embeddings.append(0)
    embeddings.append(volatility_status_embeddings)

    # Add Statuses
    status_embeddings = []
    for status in Status._member_map_.values():
        if status.name.lower().replace("_", "") == move.status: status_embeddings.append(1)
        elif status.name.lower().replace("_", "") in list(map(lambda x: x.get('status', ''), move.secondary)): status_embeddings.append(1)
        else: status_embeddings.append(0)
    embeddings.append(status_embeddings)

    # Add Boosts
    boost_embeddings = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'evasion': 0, 'accuracy': 0}
    if move.boosts:
        for stat in move.boosts: boost_embeddings[stat] += move.boosts[stat]
    elif move.secondary:
        for x in move.secondary:
            for stat in x.get('boosts', {}): boost_embeddings[stat] += x['boosts'][stat]
    embeddings.append(boost_embeddings.values())

    # Add Self-Boosts; meteormash, scaleshot, dragondance
    self_boost_embeddings = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'evasion': 0, 'accuracy': 0}
    if move.self_boost:
        for stat in move.self_boost: self_boost_embeddings[stat] += move.self_boost[stat]
    elif move.secondary:
        for x in move.secondary:
            for stat in x.get('self', {}).get('boosts', {}): self_boost_embeddings[stat] += x['self']['boosts'][stat]
    embeddings.append(self_boost_embeddings.values())

    # Introduce the chance of a secondary effect happening
    chance = 0
    for x in move.secondary:
        chance = max(chance, x.get('chance', 0))
    embeddings.append([chance])

    to_return = [item for sublist in embeddings for item in sublist]
    return to_return

# To run from command line, run this in the root directory: python3.8 simulators/test_dqn.py
def main():
    print("\033[92m Starting script... \033[0m")
    print(len(embed_move(Move('genesissupernova'))))


    with open('/Users/cayman/Library/Python/3.8/lib/python/site-packages/poke_env/data/moves.json') as f:
        moves = json.load(f)
        for move_id in moves:
            try:
                embedding = embed_move(Move(move_id))
                print(move_id, len(embedding))
            except Exception as e:
                print(move_id)
                print(Move(move_id))
                print(e)
                print()


if __name__ == "__main__":
    main()
