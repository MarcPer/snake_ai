#!/usr/bin/env python

from os import path

from multiprocessing import Pool
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2
from plugins.snake_env import SnakeEnv

# Optional: PPO2 requires a vectorized environment to run
# the env is now wrapped automatically when passing it to the constructor

def train(model_payload):
    env = SnakeEnv(grid_size=4)
    model_name = model_payload['name']
    model_path = path.join('models', model_name)
    if path.isfile(model_path):
        env = DummyVecEnv([lambda: env])
        model = PPO2.load('model_path', env=env, tensorboard_log=f'./logs/{model_name}')
    else:
        model = PPO2(MlpPolicy, env=env, tensorboard_log=f'./logs/{model_name}')

    model.learn(total_timesteps=1000000)
    model.save(model_path)
    env.close()

learning_rates = list(map(lambda x: 10**x * 0.00025, range(-2, 3)))
model_data = []
for i, params in enumerate(learning_rates):
    model_data.append({'name': f'ppo2_model2_{i}', 'learning_rate': params})

with Pool(5) as p:
    p.map(train, model_data)
