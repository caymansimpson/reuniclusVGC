from poke_env.player.player import Player
from poke_env.player.random_player import RandomPlayer
import random
from queue import PriorityQueue
import numpy as np

"""
============== Creating a player that moves based on Expectimax ==============
This is not a finished bot

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
"""
# Need to implement advance(battle, actions)
# get_value(model, battle)
# use PriorityQueue to prioritize most likely situations
function alphabeta(battle, depth, alpha, beta, maximizingPlayer) is
    if depth == 0 or battle.won: return get_value(model, battle)

    first_moves = get_possible_moves(battle, battle.active_pokemon[0])
    second_moves = get_possible_moves(battle, battle.active_pokemon[1])

    all_possible_moves = itertools.product(first_moves, second_moves)
    filtered_moves = filter_to_possible_moves(battle, all_possible_moves)
    reasonable_moves = filter_to_reasonable_moves(battle, filtered_moves)

    if maximizingPlayer then
        value = -np.inf

        for actions in (reasonable_moves if len(reasonable_moves) > 0 else filtered_moves):
            value = max(value, alphabeta(advance(battle, actions), depth − 1, alpha, beta, FALSE))
            alpha = max(alpha, value)

            if alpha ≥ beta: break # (* beta cutoff *)
        return value
    else
        value = np.inf
        for actions in (reasonable_moves if len(reasonable_moves) > 0 else filtered_moves):
            value = min(value, alphabeta(advance(battle, actions), depth − 1, alpha, beta, TRUE))
            beta = min(beta, value)
            if beta ≤ alpha: break # (* alpha cutoff *)
        return value

alphabeta(battle, 6, -np.inf, np.inf, TRUE)
"""

"""
In alpha zero, they have:
- deep neural network that takes in the state and output action probabilities, with the predicted value of an action
    - the predicted value  = E[expected outcome | state]
- It doesn't use alphabeta pruning; instead it uses a Monte-carlo tree search
    - It just self-plaus a bunch til the games end
    - In each self-play, they branch off to explore different outcomes
    - How does it select states?
        - low visit count
        - high max(move probability)
        - high predicted value
    - Neural network aims to:
        - minimize error between predicted outcomes and game outcomes
        - maximize similarity of win probability with action probability
        - Mathematically, minimize the following:
            - (predicted outcoemes - actual outcomes)^2 - sum(prob_action*log(predicted_prob_action)) + constant*sum(parameters^2)
"""
class ExpectimaxPlayer(Player):

    def choose_move(self, battle):
        return '/choose default'

    # Get Random Team
    def teampreview(self, battle):
        return "/team " + "".join(random.sample(list(map(lambda x: str(x+1), range(0, len(battle.team)))), k=4))
