from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
import random

"""
To modify this algo for Pokemon and efficiency, when prioritizing which trees to go down, we should prioritize:
- always saving best case scenario found so far
- never go past three turns
- explore self-damaging moves last

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
        return self.choose_random_doubles_move(battle)

    def teampreview(self, battle):
        # We use random for now
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team))), k=4))

    # Win: 100 points
    # Each mon: 20 points
    # Each Pokemon that's faster: 1 (up to 4)
    def _reward(self, battle):
        return 0
