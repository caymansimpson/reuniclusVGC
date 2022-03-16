import sys
from typing import Dict, List, Optional

sys.path.append(".") # will make "helpers" callable from root
sys.path.append("..") # will make "utils" callable from simulators
sys.path.append("...") # will make "utils" callable from simulators

from poke_env.environment.battle import Battle
from poke_env.player.battle_order import *
from helpers.doubles_utils import *

# Predicts Moves of a mon given a team-builder, then battle history
class AnticipationModel():

  def __init__(self, gen=8, priorty=0):
    return None

  # Predict moves based on teampreview
  def predict_prior(self, mon, observed_team):
    return None

  # Predict moves based on teampreview and battle history
  def predict_posterier(self, mon, observed_team, history):
    return None

  # Trains model
  def train(self, data):
    return None

  # Saves model
  def save(self, filename):
    return None

  # Read file of pre-trained parameters
  def load(self, filename):
    return None
