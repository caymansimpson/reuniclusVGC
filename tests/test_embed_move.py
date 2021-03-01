# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import json
import traceback

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.environment.move import Move
from poke_env.environment.field import Field
from poke_env.environment.side_condition import SideCondition
from poke_env.environment.status import Status
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.battle import Battle

from helpers.doubles_utils import *
from poke_env.utils import to_id_str

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

async def main():
    print("\033[92m Starting script... \033[0m")

    # Define what we need to test embedding moves
    player = SimpleDQNPlayer()
    expected_len = 178

    # Define function testing embeddings
    def test_embedding(embedding, expected_len, opp=False):
        try:
            if len(embedding) != expected_len:
                print("Error: Length of embedding does not equal" + str(expected_len) + " like expected -- it is " + str(len(embedding)))
                if opp: print("This happened for the opponent")
                raise(Exception())
        except Exception as e:
            print(move_id)
            print(Move(move_id))
            print(e)
            traceback.print_exc()
            print()

    # Iterate through all moves to ensure they have the same length
    with open('/Users/cayman/Repositories/poke-env/src/poke_env/data/moves.json') as f:
        moves = json.load(f)
        for move_id in moves:
            embedding = player._embed_move(Move(move_id))
            test_embedding(embedding, expected_len)

    print("Done testing on all moves... now testing on opponent mon...")

    # Create dummy player that tests embeddings in an online battle scenario
    class DummyPlayer(RandomDoublesPlayer):

        def choose_move(self, battle):
            for mon in battle.teampreview_opponent_team.values():
                for move in (list(mon.moves.values()) + [None, None, None, None])[:4]:
                    embedding = player._embed_move(move)
                    test_embedding(embedding, expected_len, opp=True)

            random = RandomDoublesPlayer()
            move = random.choose_move(battle)
            return move

    # We create players:
    p0 = SmarterRandomPlayer(max_concurrent_battles=1, battle_format='gen8vgc2021', team=TeamRepository.teams['regirock'])
    p1 = DummyPlayer(max_concurrent_battles=1, battle_format="gen8vgc2021", team=TeamRepository.teams['spectrier'])

    await asyncio.gather(
        p0.send_challenges(
            opponent=to_id_str(p1.username),
            n_challenges=1,
            to_wait=p1.logged_in,
        ),
        p1.accept_challenges(
            opponent=to_id_str(p0.username), n_challenges=1
        ),
    )
    print("Finished testing on opponents mons...")
    print("\033[92m Done! \033[0m")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
