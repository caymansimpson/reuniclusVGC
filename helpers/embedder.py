import sys
from typing import Dict, List, Optional


sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from poke_env.data import GEN_TO_MOVES, GEN_TO_POKEDEX
from poke_env.environment.field import Field
from poke_env.environment.side_condition import SideCondition
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.target_type import TargetType
from poke_env.environment.volatile_status import VolatileStatus
from poke_env.environment.battle import Battle
from poke_env.player.battle_order import *
from helpers.doubles_utils import *

class Embedder():

    def __init__(self, gen=8):

        # Store all possible game-related knowledge, so that we can can embed battle states. The tuples are
        # key where we retrieve the classes, the class, and whether poke_env supports returning the class (as opposed to string)
        self._knowledge = {}
        sets = [
            ('Field', Field, False),
            ('SideCondition', SideCondition, False),
            ('Status', Status, True),
            ('Weather', Weather, True),
            ('PokemonType', PokemonType, True),
            ('MoveCategory', MoveCategory, True),
            ('TargetType', TargetType, False),
            ('VolatileStatus', VolatileStatus, False),
        ]

        for key, klass, supported in sets:
            if supported: self._knowledge[key] =  list(klass._member_map_.values())
            else: self._knowledge[key] = list(map(lambda x: x.name.lower().replace("_", ""), list(klass._member_map_.values())))

        self._knowledge['Move'] = list(GEN_TO_MOVES[gen].keys())
        self._knowledge['Pokemon'] = list(GEN_TO_POKEDEX[gen].keys())

        # These are the lengths of the embeddings of each function. TODO: depends on the generation
        self.MOVE_LEN = 177
        self.MON_LEN = 100
        self.OPP_MON_LEN = 50
        self.BATTLE_LEN = 100

    # Returns an array of an embedded move; could be precomputed
    def embed_move(self, move):
        # If the move is None or empty, return a negative array (filled w/ -1's)
        if move is None or move.is_empty: return [-1]*self.MOVE_LEN

        embeddings = []

        # OHE Move, Category, Defensive Category, Move Type
        embeddings.append([1 if move.id == m else 0 for m in self._knowledge['Move']])
        embeddings.append([1 if move.category == category else 0 for category in self._knowledge['MoveCategory']])
        embeddings.append([1 if move.defensive_category == category else 0 for category in self._knowledge['MoveCategory']])
        embeddings.append([1 if move.type == pokemon_type else 0 for pokemon_type in self._knowledge['PokemonType']])

        # OHE Fields, SC, Weather (bad coding -- assumes field name will be move name, and uses string manipulation)
        embeddings.append([1 if move.id == field else 0 for field in self._knowledge['Field']])
        embeddings.append([1 if move.side_condition == sc else 0 for sc in self._knowledge['SideCondition']])
        embeddings.append([1 if move.weather == weather else 0 for weather in self._knowledge['Weather']])

        # OHE Targeting Types
        embeddings.append([1 if move.deduced_target and move.deduced_target.lower() == tt else 0 for tt in self._knowledge['TargetType']])

        # OHE Volatility Statuses
        volatility_status_embeddings = []
        for vs in self._knowledge['VolatileStatus']:
            if vs == move.volatile_status: volatility_status_embeddings.append(1)
            elif move.secondary and vs in list(map(lambda x: x.get('volatilityStatus', '').lower(), move.secondary)): volatility_status_embeddings.append(1)
            else: volatility_status_embeddings.append(0)
        embeddings.append(volatility_status_embeddings)

        # OHE Statuses
        status_embeddings = []
        for status in self._knowledge['Status']:
            if status == move.status: status_embeddings.append(1)
            elif move.secondary and status in list(map(lambda x: x.get('status', ''), move.secondary)): status_embeddings.append(1)
            else: status_embeddings.append(0)
        embeddings.append(status_embeddings)

        # OHE Boosts (which sometimes are self-boosts)
        boost_embeddings = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'evasion': 0, 'accuracy': 0}
        if move.boosts:
            for stat in move.boosts: boost_embeddings[stat] += move.boosts[stat]
        elif move.secondary:
            for x in move.secondary:
                for stat in x.get('boosts', {}): boost_embeddings[stat] += x['boosts'][stat]
        embeddings.append(boost_embeddings.values())

        # Add Self-Boosts
        self_boost_embeddings = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'evasion': 0, 'accuracy': 0}
        if move.self_boost:
            for stat in move.self_boost: self_boost_embeddings[stat] += move.self_boost[stat]
        elif move.secondary:
            for x in move.secondary:
                for stat in x.get('self', {}).get('boosts', {}): self_boost_embeddings[stat] += x['self']['boosts'][stat]
        embeddings.append(self_boost_embeddings.values())

        # Introduce the chance of a secondary effect happening
        chance = 0
        for x in move.secondary:
            chance = max(chance, x.get('chance', 0))
        embeddings.append([chance])

        # Encode other properties
        embeddings.append([
            move.accuracy,
            move.base_power,
            int(move.breaks_protect),
            move.crit_ratio,
            move.current_pp,
            move.damage,
            move.drain,
            move.expected_hits,
            int(move.force_switch),
            move.heal,
            int(move.ignore_ability),
            int(move.ignore_defensive),
            int(move.ignore_evasion),
            1 if move.ignore_immunity else 0,
            move.n_hit[0] if move.n_hit else 1, # minimum times the move hits
            move.n_hit[1] if move.n_hit else 1, # maximum times the move hits
            move.priority,
            move.recoil,
            int(move.self_destruct is not None),
            int(move.self_switch is not None),
            int(move.steals_boosts),
            int(move.thaws_target),
            int(move.use_target_offensive),
        ])

        # Flatten the arrays
        return [item for sublist in embeddings for item in sublist]

    def embed_mon(self, mon):
        return []

    def embed_opp_mon(self, mon):
        return []

    def embed_battle(self, mon):
        return []

