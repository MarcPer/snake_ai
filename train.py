#!/usr/bin/env python

from os import path

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from plugins.snake_env import SnakeEnv
import time

# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor

env = SnakeEnv(grid_size=4)
# env = SnakeEnv(grid_size=6)
learning_rate = 0.0005
# model_name = 'ppo2_grid6_alpha0'
# model_name = 'ppo2_grid6_stupid'
model_name = 'ppo2_grid4_alpha0'
model_path = path.join('models', model_name)
if path.isfile(model_path + '.zip'):
    print('---- Loading file: ', model_path)
    env = DummyVecEnv([lambda: env])
    model = PPO2.load(model_path, env=env, learning_rate=learning_rate, tensorboard_log=f'./logs/{model_name}')
else:
    model = PPO2(MlpPolicy, env=env, learning_rate=learning_rate, tensorboard_log=f'./logs/{model_name}')

timesteps = 10_000_000
timesteps = 10000
model.learn(total_timesteps=timesteps)
model.save(model_path)
env.close()

