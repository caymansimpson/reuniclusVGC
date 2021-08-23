# -*- coding: utf-8 -*-
import asyncio
import sys
import random
import tensorflow as tf
import os
import numpy as np
import datetime

sys.path.append(".") # will make "bots" callable from root
sys.path.append("..") # will make "bots" callable from simulators
sys.path.append('/Users/cayman/Repositories/poke-env/src') #; https://stackoverflow.com/questions/4383571/importing-files-from-different-folder

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

from tensorflow.keras.layers import Dense, Flatten, BatchNormalization

from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy, MaxBoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory

# This is the function that will be used to train the dqn
def dqn_training(player, dqn, nb_steps):
    history = dqn.fit(player, nb_steps=nb_steps, callbacks=[WandbCallback()])
    # print(history.history.keys()); dict_keys(['episode_reward', 'nb_episode_steps', 'nb_steps'])
    player.complete_current_battle()

def dqn_evaluation(player, dqn, nb_episodes):
    # Reset battle statistics
    player.reset_battles()
    dqn.test(player, nb_episodes=nb_episodes, visualize=False, verbose=False)


# Record progress of wins for keras models; you can add this to callbacks here: WinRatioCallback(player, dqn)
class WinRatioCallback(tf.keras.callbacks.Callback):

    def __init__(self, player, dqn):
        self.player = player
        self.dqn = dqn
        self.max_player = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])
        self.rand_player = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams['swampert'])

    def on_epoch_end(self, epoch, logs=None):

        if epoch % 2000 != 0: return
        num_battles = 100

        self.player.play_against(env_algorithm=dqn_evaluation, opponent=self.max_player, env_algorithm_kwargs={"dqn": self.dqn, "nb_episodes": num_battles})
        wandb.log({'epoch': epoch, 'pct_wins_against_max': self.player.n_won_battles*1./num_battles})

        self.player.play_against(env_algorithm=dqn_evaluation, opponent=self.rand_player, env_algorithm_kwargs={"dqn": dqn, "nb_episodes": num_battles})
        wandb.log({'epoch': epoch, 'pct_wins_against_rand': self.player.n_won_battles*1./num_battles})

