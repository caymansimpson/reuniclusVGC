# -*- coding: utf-8 -*-
import sys
import random
import time
import json
import traceback

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

from poke_env.environment.move import Move
from helpers.embedder import Embedder

def importMoves(gen=8):
    moves = {}
    with open('/Users/cayman/Repositories/poke-env/src/poke_env/data/moves_by_gen/gen{0}_moves.json'.format(gen)) as f:
        moves = json.load(f)

    return {move_id: Move(move_id) for move_id in moves}

# Check whether the move lengths are always consistent
def validateLength(embedded_moves):
    hist = {}

    for embed in embedded_moves.values():
        if len(embed) not in hist: hist[len(embed)] = 1
        else: hist[len(embed)] += 1

    if len(hist) == 1: print("\tAll moves have a length of {0} -- everything looks good!".format(list(hist.keys())[0]))
    else:
        most_common_len = max(hist, key=hist.get)

        print("\tError: Moves don't always return a consistent length...")
        print("\tDistribution of lengths:" + str(hist))
        print("\tMost Common Length: {0}".format(most_common_len))
        print("\tMoves that don't have the most common length:")

        errors = {}

        for move_id in embedded_moves:
            if len(embedded_moves[move_id]) != most_common_len:
                if len(embedded_moves[move_id]) not in errors: errors[len(embedded_moves[move_id])] = []
                errors[len(embedded_moves[move_id])].append(move_id)

        for error_len in errors:
            print("\t\t Length: {0}".format(error_len) + " || " + ', '.join(errors[error_len]))


    print()

# Check whether the moves are always unique
def validateUniqueness(embedded_moves):

    alerted, duplicates = False, list()

    for m1 in embedded_moves:
        for m2 in embedded_moves:

            # Hidden Power is an edge-case that needs to be fixed
            if m1 == m2 or 'hiddenpower' in m1: continue

            elif embedded_moves[m1] == embedded_moves[m2]:
                if not alerted:
                    print("\tError: Not all moves are unique...")
                    alerted = True

                if m1 not in duplicates:
                    print("\t\t{0} is a duplicate of {1}".format(m1, m2))
                    duplicates.append(m2)

    if not alerted: print("\tAll embedded moves are unique; everything looks good!")
    print()

def main():
    print("\033[92m Starting script... \033[0m")
    t0 = time.time()

    expected_len = 180
    gen = 8

    print("\033[92m Loading Embedder & Moves... \033[0m")
    t1 = time.time()

    # Load Embedder and Moves
    embedder = Embedder(gen)
    moves = importMoves(gen)

    t1 = time.time()
    print("\tFinished in {0:.3f} seconds\n".format(t0 - t1))
    print("\033[92m Embedding Moves... \033[0m")

    # Store all embedded Moves
    embedded_moves = dict()

    for move_id in moves:
        embedded_moves[move_id] = embedder.embed_move(moves[move_id])

    t2 = time.time()
    print("\tFinished in {0:.3f} seconds\n".format(t2 - t1))
    print("\033[92m Validating Moves... \033[0m")

    validateLength(embedded_moves)
    validateUniqueness(embedded_moves)

    print("\033[92m Done in {0:.3f} seconds! \033[0m".format(time.time() - t0))


if __name__ == "__main__":
    main()
