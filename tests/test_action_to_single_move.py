# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import json


sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.environment.move import Move
from poke_env.environment.field import Field
from poke_env.environment.side_condition import SideCondition
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle
from poke_env.environment.double_battle import DoubleBattle
from poke_env.player.battle_order import DoubleBattleOrder, DefaultBattleOrder, BattleOrder, DefaultDoubleBattleOrder


from helpers.doubles_utils import *

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

class DummyDoublesPlayer(RandomDoublesPlayer):
    first = True
    distinct = set()
    null = 0

    # Basically, on the first move, take the existing battle state and go through all possible inputs for _action_to_move
    # and print out the mapping between the action (int) and the output (DoubleBattleOrder) to verify the output's correctness
    def choose_move(self, battle):
        if not self.first: return '/choose default'

        plyr = SimpleDQNPlayer()
        for i in range(676):
            print('=== i:', i, '===')
            action = plyr._action_to_move(i, battle)
            print('Returned Move:', action.message if action else "None")
            if not isinstance(action, DefaultDoubleBattleOrder): self.distinct.add(str(action))
            else: self.null += 1

            print()

        self.first = False
        battle_debug(battle)

        return '/choose default'

async def main():
    print("\033[92m Starting script... \033[0m")

    # We create players:
    players = [
      DummyDoublesPlayer(max_concurrent_battles=1, battle_format="gen8vgc2021", team=TeamRepository.teams['sample']),
      RandomDoublesPlayer(max_concurrent_battles=1, battle_format="gen8vgc2021", team=TeamRepository.teams['sample']),
    ]
    cross_evaluation = await cross_evaluate(players, n_challenges=1)

    print("Number of distinct actions returned:", len(players[0].distinct))
    print("Number of illegal actions returned:", players[0].null)
    print("Expected number of distinct actions returned: 418 (see ../README.md for how to get this number)")
    if len(players[0].distinct) + players[0].null < 676:
      print("Distinct Actions + Illegal Actions should equal 676 and we got ", len(players[0].distinct) + players[0].null, "- we returned the same legal actino twice")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
