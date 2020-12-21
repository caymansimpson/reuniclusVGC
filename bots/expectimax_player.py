from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
import random

"""
To modify this algo for Pokemon and efficiency, when prioritizing which trees to go down, we should prioritize:
- always saving best case scenario found so far
- never go past three turns
- explore self-damaging moves last

# To do this, use a stack and enueue things in the forlopp and then for all things in stack, order it, and pull them out in order
function alphabeta(node, depth, α, β, maximizingPlayer) is
    if depth = 0 or node is a terminal node then
        return the heuristic value of node
    if maximizingPlayer then
        value := −∞
        for each child of node do
            value := max(value, alphabeta(child, depth − 1, α, β, FALSE))
            α := max(α, value)
            if α ≥ β then
                break (* β cutoff *)
        return value
    else
        value := +∞
        for each child of node do
            value := min(value, alphabeta(child, depth − 1, α, β, TRUE))
            β := min(β, value)
            if β ≤ α then
                break (* α cutoff *)
        return value
"""

class ExpectimaxPlayer(Player):

    def choose_move(self, battle):

        # If we're not being forced to switch and are choosing our moves
        if not any(battle.force_switch):

            # Go through and get actions, filter them down to what's possible, and then eliminate ones that dont make sense
            first_moves = get_possible_moves(battle, battle.active_pokemon[0])
            second_moves = get_possible_moves(battle, battle.active_pokemon[1])

            all_possible_moves = itertools.product(first_moves, second_moves)
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
            reasonable_moves = filter_to_reasonable_moves(battle, filtered_moves)

            action1, action2 = Action(), Action()
            if len(reasonable_moves) > 0: action1, action2 = random.choice(reasonable_moves)
            elif len(filtered_moves) > 0: action1, action2 = random.choice(filtered_moves)

            # Choose a random action, and order actions when a pokemon is fainted so that the only action goes first
            if battle.active_pokemon[0] is None: action1, action2 = action2, action1

            order = "/choose " + action1.showdownify() + "," + action2.showdownify()

        # Force Switch situation
        else:
            moves = get_possible_moves(battle, battle.active_pokemon[0 if battle.force_switch[0] else 1])
            all_possible_moves = itertools.product(moves, [Action()])
            filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
            action1, _ = random.choice(filtered_moves)
            order = "/choose " + action1.showdownify()

        return order

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))

    # Win: 100 points
    # Each mon: 20 points
    # Each Pokemon that's faster: 1 (up to 4)
    def _reward(self, battle):
        return 0
