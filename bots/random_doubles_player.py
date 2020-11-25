from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
import random

class RandomDoublesPlayer(Player):
    def choose_move(self, battle):
        return self.choose_random_doubles_move(battle)

    # Simplifies Random Move Choices -- no Z, dynamax or Mega evolutions
    # original choose_random_doubles_move found here: https://github.com/hsahovic/poke-env/blob/a336a7221089537ef724aa1d15bb58d1a81cb69d/src/poke_env/player/player.py
    def choose_random_doubles_move(self, battle):
        available_orders = []

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

            # If we're out of PP, it shouldn't be considered an available move
            if move.current_pp == 0: continue

            # Add all available move to list against all targets
            for target in battle.get_possible_showdown_targets(move, pokemon_1):
                available_orders.append(self.create_order(move, move_target=target))

        # Add all available switches to this list, if either the pokemon isn't trapped or we're forced to switch
        if not battle.trapped[pokemon_1_index] or sum(battle.force_switch) == 1:
            for pokemon in battle.available_switches[pokemon_1_index]:
                available_orders.append(self.create_order(pokemon))

        # Update order to be a random choice for the first pokemon
        if available_orders: order = random.choice(available_orders)
        else: order = self.choose_default_move()

        # If we're being forced to switch, return the switch
        if sum(battle.force_switch) == 1:
            return order

        # Move onto the second pokemon
        if pokemon_2 is not None or sum(battle.force_switch) == 2:
            pokemon_2 = battle.active_pokemon[1] # If there are two active pokemon, this will always be 1
            available_orders = []

            if pokemon_2 is not None:

                # Add available moves if they have PP left
                for move in battle.available_moves[1]:
                    if move.current_pp == 0: continue

                    for target in battle.get_possible_showdown_targets(move, pokemon_2):
                        available_orders.append(self.create_order(move, move_target=target))

            # Only add switches if we're not trapped or we're forced to switch
            if not battle.trapped[1] or sum(battle.force_switch) == 2:
                for pokemon in battle.available_switches[1]:

                    # Ensure that we have not already chosen this pokemon for switching
                    if order != self.create_order(pokemon):
                        available_orders.append(self.create_order(pokemon))

            # Add this new order to our order
            if available_orders:
                order += random.choice(available_orders).replace("/choose ", ",")
            else:
                order += ",default"

        return order
