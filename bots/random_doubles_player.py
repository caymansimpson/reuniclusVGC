from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.player.battle_order import DoubleBattleOrder, DefaultDoubleBattleOrder
import random
import itertools
import sys

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from helpers.doubles_utils import *

class RandomDoublesPlayer(Player):

    def choose_move(self, battle):
        orders = self.get_all_doubles_moves(battle)

        filtered_orders = list(filter(lambda x: DoubleBattleOrder.is_valid(battle, x), orders))
        if filtered_orders: order = random.choice(filtered_orders)
        else: order = DefaultDoubleBattleOrder()

        return order

    def teampreview(self, battle):

        # We use 1-6 because  showdown's indexes start from 1
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
