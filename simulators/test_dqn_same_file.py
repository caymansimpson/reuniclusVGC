# -*- coding: utf-8 -*-
import asyncio
import sys
import random
from math import comb
import tensorflow as tf

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, MaxBoltzmannQPolicy
from rl.memory import SequentialMemory

from tensorflow.keras.layers import Dense, Flatten, Activation, BatchNormalization, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# This is the function that will be used to train the dqn
def dqn_training(player, dqn, nb_steps):
    global graph
    with graph.as_default():
        dqn.fit(player, nb_steps=nb_steps)
        player.complete_current_battle()


def dqn_evaluation(player, dqn, nb_episodes):
    # Reset battle statistics
    player.reset_battles()
    dqn.test(player, nb_episodes=nb_episodes, visualize=False, verbose=False)

    print(
        "DQN Evaluation: %d victories out of %d episodes"
        % (player.n_won_battles, nb_episodes)
    )

# To run from command line, run this in the root directory: python3.8 simulators/test_dqn.py
def main():
    print("\033[92m Starting script... \033[0m")

    random_opp = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
    max_opp = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['regirock'])

    env_player = SimpleDQNPlayer(num_battles=10000, battle_format="gen8vgc2021", team=TeamRepository.teams['garchomp'])

    # Output dimension
    n_action = len(env_player.action_space)

    global graph
    graph = tf.compat.v1.get_default_graph()

    model = Sequential()

    # Get initializer for hidden layers
    initializer = tf.keras.initializers.RandomNormal(mean=.05, stddev=.02)

    # Input Layer
    model.add(Input(shape=(1, 7732)))

    # Hidden Layers
    model.add(Dense(512, activation="relu", use_bias=False, kernel_initializer=initializer, name='first_hidden'))
    model.add(Flatten(name='flatten')) # Flattening resolve potential issues that would arise otherwise
    model.add(Dense(256, activation="relu", use_bias=False, kernel_initializer=initializer, name='second_hidden'))

    # Output Layer
    model.add(Dense(len(env_player.action_space), use_bias=False, kernel_initializer=initializer, name='final'))
    model.add(BatchNormalization()) # Increases speed: https://www.dlology.com/blog/one-simple-trick-to-train-keras-model-faster-with-batch-normalization/
    model.add(Activation("linear")) # Same as passing activation in Dense Layer, but allows us to access last layer: https://stackoverflow.com/questions/40866124/difference-between-dense-and-activation-layer-in-keras

    # This is how many battles we'll remember before we start forgetting old ones
    memory = SequentialMemory(limit=max(10000, 10000), window_length=1)

    # Simple epsilon greedy policy
    # This takes the output of our NeuralNet and converts it to a value
    # Softmax is another probabilistic option: https://github.com/keras-rl/keras-rl/blob/master/rl/policy.py#L120
    policy = LinearAnnealedPolicy(
        MaxBoltzmannQPolicy(),
        attr="eps",
        value_max=1.0,
        value_min=0.05,
        value_test=0,
        nb_steps=10000,
    )

    # Defining our DQN
    dqn = DQNAgent(
        model=model,
        nb_actions=len(env_player.action_space),
        policy=policy,
        memory=memory,
        nb_steps_warmup=1000, # The number of battles we go through before we start training: https://hub.packtpub.com/build-reinforcement-learning-agent-in-keras-tutorial/
        gamma=0.9, # This is the discount factor for the Value we learn - we care a lot about future rewards
        target_model_update=.01, # This controls how much/when our model updates: https://github.com/keras-rl/keras-rl/issues/55
        delta_clip=1, # Helps define Huber loss - cips values to be -1 < x < 1. https://srome.github.io/A-Tour-Of-Gotchas-When-Implementing-Deep-Q-Networks-With-Keras-And-OpenAi-Gym/
        enable_double_dqn=True,
    )

    dqn.compile(Adam(lr=0.01), metrics=["mae"])

    # Training
    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=random_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": 10000},
    )

    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=max_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": 10000},
    )

    # Evaluation
    print("Results against random player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=random_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": 100},
    )

    print("\nResults against max player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=max_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": 100},
    )


if __name__ == "__main__":
    main()
