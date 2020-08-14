#!/usr/bin/env python

import gym

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from plugins.snake_env import SnakeEnv

env = SnakeEnv(grid_size=4)
# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor

model = PPO2(MlpPolicy, env)

env = DummyVecEnv([lambda: env])
model = PPO2.load('models/ppo2_model1', env=env, tensorboard_log='./logs/ppo2_model1')

model.learn(total_timesteps=1000000)
model.save("models/ppo2_model1")

env.close()
