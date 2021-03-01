from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
from poke_env.player.battle_order import DoubleBattleOrder
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.field import Field
from poke_env.environment.status import Status
from poke_env.environment.side_condition import SideCondition
from enum import Enum, unique, auto

from typing import Optional
import random
import numpy as np
import itertools
import tensorflow as tf

# Given a boost level, returns the modifier
def statMod(statStage):
    if statStage == 0: multiplier = 1
    elif statStage == 1: multiplier = 1.5
    elif statStage == -1: multiplier = 2.0/3
    elif statStage == 2: multiplier = 2
    elif statStage == -2: multiplier = 1.0/2
    elif statStage == 3: multiplier = 2.5
    elif statStage == -3: multiplier = 0.4
    elif statStage == 4: multiplier = 3
    elif statStage == -4: multiplier = 1.0/3
    elif statStage == 5: multiplier = 3.5
    elif statStage == -5: multiplier = 2.0/7
    elif statStage == 6: multiplier = 4
    elif statStage == -6: multiplier = 1.0/4
    return multiplier

# We evaluate the performance on mon1 against mon2 by its type advantage
# We return how much better you can perform
def compute_type_advantage(mon1, mon2):

    a_on_b = b_on_a = -np.inf

    # Store the max damage multiplier that the mon can do
    for type_ in mon1.types:
        if type_: a_on_b = max(a_on_b, type_.damage_multiplier(*mon2.types))

    # Do the other way around
    for type_ in mon2.types:
        if type_: b_on_a = max(b_on_a, type_.damage_multiplier(*mon1.types))

    # Our performance metric is the difference between the two
    return a_on_b - b_on_a

# We compute the speed of a pokemon, based on the battle conditions, the mon itself and
# whether it is an opponent mon. Does not take into account unburden
# TODO: test
def compute_effective_speed(battle, mon):
    speed = mon.stats['spe']

    # Abilities
    if battle.weather:
        if mon.ability == 'Slush Rush' and battle.weather.name == 'HAIL': speed *= 2
        elif mon.ability == 'Sand Rush' and battle.weather.name == 'SANDSTORM': speed *= 2
        elif mon.ability == 'Chlorophyll' and battle.weather.name in  ['SUNNYDAY', 'DESOLATELAND']: speed *= 2
        elif mon.ability == 'Swift Swim' and battle.weather.name in ['RAINDANCE', 'PRIMORDIALSEA']: speed *= 2
        elif mon.ability == 'Surge Surfer' and Field.ELECTRIC_TERRAIN in battle.fields: speed *= 2 # Field(1) corresponds to Electric Terrain

    # Incorporate boosts
    speed *= statMod(mon.boosts['spe'])

    # Incorporate status (Paralysis) if the mon doesnt have quickfeed
    if mon.ability == 'Quick Feet' and not mon.status: speed *= 1.5
    elif mon.status and mon.status == Status.PAR: speed *= .5 # Status(4) corresponds to paralysis

    # Held Items (choice scarf, iron ball)
    if mon.item == 'ironball': speed *= .5
    elif mon.item == 'choicescarf': speed *= 1.5

    # Side Conditions
    if SideCondition.GRASS_PLEDGE in battle.side_conditions: speed *= .25 # GRASS_PLEDGE, or creating a swamp
    elif SideCondition.TAILWIND in battle.side_conditions: speed *= 2 # TAILWIND

    return speed

# We compute the speed of an opponent pokemon in the worst case scenario
# TODO: test
def compute_worst_case_scenario_speed(battle, mon):
    tr = Field.TRICK_ROOM in battle.fields

    # Use stat equation
    speed = (2*mon.base_stats['spe'] + 31 + 252/4)*mon.level/100 + 5

    # Natures modification
    speed *= .9 if tr else 1.1

    # Abilities; assuming that a mon would use their speed abilities
    if battle.weather:
        if 'Slush Rush' in mon.possible_abilities and battle.weather.name == 'HAIL': speed *= 2
        elif 'Sand Rush' in mon.possible_abilities and battle.weather.name == 'SANDSTORM': speed *= 2
        elif 'Chlorophyll' in mon.possible_abilities and battle.weather.name in  ['SUNNYDAY', 'DESOLATELAND']: speed *= 2
        elif 'Swift Swim' in mon.possible_abilities and battle.weather.name in ['RAINDANCE', 'PRIMORDIALSEA']: speed *= 2
        elif 'Surge Surfer' in mon.possible_abilities  and Field.ELECTRIC_TERRAIN in battle.fields: speed *= 2 # Field(1) corresponds to Electric Terrain

    # Incorporate boosts
    speed *= statMod(mon.boosts['spe'])

    # Incorporate status (Paralysis) if the mon doesnt have quickfeed
    if mon.ability == 'Quick Feet' and not mon.status: speed *= 1.5
    elif mon.status == Status.PAR: speed *= .5 # Status(4) corresponds to paralysis

    # We don't take into account Held Items (choice scarf, iron ball) because it would make this reward useless
    # in situations where they aren't available. Eventually, we need to run code to use all battle cues (hail, sandstorm, mon order)
    # to guess speed number ranges
    # if mon.item == 'ironball': speed *= .5
    # elif mon.item == 'choicescarf': speed *= 1.5

    # Side Conditions
    if SideCondition.GRASS_PLEDGE in battle.side_conditions: speed *= .25 # GRASS_PLEDGE, or creating a swamp
    elif SideCondition.TAILWIND in battle.side_conditions: speed *= 2 # TAILWIND

    return speed

def battle_debug(battle):
    print()
    print("=============== Battle Debug =================")
    print("My mons: ", battle.active_pokemon)
    print("Can Dynamax: ", battle.can_dynamax)
    print("Force Switch: ", battle.force_switch)

    for i, mon in enumerate(battle.active_pokemon):
        print(f"{i}th mon's moves:", ', '.join(map(lambda x: x.id, battle.available_moves[i])))

    for i, mon in enumerate(battle.active_pokemon):
        print(f"{i}th mon's available switches:", ', '.join(map(lambda x: x.species, battle.available_switches[i])))

    print("Opp mons:", battle.opponent_active_pokemon)

    print("Side Conditions:", battle.side_conditions)
    print("Fields:         ", battle.fields)
    print("Weather:        ", battle.weather)
    print("=================== End =====================")
    print()

# Record progress of wins for keras models
class WinRatioCallback(tf.keras.callbacks.Callback):

    def __init__(self, player, dqn):
        self.player = player
        self.dqn = dqn
        self.max_player = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
        self.rand_player = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])

    def on_epoch_end(self, epoch, logs=None):

        if epoch % 2000 != 0: return
        num_battles = 100

        self.player.play_against(env_algorithm=dqn_evaluation, opponent=self.max_player, env_algorithm_kwargs={"dqn": self.dqn, "nb_episodes": num_battles})
        wandb.log({'epoch': epoch, 'pct_wins_against_max': self.player.n_won_battles*1./num_battles})

        self.player.play_against(env_algorithm=dqn_evaluation, opponent=self.rand_player, env_algorithm_kwargs={"dqn": dqn, "nb_episodes": num_battles})
        wandb.log({'epoch': epoch, 'pct_wins_against_rand': self.player.n_won_battles*1./num_battles})
