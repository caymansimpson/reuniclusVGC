import sys
import random
import itertools
import re

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from helpers.doubles_utils import *

# Random Bot that doesn't self-hit
class SmarterRandomPlayer(Player):
    def choose_move(self, battle):

        # If we're not being forced to switch and are choosing our moves
        if not any(battle.force_switch):

            # Go through and get actions, filter them down to what's possible, and then eliminate ones that dont make sense
            first_moves = get_possible_moves(battle, battle.active_pokemon[0])
            second_moves = get_possible_moves(battle, battle.active_pokemon[1])

            all_possible_moves = itertools.product(first_moves, second_moves)
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
            reasonable_moves = filter_to_reasonable_moves(battle, filtered_moves)

            action1, action2 = Action(), Action()
            if len(reasonable_moves) > 0: action1, action2 = random.choice(reasonable_moves)
            elif len(filtered_moves) > 0: action1, action2 = random.choice(filtered_moves)

            # Choose a random action, and order actions when a pokemon is fainted so that the only action goes first
            if battle.active_pokemon[0] is None: action1, action2 = action2, action1

            order = "/choose " + action1.showdownify() + "," + action2.showdownify()

        # Force Switch situation
        else:
            moves = get_possible_moves(battle, battle.active_pokemon[0 if battle.force_switch[0] else 1])
            all_possible_moves = itertools.product(moves, [Action()])
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
            action1, _ = random.choice(filtered_moves)
            order = "/choose " + action1.showdownify()

        return order

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
