# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import tensorflow as tf
import numpy as np

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
# sys.path.insert(1, '/Users/cayman/Library/Python/3.6/lib/python/site-packages')

from poke_env.player.random_player import RandomPlayer
from poke_env.player.utils import cross_evaluate
from tabulate import tabulate
from bots.random_doubles_player import RandomDoublesPlayer
from bots.smarter_random_player import SmarterRandomPlayer
from bots.simple_dqn_player import SimpleDQNPlayer
from bots.max_damage_player import MaxDamagePlayer
from helpers.team_repo import TeamRepository

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, MaxBoltzmannQPolicy, EpsGreedyQPolicy

from rl.memory import SequentialMemory

# from tensorflow.python.keras.backend import set_session

# This is the function that will be used to train the dqn
def dqn_training(player, dqn, nb_steps):
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

if __name__ == "__main__":

    # TODO: https://github.com/wau/keras-rl2/blob/master/examples/dqn_atari.py#L107; plot rewards and loss

    NB_TRAINING_STEPS = 20000
    NB_EVALUATION_EPISODES = 100

    tf.random.set_seed(0)
    np.random.seed(0)
    tf.get_logger().setLevel('ERROR')

    env_player = SimpleDQNPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['garchomp'])

    opponent = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
    second_opponent = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['regirock'])

    # Output dimension
    n_action = len(env_player.action_space)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(1024, activation="relu", input_shape=(1, 7782)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation="elu"),
        tf.keras.layers.Dense(256, activation="elu"),
        tf.keras.layers.Dense(n_action, activation="linear")
    ])

    model.summary()

    memory = SequentialMemory(limit=10000, window_length=1)

    # Ssimple epsilon greedy
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr="eps",
        value_max=1.0,
        value_min=0.05,
        value_test=0,
        nb_steps=10000,
    )

    # gamma 0.8
    # reward is everything
    # random: 76% of battles won
    # max: 0% of battles won

    # gamma 0.9
    # reward is just winning
    # random: 77% of battles won
    # max: 0% battles won

    # Defining our DQN
    dqn = DQNAgent(
        model=model,
        nb_actions=len(env_player.action_space),
        policy=policy,
        memory=memory,
        nb_steps_warmup=1000,
        gamma=0.9, # This is the discount factor for the Value we learn - we care a lot about future rewards
        target_model_update=1, # This controls how much/when our model updates: https://github.com/keras-rl/keras-rl/issues/55; will create "Tensor.op is meaningless when eager execution is enabled.") error if < 1
        delta_clip=.01, # Helps define Huber loss - cips values to be -1 < x < 1. https://srome.github.io/A-Tour-Of-Gotchas-When-Implementing-Deep-Q-Networks-With-Keras-And-OpenAi-Gym/
        enable_double_dqn=True,
    )

    dqn.compile(tf.keras.optimizers.Adam(lr=0.00025), metrics=["mae"])

    # Training
    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=second_opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": NB_TRAINING_STEPS},
    )

    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": NB_TRAINING_STEPS},
    )

    model.save("models/model_%d" % NB_TRAINING_STEPS)

    # Evaluation
    print("Results against random player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": NB_EVALUATION_EPISODES},
    )

    print("\nResults against max player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=second_opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": NB_EVALUATION_EPISODES},
    )
