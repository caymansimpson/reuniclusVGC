# -*- coding: utf-8 -*-
import asyncio
import sys
import random
from math import comb

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

# To run from command line, run this in the root directory: python3.8 simulators/test_dqn.py
def main():
    print("\033[92m Starting script... \033[0m")

    plyr = SimpleDQNPlayer(num_battles=10000, battle_format="gen8vgc2021", team=TeamRepository.teams['garchomp'])

    # Initialize and check out our model
    plyr.model.summary()

    random_opp = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
    max_opp = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['regirock'])

    # Train
    print("Training against random opponent 10,000 times...")
    plyr.train(random_opp, 10000)
    print("Training against max opponent 10,000 times...")
    plyr.train(max_opp, 10000)
    plyr.save_model()

    # Evaluate
    print("Results against random players:")
    plyr.evaluate_model(random_opp, 100)
    plyr.evaluate_model(max_opp, 100)

if __name__ == "__main__":
    main()
