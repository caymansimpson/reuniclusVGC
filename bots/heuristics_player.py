import numpy as np
import sys
import random
from typing import Dict, List, Optional

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.environment.field import Field
from poke_env.environment.side_condition import SideCondition
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.target_type import TargetType
from poke_env.environment.volatile_status import VolatileStatus
from poke_env.environment.battle import Battle
from bots.random_doubles_player import RandomDoublesPlayer

from poke_env.player.battle_order import DoubleBattleOrder, DefaultBattleOrder, BattleOrder, DefaultDoubleBattleOrder

from helpers.doubles_utils import *

""" ============== Creating a player that moves based on Heuristics ==============
Possible options:
- Optimize for my mons move first
- Optimize for the least damage taken (e.g. if another mon moves first, assume worst case scenario)
- Optimize for KOs
- Optimize for sweeps
- Assume worst-case scenario pokemon is brought as a counter, and update when this isnt the case
"""
class HeuristicsPlayer(Player):

    def choose_move(self, battle):
        return '/choose default'

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
