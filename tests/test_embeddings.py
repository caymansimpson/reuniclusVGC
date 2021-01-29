# -*- coding: utf-8 -*-
import asyncio
import sys
import random
from math import comb

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.player.random_player import RandomPlayer
from poke_env.player.player import Player
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from helpers.team_repo import TeamRepository
from poke_env.player.battle_order import DoubleBattleOrder, DefaultDoubleBattleOrder


class TempRandomPlayer(Player):
    _plyr = SimpleDQNPlayer()

    def choose_move(self, battle):
        orders = self.get_all_doubles_moves(battle)

        filtered_orders = list(filter(lambda x: DoubleBattleOrder.is_valid(battle, x), orders))
        if filtered_orders: order = random.choice(filtered_orders)
        else: order = DefaultDoubleBattleOrder()

        if battle.turn == 1:
            print()
            print("Len of Move Embeddings: ", len(self._plyr._embed_move(list(battle.active_pokemon[0].moves.values())[0])))
            print("Len of Mon Embeddings: ", len(self._plyr._embed_opp_mon(battle, battle.active_pokemon[0])))
            print("Len of Opponent Mon Embeddings: ", len(self._plyr._embed_opp_mon(battle, battle.opponent_active_pokemon[0])))
            print("Len of Battle Embeddings: ", len(self._plyr.embed_battle(battle)))

        return order

    def teampreview(self, battle):

        # We use 1-6 because  showdown's indexes start from 1
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))


# To run from command line, run this in the root directory: python3.8 simulators/simulate_random_doubles.py
async def main():
    print("\033[92m Starting script... \033[0m")

    # We create players:
    players = [
      RandomDoublesPlayer(max_concurrent_battles=1, battle_format='gen8vgc2021', team=TeamRepository.teams['mamoswine']),
      TempRandomPlayer(max_concurrent_battles=1, battle_format='gen8vgc2021', team=TeamRepository.teams['spectrier']),
    ]

    # Each player plays n times against eac other
    n = 10

    # Pit players against each other
    print("About to start " + str(n*sum(i for i in range(0, len(players)))) + " battles...")
    cross_evaluation = await cross_evaluate(players, n_challenges=n)

    # Defines a header for displaying results
    table = [["-"] + [p.username for p in players]]

    # Adds one line per player with corresponding results
    for p_1, results in cross_evaluation.items():
        table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])

    # Displays results in a nicely formatted table.
    print(tabulate(table))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
