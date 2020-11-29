# -*- coding: utf-8 -*-
import asyncio
import sys
import random

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from helpers.team_repo import TeamRepository

# TODO: examine why we get this error:
# 2020-11-29 01:59:42,142 - SmarterRandomPlayer 1 - WARNING - Error message received: |error|[Invalid choice] Can't move: Your Zapdos doesn't have a move matching nastyplot
async def main():
    # We create players:
    players = [
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=TeamRepository.teams[0]),
      SmarterRandomPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=TeamRepository.teams[1]),
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=TeamRepository.teams[1]),
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=TeamRepository.teams[2]),
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=TeamRepository.teams[3])
    ]

    # Now, we can cross evaluate them: every player will player 30 games against every
    # other player.
    cross_evaluation = await cross_evaluate(players, n_challenges=50)

    # Defines a header for displaying results
    table = [["-"] + [p.username for p in players]]

    # Adds one line per player with corresponding results
    for p_1, results in cross_evaluation.items():
        table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])

    # Displays results in a nicely formatted table.
    print(tabulate(table))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
