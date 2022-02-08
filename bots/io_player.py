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
from poke_env.environment.double_battle import DoubleBattle

from helpers.doubles_utils import *
from poke_env.utils import active_pokemon_to_showdown_target

class IOPlayer(Player):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._DEFAULT_ORDER = "default"

        print("====================== Welcome to IOPlayer ======================")
        print("With this player, you will be able to input moves via the terminal")
        print("which will allow you to interact with your bot.")
        print()
        print("Moves will be inputed in the following way. For each pokemon, you")
        print("will get a prompt, with listed moves. You should choose whether")
        print("you want to switch, or attack (and whom). For example, a command")
        print("for Furret would be \"switch Linoone\" which would switch your")
        print("Furret for a Linoone, even though Linoone is an inferior mon on")
        print("all accounts. Alternatively, you can attack via \"move doubleedge")
        print("Linoone\" (since we want to attack all Linoones. You could also do")
        print("\"move doubleedge 1\" if you know the pokemon's index. Spread moves")
        print("or moves without targets will ignore a target.")
        print()
        print("Also, if you want to dynamax or mega-evolve (and it's allowed),")
        print("you can append \"dynamax\", \"z_move\" or \"mega\" to the end of")
        print("the order. So for example: \"\"fissure Linoone mega\"")
        print()
        print("Lastly, we won't validate the validity of your moves. So if you")
        print("switch to the same mon or don't enter a target when you should,")
        print("then the engine will reprompt your turn, even if we don't catch")
        print("the error before then.")
        print()
        print("Happy playing!")

    def choose_move(self, battle):
        mon1 = battle.active_pokemon[0].species if battle.active_pokemon[0] else "None"
        mon2 = battle.active_pokemon[1].species if battle.active_pokemon[1] else "None"

        print()
        print(f'\033[95mTurn Number {battle.turn} starting!\033[0m')
        print(f"The battle can be found at http://localhost.psim.us/battle-{battle.format}-{battle.battle_tag}")
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

        m0 = self._promptOrder(battle, 0)
        m1 = self._promptOrder(battle, 1)

        return DoubleBattleOrder(
            first_order = self._convertPartialMessage(battle, m0, 0),
            second_order = self._convertPartialMessage(battle, m1, 1),
        )

    # Where we prompt and validate the order given to each individual pokemon. Runs a check on whether the order
    # is valid, and will reprompt the user if the order is not valid.
    def _promptOrder(self, battle, index):
        # No order to give since there's no mon in this position; we return defualt
        if not battle.active_pokemon[index]: return self._DEFAULT_ORDER

        # Prompt the order
        msg = input(f"\033[93mWhat order do you want to give {battle.active_pokemon[index].species}?\033[0m ").strip().lower()

        # Put the user in a loop if the message doesnt pass validation until they do
        while(not self._isValidOrder(msg, battle, index)):
            err = self._guessError(msg, battle, index)
            print(f"\033[91mError: Not Valid Order. Possible reason: {err}?\033[0m")
            msg = input(f"\033[93mWhat order do you want to give {battle.active_pokemon[index].species}?\033[0m ")

        return msg

    # Checks whether the order inputted for a single mon is correct
    def _isValidOrder(self, msg, battle, index):
        if msg == self._DEFAULT_ORDER: return True

        # if switch is valid, we're good
        elif msg.startswith("switch"):
            switch_target = msg.replace("switch", "").strip()
            return switch_target in map(lambda x: x.species, battle.available_switches[index])

        # Check if the move is valid, that it the target set is on the field, and also that there's no weird appendices
        elif msg.startswith("move"):
            move_msg = msg.replace("move", "").strip()
            tokens = move_msg.split(" ")
            if tokens[0] not in battle.active_pokemon[index].moves.keys(): return False

            possible_tokens = [
                battle.opponent_active_pokemon[0].species,
                battle.opponent_active_pokemon[1].species,
                battle.active_pokemon[1 - index].species,
                "mega",
                "dynamax",
                "z_move",
                "0",
                "1"
            ]
            return all(map(lambda x: x in possible_tokens, tokens[1:]))

        # If you don't have "switch", "defualt", or "move" in the msg, then it's bad
        else:
            return False

    # Heuristic to guess where the user went wrong. Assumes that the msg parameter has not passed _isValidOrder()
    def _guessError(self, msg, battle, index):
        if "switch" not in msg and "move" not in msg:
            return "You did not specify whether the move should be a \"switch\" or a \"move\". Orders need to start with either"
        elif msg.startswith("switch"):
            return "You did not give a valid switch option - typo"
        elif msg.startswith("move"):
            move_msg = msg.replace("move", "").strip()
            tokens = move_msg.split(" ")
            if tokens[0] not in battle.active_pokemon[index].moves.keys(): return "You did not give a valid move"
            else: return "you had a space and the token after the space isn't \"dynamax\", \"mega\" or a valid target"
        else:
            return "no idea"


    def _convertPartialMessage(self, battle, msg, index):
        if msg == self._DEFAULT_ORDER: return DefaultBattleOrder()

        order, target, mega, dynamax, z_move = None, None, False, False, False
        if 'switch' in msg:
            order = Pokemon(species=re.search("switch\s([a-zA-Z\-\_0-9]+).*", msg).group(1).lower())
        elif 'move' in msg:
            tokens = msg.split(" ")
            order = Move(tokens[1])

            if len(tokens) <= 2: target = DoubleBattle.EMPTY_TARGET_POSITION
            else:
                target = tokens[2]
                if target.strip().isdigit(): target = int(target)
                elif battle.opponent_active_pokemon[0].species == target.strip(): target = active_pokemon_to_showdown_target(0, opp=True)
                elif battle.opponent_active_pokemon[1].species == target.strip(): target = active_pokemon_to_showdown_target(1, opp=True)
                elif battle.active_pokemon[1 - index].species == target.strip(): target = active_pokemon_to_showdown_target(1 - index, opp=False)

        if ' mega' in msg: mega = True
        if 'dynamax' in msg: dynamax = True
        if 'z_move' in msg: z_move = True

        return BattleOrder(order, move_target=target, actor=battle.active_pokemon[index], mega=mega, dynamax=dynamax, z_move=z_move)

    # Just select the first 4 mons
    def teampreview(self, battle):
        return "/team 1234"
