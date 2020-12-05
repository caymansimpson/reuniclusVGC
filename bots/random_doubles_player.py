from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
import random
import sys

sys.path.append(".") # will make "utils" callable from root
sys.path.append("..") # will make "utils" callable from simulators

from helpers.doubles_utils import Action

class RandomDoublesPlayer(Player):

    # TODO:  WARNING - Error message received: |error|[Invalid choice] Can't move: You sent more choices than unfainted Pokémon.
    # Simplifies Random Move Choices -- no Z, dynamax or Mega evolutions
    # original choose_random_doubles_move found here: https://github.com/hsahovic/poke-env/blob/a336a7221089537ef724aa1d15bb58d1a81cb69d/src/poke_env/player/player.py
    def choose_move(self, battle):

        print('')
        print('\t' + str(battle.active_pokemon))


        actions = []
        action1, action2 = None, None

        # If we somehow don't have any active pokemon, return default
        if not any(battle.active_pokemon):
            return self.choose_default_move()

        # Get available pokemon
        pokemon_1, pokemon_2 = battle.active_pokemon

        # If one pokemon is left and it's in the second slot, we make it Pokemon 1 and also keep it's index at 1
        pokemon_1_index = 0
        if pokemon_1 is None:
            pokemon_1, pokemon_2 = pokemon_2, pokemon_1
            pokemon_1_index = 1

        # Iterate through available moves of Pokemon_1
        for move in battle.available_moves[pokemon_1_index]:

            # Add all available move to list against all targets
            for target in battle.get_possible_showdown_targets(move, pokemon_1):
                actions.append(Action(pokemon_1, move, target))

        # Add all available switches to this list, if either the pokemon isn't trapped or we're forced to switch
        if not battle.trapped[pokemon_1_index] or sum(battle.force_switch) == 1:
            for pokemon in battle.available_switches[pokemon_1_index]:
                actions.append(Action(pokemon_1, pokemon))

        # Update order to be a random choice for the first pokemon
        if actions:
            action1 = random.choice(actions)
            order = '/choose ' + action1.showdownify()
        else: order = '/choose default'

        # If we're being forced to switch, return the switch
        if sum(battle.force_switch) == 1:
            return order

        # Move onto the second pokemon
        if pokemon_2 is not None or sum(battle.force_switch) == 2:
            actions = []

            if pokemon_2 is not None:

                # Add available moves if they have PP left
                for move in battle.available_moves[1]:
                    for target in battle.get_possible_showdown_targets(move, pokemon_2):
                        actions.append(Action(pokemon_2, move, target))

            # Only add switches if we're not trapped or we're forced to switch
            if not battle.trapped[1] or sum(battle.force_switch) == 2:
                for pokemon in battle.available_switches[1]:

                    # Ensure that we have not already chosen this pokemon for switching
                    if order != self.create_order(pokemon):
                        actions.append(Action(pokemon_2, pokemon))

            # Add this new order to our order
            if actions:
                action2 = random.choice(actions)
                order += ',' + action2.showdownify()
            else:
                order += ",default"

        # if battle.active_pokemon[0] is not None and battle.active_pokemon[1] is not None:
        #     print('\t' + str(action1) + "\t\t||\t\t" + str(action2))
        #     print('\t' + battle.active_pokemon[0].species + "," + battle.active_pokemon[1].species + "=> " + order)
        # elif battle.active_pokemon[0] is None:
        #     print('\t' + str(action1) + "\t\t||\t\t" + str(action2))
        #     print('\t' + "None," + battle.active_pokemon[1].species + "=> " + order)
        # elif battle.active_pokemon[1] is None:
        #     print('\t' + str(action1) + "\t\t||\t\t" + str(action2))
        #     print('\t' + battle.active_pokemon[0].species + ",None=> " + order)

        return order

    def teampreview(self, battle):

        # We use 1-6 because  showdown's indexes start from 1
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
