# -*- coding: utf-8 -*-
import asyncio

import sys
sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer

most_common_team = """
Tapu Fini @ Wiki Berry
Level: 50
Ability: Misty Surge
EVs: 236 HP / 0 Atk / 4 Def / 204 SpA / 12 SpD / 52 Spe
Modest Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Muddy Water
-  Moonblast
-  Protect
-  Calm Mind

Regieleki @ Light Clay
Level: 50
EVs: 0 HP / 0 Atk / 0 Def / 252 SpA / 4 SpD / 252 Spe
Timid Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Electroweb
-  Thunderbolt
-  Reflect
-  Light Screen

Incineroar @ Figy Berry
Level: 50
EVs: 244 HP / 20 Atk / 84 Def / 0 SpA / 148 SpD / 12 Spe
Careful Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Fake Out
-  Flare Blitz
-  Parting Shot
-  Snarl

Landorus-Therian @ Assault Vest
Level: 50
Ability: Intimidate
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Earthquake
-  Rock Slide
-  Fly
-  Superpower

Metagross @ Weakness Policy
Level: 50
Ability: Clear Body
EVs: 252 HP / 252 Atk / 0 Def / 0 SpA / 4 SpD / 0 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Protect
-  Iron Head
-  Stomping Tantrum
-  Ice Punch

Urshifu @ Focus Sash
Level: 50
EVs: 0 HP / 252 Atk / 0 Def / 0 SpA / 4 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Wicked Blow
-  Close Combat
-  Sucker Punch
-  Protect
"""

swampert_team = """
Zapdos-Galar @ Choice Scarf
Level: 50
Ability: Defiant
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Thunderous Kick
-  Brave Bird
-  Coaching
-  Stomping Tantrum

Dragapult @ Life Orb
Level: 50
Ability: Clear Body
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Phantom Force
-  Dragon Darts
-  Fly
-  Protect

Swampert @ Assault Vest
Level: 50
Ability: Torrent
EVs: 252 HP / 228 Atk / 4 Def / 0 SpA / 4 SpD / 20 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Liquidation
-  Ice Punch
-  High Horsepower
-  Hammer Arm

Clefairy @ Eviolite
Level: 50
Ability: Friend Guard
EVs: 252 HP / 0 Atk / 252 Def / 0 SpA / 4 SpD / 0 Spe
Bold Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Follow Me
-  Helping Hand
-  Sing
-  Protect

Celesteela @ Weakness Policy
Level: 50
Ability: Beast Boost
EVs: 92 HP / 0 Atk / 4 Def / 252 SpA / 4 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Flash Cannon
-  Air Slash
-  Meteor Beam
-  Protect

Rotom-Heat @ Sitrus Berry
Level: 50
Ability: Levitate
EVs: 252 HP / 0 Atk / 44 Def / 36 SpA / 20 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Overheat
-  Thunderbolt
-  Nasty Plot
-  Protect
"""

moltres_team="""
Raichu @ Focus Sash
Level: 50
Ability: Lightning Rod
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Nuzzle
-  Reflect
-  Fake Out
-  Eerie Impulse

Tapu Fini @ Sitrus Berry
Level: 50
Ability: Misty Surge
EVs: 252 HP / 0 Atk / 68 Def / 116 SpA / 20 SpD / 52 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Moonblast
-  Muddy Water
-  Calm Mind
-  Protect

Kartana @ Life Orb
Level: 50
Ability: Beast Boost
EVs: 4 HP / 252 Atk / 0 Def / 0 SpA / 0 SpD / 252 Spe
Jolly Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Leaf Blade
-  Sacred Sword
-  Smart Strike
-  Protect

Rotom-Heat @ Safety Goggles
Level: 50
Ability: Levitate
EVs: 252 HP / 0 Atk / 44 Def / 36 SpA / 20 SpD / 156 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Overheat
-  Thunderbolt
-  Nasty Plot
-  Protect

Regirock @ Leftovers
Level: 50
Ability: Clear Body
EVs: 252 HP / 156 Atk / 0 Def / 0 SpA / 100 SpD / 0 Spe
Adamant Nature
IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Rock Slide
-  Body Press
-  Earthquake
-  Curse

Moltres-Galar @ Weakness Policy
Level: 50
Ability: Berserk
EVs: 204 HP / 0 Atk / 100 Def / 76 SpA / 28 SpD / 100 Spe
Modest Nature
IVs: 31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe
-  Fiery Wrath
-  Air Slash
-  Nasty Plot
-  Protect
"""

async def main():
    # We create three random players
    players = [
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=most_common_team),
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=moltres_team),
      RandomDoublesPlayer(max_concurrent_battles=10, battle_format='gen8vgc2021', team=swampert_team),
    ]

    # Now, we can cross evaluate them: every player will player 30 games against every
    # other player.
    cross_evaluation = await cross_evaluate(players, n_challenges=100)

    # Defines a header for displaying results
    table = [["-"] + [p.username for p in players]]

    # Adds one line per player with corresponding results
    for p_1, results in cross_evaluation.items():
        table.append([p_1] + [cross_evaluation[p_1][p_2] for p_2 in results])

    # Displays results in a nicely formatted table.
    print(tabulate(table))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
