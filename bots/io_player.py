# -*- coding: utf-8 -*-
import sys
import random
import itertools
import re

sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.player.battle_order import DoubleBattleOrder, DefaultBattleOrder, BattleOrder

from helpers.doubles_utils import *
from poke_env.utils import active_pokemon_to_showdown_target

class IOPlayer(Player):

    # TODO: give examples of how to give orders
    # TODO: support error messaging, helfpul hints and reprompting

    def choose_move(self, battle):
        mon1 = battle.active_pokemon[0].species if battle.active_pokemon[0] else "None"
        mon2 = battle.active_pokemon[1].species if battle.active_pokemon[1] else "None"

        print()
        print(f'\033[95mTurn Number {battle.turn} starting!\033[0m')
        print(f"Pokemon are: {mon1} and {mon2}")
        print(f"Opponents Mons are: {battle.opponent_active_pokemon[0].species} and {battle.opponent_active_pokemon[1].species}")
        print()

        if battle.active_pokemon[0]: print(f"{mon1}'s moves: " + ', '.join(battle.active_pokemon[0].moves.keys()))
        else: print("First mon's moves: None")
        print("First mon's switches: " + ', '.join(map(lambda x: x.species, battle.available_switches[0])))
        print()

        if battle.active_pokemon[1]: print(f"{mon2}'s moves: " + ', '.join(battle.active_pokemon[1].moves.keys()))
        else: print("Second mon's moves: None")
        print("Second mon's switches: " + ', '.join(map(lambda x: x.species, battle.available_switches[1])))
        print()

        message = input("\033[93mWhat order do you want to give?\033[0m\n\t")

        #try:
        message = message.replace('/choose', '')
        order_messages = list(map(lambda x: x.strip(), message.split(',')))

        # Get First Order
        return DoubleBattleOrder(
            first_order = self._convertPartialMessage(battle, order_messages[0], 0),
            second_order = self._convertPartialMessage(battle, order_messages[1], 1),
        )

    def _convertPartialMessage(self, battle, msg, index):
        if 'default' in msg: return DefaultBattleOrder()

        order, target, mega, dynamax, z_move = None, None, False, False, False
        if 'switch' in msg:
            order = Pokemon(species=re.search("switch\s([a-zA-Z\-\_0-9]+).*", msg).group(1).lower())
        elif 'move' in msg:
            matches = re.search("move\s([a-zA-Z\-\_0-9]+)\s?([a-zA-Z\-\_0-9])?.*", msg)
            order = Move(matches.group(1).lower())

            target = matches.group(2).strip()
            if target.isdigit(): target = int(target)
            elif battle.opponent_active_pokemon[0].species == target: target = active_pokemon_to_showdown_target(0, opp=True)
            elif battle.opponent_active_pokemon[1].species == target: target = active_pokemon_to_showdown_target(1, opp=True)
            elif battle.active_pokemon[1 - index].species == target: target = active_pokemon_to_showdown_target(1 - index, opp=False)

        if 'mega' in msg: mega = True
        if 'dynamax' in msg: dynamax = True
        if 'z_move' in msg: z_move = True

        return BattleOrder(order, move_target=target, actor=battle.active_pokemon[index], mega=mega, dynamax=dynamax, z_move=z_move)

    # Just select the first 4 mons
    def teampreview(self, battle):
        return "/team 1234"
