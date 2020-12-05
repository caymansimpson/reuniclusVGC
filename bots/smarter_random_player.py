import sys
import random

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from helpers.doubles_utils import get_reasonable_moves

# Random Bot that doesn't self-hit
# TODO: need to handle case where mon has no available moves/switches left and needs to struggle
class SmarterRandomPlayer(Player):
    def choose_move(self, battle):

        # Get all possible moves. If there are none, return default
        possible_moves = get_reasonable_moves(battle)
        if len(possible_moves) == 0: return "/choose default,default"

        # Choose a random action, and order actions when a pokemon is fainted so that the only action goes first
        action1, action2 = random.choice(possible_moves)
        if action1 is None and action2 is None: return "/choose default,default"
        if battle.active_pokemon[0] is None: action1, action2 = action2, action1

        order = "/choose " + (action1.showdownify() if action1 is not None else "default")
        order += "," + (action2.showdownify() if action2 is not None else "default")

        # if battle.active_pokemon[0] is not None and battle.active_pokemon[1] is not None:
        #     print(str(action1) + "\t\t||\t\t" + str(action2))
        #     print(battle.active_pokemon[0].species + "," + battle.active_pokemon[1].species + "=> " + order)
        # elif battle.active_pokemon[0] is None:
        #     print(str(action1) + "\t\t||\t\t" + str(action2))
        #     print("None," + battle.active_pokemon[1].species + "=> " + order)
        # elif battle.active_pokemon[1] is None:
        #     print(str(action1) + "\t\t||\t\t" + str(action2))
        #     print(battle.active_pokemon[0].species + ",None=> " + order)

        return order

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