"""
    # Embeds a move in a 178-dimensional array. This includes a move's accuracy, base_power, whether it breaks protect, crit ratio, pp,
    # damage, drain %, expected # of hits, whether it forces a switch, how much it heals, whether it ignores abilities/defenses/evasion/immunity
    # min times it can hit, max times it can hit its priority bracket, how much recoil it causes, whether it self destructs, whether it causes you to switch/steal boosts/thaw target/
    # uses targets offense, the moves offensive category (ohe: 3), defensive category (ohe: 3), type (ohe: ), fields (ohe: ), side conditions (ohe: ), weathers (ohe: ), targeting types (ohe: 14), volatility status (ohe: 57),
    # status (ohe: ), boosts (ohe: 6), self-boosts (ohe: 6) and the chance of a secondary effect
    def _embed_move(self, move):


    # We encode the opponent's mon in a 779-dimensional embedding
    # We encode all the mons moves, whether it is active, it's current hp, whether it's fainted, its level, weight, whether it's recharging, preparing, dynamaxed,
    # its stats, boosts, status, types and whether it's trapped or forced to switch out.
    # We currently don't encode its item, abilities (271) or its species (1155) because of the large cardinalities
    def _embed_mon(self, battle, mon):
        embeddings = []

        # Append moves to embedding (and account for the fact that the mon might have <4 moves)
        for move in (list(mon.moves.values()) + [None, None, None, None])[:4]:
            embeddings.append(self._embed_move(move))

        # Add whether the mon is active, the current hp, whether its fainted, its level, its weight and whether its recharging or preparing
        embeddings.append([
            int(mon.active),
            mon.current_hp,
            int(mon.fainted),
            mon.level,
            mon.weight,
            int(mon.must_recharge),
            1 if mon.preparing else 0,
            int(mon.is_dynamaxed),
        ])

        # Add stats and boosts
        embeddings.append(mon.stats.values())
        embeddings.append(mon.boosts.values())

        # Add status (one-hot encoded)
        embeddings.append([1 if mon.status == status else 0 for status in self._knowledge['Status']])

        # Add Types (one-hot encoded)
        embeddings.append([1 if mon.type_1 == pokemon_type else 0 for pokemon_type in self._knowledge['PokemonType']])
        embeddings.append([1 if mon.type_2 == pokemon_type else 0 for pokemon_type in self._knowledge['PokemonType']])

        # Add whether the mon is trapped or forced to switch. But first, find the index
        index = None
        if mon in battle.active_pokemon: index = 0 if battle.active_pokemon[0] == mon else 1
        embeddings.append([
            1 if index and battle.trapped[index] else 0,
            1 if index and battle.force_switch[index] else 0,
        ])

        # Flatten all the lists into a Nx1 list
        return [item for sublist in embeddings for item in sublist]

    # We encode the opponent's mon in a 771-dimensional embedding
    # We encode all the mons moves, whether it's active, if we know it's sent, it's current hp, whether it's fainted, its level, weight, whether it's recharging,
    # preparing, dynamaxed, its base stats (because we don't know it's IV/EV/Nature), boosts, status, types and whether it's trapped or forced to switch out.
    # We currently don't encode its item, possible abilities (271 * 3) or its species (1155) because of the large cardinalities
    # In the future, we should predict high/low ranges of stats based on damage and speeds/hail, and items based on cues
    def _embed_opp_mon(self, battle, mon):
        embeddings = []

        # Append moves to embedding (and account for the fact that the mon might have <4 moves)
        for move in (list(mon.moves.values()) + [None, None, None, None])[:4]:
            embeddings.append(self._embed_move(move))

        # Add whether the mon is active, the current hp, whether its fainted, its level, its weight and whether its recharging or preparing
        embeddings.append([
            int(mon.active), # This mon is on the field now
            int(mon in battle.opponent_team.values()), # This mon was brought
            mon.current_hp,
            int(mon.fainted),
            mon.level,
            mon.weight,
            int(mon.must_recharge),
            1 if mon.preparing else 0,
            int(mon.is_dynamaxed),
        ])

        # Add stats and boosts
        embeddings.append(mon.base_stats.values())
        embeddings.append(mon.boosts.values())

        # Add status (one-hot encoded)
        embeddings.append([1 if mon.status == status else 0 for status in self._knowledge['Status']])

        # Add Types (one-hot encoded)
        embeddings.append([1 if mon.type_1 == pokemon_type else 0 for pokemon_type in self._knowledge['PokemonType']])
        embeddings.append([1 if mon.type_2 == pokemon_type else 0 for pokemon_type in self._knowledge['PokemonType']])

        # Add whether the mon is trapped or forced to switch. But first, find the index
        index = None
        if mon in battle.active_pokemon: index = 0 if battle.active_pokemon[0] == mon else 1
        embeddings.append([
            1 if index and battle.trapped[index] else 0,
            1 if index and battle.force_switch[index] else 0,
        ])

        # Flatten all the lists into a Nx1 list
        return [item for sublist in embeddings for item in sublist]

    # Embeds the state of the battle in a 7814-dimensional embedding
    # Embed mons (and whether theyre active)
    # Embed opponent mons (and whether theyre active, theyve been brought or we don't know)
    # Then embed all the Fields, Side Conditions, Weathers, Player Ratings, # of Turns and the bias
    def embed_battle(self, battle):
        embeddings = []

        # Add team to embeddings
        for mon in battle.sent_team.values():
            embeddings.append(self._embed_mon(battle, mon))

        # Embed opponent's mons. teampreview_opponent_team has empty move slots while opponent_team has moves we remember.
        # We first embed opponent_active_pokemon, then ones we remember from the team, then the rest
        embedded_opp_mons = set()
        for mon in battle.opponent_active_pokemon:
            if mon:
                embeddings.append(self._embed_opp_mon(battle, mon))
                embedded_opp_mons.add(mon.species)

        for mon in battle.opponent_team.values():
            if mon.species in embedded_opp_mons: continue
            embeddings.append(self._embed_opp_mon(battle, mon))
            embedded_opp_mons.add(mon.species)

        for mon in battle.teampreview_opponent_team:
            if mon in embedded_opp_mons: continue
            embeddings.append(self._embed_opp_mon(battle, battle.teampreview_opponent_team[mon]))
            embedded_opp_mons.add(mon)

        # Add Dynamax stuff
        embeddings.append(battle.can_dynamax + battle.opponent_can_dynamax + [battle.dynamax_turns_left, battle.opponent_dynamax_turns_left])

        # Add Fields;
        embeddings.append([1 if field in battle.fields else 0 for field in self._knowledge['Field']])

        # Add Side Conditions
        embeddings.append([1 if sc in battle.side_conditions else 0 for sc in self._knowledge['SideCondition']])

        # Add Weathers
        embeddings.append([1 if weather == battle.weather else 0 for weather in self._knowledge['Weather']])

        # Add Player Ratings, the battle's turn and a bias term
        embeddings.append(list(map(lambda x: x if x else -1, [battle.rating, battle.opponent_rating, battle.turn, 1])))

        # Flatten all the lists into a 7814-dim list
        return np.array([item for sublist in embeddings for item in sublist])
"""
