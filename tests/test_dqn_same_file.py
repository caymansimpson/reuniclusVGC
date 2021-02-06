# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import tensorflow as tf
import os
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

import wandb
from wandb.keras import WandbCallback
from tensorflow.keras.callbacks import Callback

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, MaxBoltzmannQPolicy, EpsGreedyQPolicy

from rl.memory import SequentialMemory

# This is the function that will be used to train the dqn
def dqn_training(player, dqn, nb_steps):
    dqn.fit(player, nb_steps=nb_steps, callbacks=[WandbCallback()])
    player.complete_current_battle()

def dqn_evaluation(player, dqn, nb_episodes):
    # Reset battle statistics
    player.reset_battles()
    dqn.test(player, nb_episodes=nb_episodes, visualize=False, verbose=False)

    print(
        "DQN Evaluation: %d victories out of %d episodes"
        % (player.n_won_battles, nb_episodes)
    )

# TODO: figure why DQN is only using same move
# TODO: Error message received: |error|[Invalid choice] Can't move: You can't choose a target for Eerie Impulse
# TODO:  WARNING - Error message received: |error|[Invalid choice] Can't move: You can't choose a target for Parting Shot
# TODO: |error|[Invalid choice] Can't switch: You sent more switches than Pokémon that need to switch
# TODO: print reward
# TODO: hyperparameter sweep: https://colab.research.google.com/drive/1gKixa6hNUB8qrn1CfHirOfTEQm0qLCSS?usp=sharing
if __name__ == "__main__":

    wandb.init(project='reuniclusVGC_DQN')
    config = wandb.config

    tf.random.set_seed(0)
    np.random.seed(0)
    tf.get_logger().setLevel('ERROR')

    config.NB_TRAINING_STEPS = 200000
    config.NB_EVALUATION_EPISODES = 1000
    config.team = 'mamoswine'
    config.first_layer_nodes = 1024
    config.second_layer_nodes = 512
    config.third_layer_nodes = 512
    config.gamma = .95
    config.delta_clip = .1
    config.target_model_update = 5
    config.lr = .01
    config.memory_limit = 100000
    config.warmup_steps = 2000

    env_player = SimpleDQNPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams[config.team])

    opponent = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
    second_opponent = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['garchomp'])

    # Output dimension
    n_action = len(env_player.action_space)

    # TODO: add batch size
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(config.first_layer_nodes, activation="relu", input_shape=(1, 7783), kernel_initializer='he_uniform'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(config.second_layer_nodes, activation="relu", kernel_initializer='he_uniform'),
        tf.keras.layers.Dense(config.third_layer_nodes, activation="relu", kernel_initializer='he_uniform'),
        tf.keras.layers.Dense(n_action, activation="linear")
    ])

    model.summary()

    memory = SequentialMemory(limit=config.memory_limit, window_length=1)

    # Simple epsilon greedy
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr="eps",
        value_max=1.0,
        value_min=0.05,
        value_test=0,
        nb_steps=config.NB_TRAINING_STEPS,
    )

    # Defining our DQN
    dqn = DQNAgent(
        model=model,
        nb_actions=len(env_player.action_space),
        policy=policy,
        memory=memory,
        nb_steps_warmup=config.warmup_steps,
        gamma=config.gamma, # This is the discount factor for the Value we learn - we care a lot about future rewards, and we dont rush to get there
        target_model_update=config.target_model_update, # This controls how much/when our model updates: https://github.com/keras-rl/keras-rl/issues/55; will create "Tensor.op is meaningless when eager execution is enabled.") error if < 1
        delta_clip=config.delta_clip, # Helps define Huber loss - cips values to be -1 < x < 1. https://srome.github.io/A-Tour-Of-Gotchas-When-Implementing-Deep-Q-Networks-With-Keras-And-OpenAi-Gym/
        enable_double_dqn=True,
    )

    dqn.compile(tf.keras.optimizers.Adam(lr=config.lr), metrics=["mae"])

    # Training
    # env_player.play_against(
    #     env_algorithm=dqn_training,
    #     opponent=opponent,
    #     env_algorithm_kwargs={"dqn": dqn, "nb_steps": config.NB_TRAINING_STEPS},
    # )

    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=second_opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": config.NB_TRAINING_STEPS},
    )

    model.save("models/model_%d" % config.NB_TRAINING_STEPS)

    # Evaluation
    print("Results against random player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": config.NB_EVALUATION_EPISODES},
    )

    print("\nResults against max player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=second_opponent,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": config.NB_EVALUATION_EPISODES},
    )

    os.system('say "your program has finished"')
