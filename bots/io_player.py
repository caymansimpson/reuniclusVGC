# -*- coding: utf-8 -*-
import sys
import random
import itertools
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.player.battle_order import DoubleBattleOrder, DefaultDoubleBattleOrder

from helpers.doubles_utils import *

class IOPlayer(Player):

    def choose_move(self, battle):
        mon1 = battle.active_pokemon[0].species if battle.active_pokemon[0] else "None"
        mon2 = battle.active_pokemon[1].species if battle.active_pokemon[1] else "None"

        print()
        print(f"Pokemon are: {mon1} and {mon2}")

        if battle.active_pokemon[0]: print("First mon's moves: " + ','.join(battle.active_pokemon[0].moves.keys()))
        else: print("First mon's moves: None")
        print("First mon's switches: " + str(battle.available_switches[0]))

        if battle.active_pokemon[1]: print("Second mon's moves: " + ','.join(battle.active_pokemon[1].moves.keys()))
        else: print("Second mon's moves: None")
        print("Second mon's switches: " + str(battle.available_switches[1]))

        order =  input("What order do you want to give?")
        return order

    # Just select the first 4 mons
    def teampreview(self, battle):
        return "/team 5634"