# TODO: figure out why no dynamax
# TODO: figure out why no switching
def train():

    # Default values for hyper-parameters we're going to sweep over
    config_defaults = {
        'NB_TRAINING_STEPS': 10000,
        'NB_EVALUATION_EPISODES': 100,
        'first_layer_nodes': 500,
        'second_layer_nodes': 500,
        'third_layer_nodes': -1,
        'gamma': .99,
        'delta_clip': .9,
        'target_model_update': 10,
        'lr': .001,
        'memory_limit': 100000,
        'warmup_steps': 500,
        'activation': "relu",
        'policy': 'EpsGreedyQPolicy',
        'team': 'garchomp',
        'opponent': 'max',
        'opponent_team': 'swampert'
    }

    # Initialize a new wandb run; We can use os.environ['WANDB_MODE'] = 'dryrun' to not save wandb to cloud
    wandb.init(config=config_defaults, project='reuniclusVGC_DQN')
    config = wandb.config

    env_player = SimpleDQNPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams[config.team])

    rand_opp = SmarterRandomPlayer(battle_format="gen8vgc2021", team=TeamRepository.teams[config.opponent_team])
    max_opp = MaxDamagePlayer(battle_format="gen8vgc2021", team=TeamRepository.teams[config.opponent_team])

    model = tf.keras.models.Sequential()
    model.add(Dense(config.first_layer_nodes, activation=config.activation, input_shape=(1, 7790), kernel_initializer='he_uniform'))
    model.add(Flatten())
    if config.second_layer_nodes > 0: model.add(Dense(config.second_layer_nodes, activation=config.activation, kernel_initializer='he_uniform'))
    if config.third_layer_nodes > 0: model.add(Dense(config.third_layer_nodes, activation=config.activation, kernel_initializer='he_uniform'))
    model.add(BatchNormalization())
    model.add(Dense(len(env_player.action_space), activation="linear"))

    model.summary()

    memory = SequentialMemory(limit=config.memory_limit, window_length=1)

    # TODO: probabilities can contain NaN, so MaxBoltzmannQPolicy might not work
    policy = None
    if config.policy == 'MaxBoltzmannQPolicy': policy = MaxBoltzmannQPolicy() # https://github.com/keras-rl/keras-rl/blob/master/rl/policy.py#L242
    elif config.policy == 'EpsGreedyQPolicy': policy = EpsGreedyQPolicy(eps=.1)
    elif config.policy == 'LinearAnnealedPolicy':
        policy = LinearAnnealedPolicy(
            EpsGreedyQPolicy(),
            attr="eps",
            value_max=.5,
            value_min=0.025,
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
        target_model_update=config.target_model_update, # This controls how much/when our model updates: https://github.com/keras-rl/keras-rl/issues/55
        delta_clip=config.delta_clip, # Helps define Huber loss - cips values to be -1 < x < 1. https://srome.github.io/A-Tour-Of-Gotchas-When-Implementing-Deep-Q-Networks-With-Keras-And-OpenAi-Gym/
        enable_double_dqn=True,
    )

    dqn.compile(
        tf.keras.optimizers.Adam(lr=config.lr),
        metrics=[
            tf.keras.metrics.MeanSquaredError(),
            tf.keras.metrics.MeanAbsoluteError(),
        ]
    )

    # Training
    env_player.play_against(
        env_algorithm=dqn_training,
        opponent=(rand_opp if config.opponent == 'rand' else max_opp),
        env_algorithm_kwargs={"dqn": dqn, "nb_steps": config.NB_TRAINING_STEPS},
    )

    # Evaluation against Rand Player
    print("Results against random player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=rand_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": config.NB_EVALUATION_EPISODES},
    )
    print("DQN Evaluation: %d victories out of %d episodes" % (env_player.n_won_battles, config.NB_EVALUATION_EPISODES))
    wandb.log({'pct_wins_against_rand': env_player.n_won_battles*1./config.NB_EVALUATION_EPISODES})

    # Evaluation against Max Player
    print("\nResults against max player:")
    env_player.play_against(
        env_algorithm=dqn_evaluation,
        opponent=max_opp,
        env_algorithm_kwargs={"dqn": dqn, "nb_episodes": config.NB_EVALUATION_EPISODES},
    )
    print("DQN Evaluation: %d victories out of %d episodes" % (env_player.n_won_battles, config.NB_EVALUATION_EPISODES))
    wandb.log({'pct_wins_against_max': env_player.n_won_battles*1./config.NB_EVALUATION_EPISODES})

    print("Saving model...")
    dqn.save_weights("models/model_" + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), overwrite=True)

# Implemented; https://colab.research.google.com/drive/1gKixa6hNUB8qrn1CfHirOfTEQm0qLCSS?usp=sharing
def sweep():
    sweep_config = {
        'method': 'bayes',
        'metric': {'name': 'pct_wins_against_max', 'goal': 'maximize'}, # or episode_reward
        'parameters': {
            'gamma': {'values': [.9, .95, .99]},
            'delta_clip': {'values': [.1, .5, .9]},
            'target_model_update': {'values': [1, 100, 1000]},
            'NB_TRAINING_STEPS': {'values': [10000, 100000, 500000, 1000000]},
            'lr': {'values': [1e-2, 1e-3, 1e-4, 3e-4, 3e-5, 1e-5]},
            'activation': {'values': ['relu', 'elu', 'selu']},
            'first_layer_nodes': {'values': [128, 256, 512, 1024]},
            'second_layer_nodes': {'values': [128, 256, 512, 1024]},
            'third_layer_nodes': {'values': [128, 256, 512, 1024]},
            'opponent': {'values': ['max', 'rand']},
            'policy': {'values': ['MaxBoltzmannQPolicy', 'EpsGreedyQPolicy', 'LinearAnnealedPolicy']},
        }
    }

    # wandb: ERROR Run m7gt74yz errored: RuntimeError("There is no current event loop in thread 'Thread-2'.",)
    sweep_id = wandb.sweep(sweep_config, entity="caymansimpson", project="reuniclusVGC_DQN")
    wandb.agent(sweep_id, train)

# TODO: see if I can get random teams to battle
# To run: from home in reuniclusVGC: source ~/.bash_profile; pyenv local system; python3.6 tests/test_dqn_same_file.py
if __name__ == "__main__":
    tf.random.set_seed(0)
    np.random.seed(0)
    tf.get_logger().setLevel('ERROR')

    train() # This will just train a model

    # sweep() # This will perform the sweep
    # asyncio.get_event_loop().run_until_complete(main)
