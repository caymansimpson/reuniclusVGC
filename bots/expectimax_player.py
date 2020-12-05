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

        # Get all possible moves. If there are none, return default
        possible_moves = get_reasonable_moves(battle)
        if len(possible_moves) == 0: return "/choose default,default"

        # Choose a random action, and order actions such that action1 always is not None
        action1, action2 = random.choice(possible_moves)
        if action1 is None and action2 is None: return "/choose default,default"

        order = "/choose " + (action1.showdownify() if action1 is None else "default")
        order += "," + (action2.showdownify() if action2 is None else "default")

        return order

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))

    # Win: 100 points
    # Each mon: 20 points
    # Each Pokemon that's faster: 1 (up to 4)
    def _reward(self, battle):
        return 0
