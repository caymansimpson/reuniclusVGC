import sys
import random

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from helpers.doubles_utils import get_reasonable_moves

# Random Bot that doesn't self-hit
class SmarterRandomPlayer(Player):
    def choose_move(self, battle):

        # Get all possible moves. If there are none, return default
        possible_moves = get_reasonable_moves(battle)
        if len(possible_moves) == 0: return "/choose default,default"

        # Choose a random action, and order actions such that action1 always is not None
        action1, action2 = random.choice(possible_moves)
        if action1 is None and action2 is None: return "/choose default,default"
        if action1 is None: action2, action1 = action1, action2

        order = "/choose " + action1.showdownify()

        if action2 != None: order += "," + action2.showdownify()
        else: order += ",default"

        return order

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
