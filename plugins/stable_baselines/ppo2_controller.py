"""Handles input that is always applied to game (e.g. QUIT command)
"""

from os import path
from stable_baselines import PPO2
from plugins.base_controller import BaseController

class Ppo2Controller(BaseController):
    def __init__(self, *args):
        if not args:
            raise SystemExit('No model file given')
        model_filename = args[0]
        fullpath = path.join('models', model_filename)
        self.model = PPO2.load(fullpath)

    def _computed_action(self, state, curr_dir):
        action, _states = self.model.predict(state)
        return action
