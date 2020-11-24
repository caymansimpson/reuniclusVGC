# -*- coding: utf-8 -*-
"""
This is a Random Bot, created by example from https://poke-env.readthedocs.io/en/stable/cross_evaluate_random_players.html#cross-evaluate-random-players
File: https://github.com/hsahovic/poke-env/blob/master/examples/cross_evaluate_random_players.py

It is meant to interact with Pokemon Showdown, and in poke-env
"""
import asyncio

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate


# By default, players play the gen8randombattle format. You can specify another battle format by passing a battle_format parameter.
# If you choose to play a format that requires teams, you’ll also need to define it with the team parameter.
# You can refer to Adapting the max player to gen 8 OU and managing team preview for an example using a custom team and format.
# -*- coding: utf-8 -*-
async def main():
    # We create three random players
    players = [RandomPlayer(max_concurrent_battles=10) for _ in range(3)]

    # Now, we can cross evaluate them: every player will player 20 games against every
    # other player.
    cross_evaluation = await cross_evaluate(players, n_challenges=20)

    # Defines a header for displaying results
    table = [["-"] + [p.username for p in players]]

    # Adds one line per player with corresponding results
    for p_1, results in cross_evaluation.items():
        table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])

    # Displays results in a nicely formatted table.
    print(tabulate(table))


if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(main())
