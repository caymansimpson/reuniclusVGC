# -*- coding: utf-8 -*-
import asyncio
import sys
import random

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.io_player import IOPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

# To run from command line, run this in the root directory: python3.8 simulators/simulate_random_doubles.py
async def main():
    print("\033[92m Starting script... \033[0m")

    # We create players:
    players = [
      IOPlayer(max_concurrent_battles=1, battle_format="gen8vgc2021", team=TeamRepository.teams['swampert']),
      RandomDoublesPlayer(max_concurrent_battles=1, battle_format="gen8vgc2021", team=TeamRepository.teams['garchomp']),
    ]

    # Each player plays n times against each other
    n = 1

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
