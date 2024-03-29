#!/usr/bin/env python
"""
UI and user input logic that interacts with snake gym environment.
"""
import pygame as pg
import argparse
import importlib
from enum import Enum
from operator import itemgetter
from plugins.snake_env import SnakeEnv
from plugins.memory_playback import MemoryPlayback

CLOCK = pg.time.Clock()
TARGET_FPS = 60 # Game update rate depends on speed parameter, not this.
                # FPS should be high to handle quick input.

def get_class_name(plugin_name):
    """Converts snake case plugin name into camel case class name.
    """
    return ''.join([c[0].upper() + c[1:] for c in plugin_name.split("_")])

def load_plugin(plugin_args):
    """Loads and instantiates plugin.
    """
    plugin_name = plugin_args[0]
    module = importlib.import_module(f'plugins.{plugin_name}')
    class_name = get_class_name(plugin_name)
    pclass = getattr(module, class_name)
    return pclass(*plugin_args[1:])

def call_if_exists(obj, method_name, args = []):
    if hasattr(obj, method_name) and callable(getattr(obj, method_name)):
        method = getattr(obj, method_name)
        return method(*args)
    return None

PLUGINS_DICT = {
        'sound': None,
        'renderer': None,
        'aux': None
        }

class Game:
    def __init__(self, controller, env, speed, plugins):
        self.env = env
        self.controller = controller
        self.update_every = round(speed/1000 * TARGET_FPS)
        self.plugins = PLUGINS_DICT
        self.load_plugins(env, plugins)

    def load_plugins(self, env, plugins):
        for p in plugins:
            print(f'Loading plugin: {p[0]}')
            pobj = load_plugin(p)
            for plugin_type in PLUGINS_DICT.keys():
                if plugin_type in pobj.types():
                    self.plugins[plugin_type] = pobj

        # Default to base plugins if none was set
        for plugin_type in PLUGINS_DICT.keys():
            if not self.plugins[plugin_type]:
                self.plugins[plugin_type] = load_plugin([f'base_{plugin_type}'])

    def reset(self):
        return {
                'game_over': False,
                'dead': False,
                'score': 0,
                'action': 0, # Do nothing
                'update_counter': self.update_every, # start counter ready to update
                'state': self.env.reset()
               }

    def run(self):
        """Start game.
        """
        game_over, dead, score, action, update_counter, state = itemgetter(
            'game_over', 'dead', 'score', 'action', 'update_counter', 'state')(self.reset())
        renderer = self.plugins['renderer']
        controller = self.controller
        is_playback = self.env.is_playback()
        sound = self.plugins['sound']
        while not game_over:
            CLOCK.tick(60)
            fps = CLOCK.get_fps()
            renderer.set_caption(f"{fps:.2f} fps")
            renderer.render(state, self.env, score,
                            {'dead': dead, 'is_playback': is_playback})

            new_action = controller.get_action(state, self.env.curr_dir)
            action = new_action if new_action != 0 else action
            if action == 'QUIT':
                game_over = True
                continue
            elif action == 'CONTINUE' and is_playback:
                dead = False
            elif action == 'RESTART':
                game_over, dead, score, action, update_counter, state = itemgetter(
                    'game_over', 'dead', 'score', 'action', 'update_counter', 'state')(self.reset())
                continue
            if dead:
                continue
            if update_counter >= self.update_every:
                state, reward, dead, _info = self.env.step(action)
                score += reward
                if reward > 0:
                    sound.play_eat()
                self.plugins['aux'].run(state, reward, dead, self.env.curr_dir, action)
                update_counter = 0
                action = 0 # Do nothing
            else:
                update_counter += 1
        for p in self.plugins.values():
            call_if_exists(p, 'close')

def load_controller(name, args):
    if name == 'user':
        from plugins.user import User
        return User()
    elif name.startswith('sb:'):
        plugin_name = name.split(':')[1].lower()
        if len(plugin_name) == 0:
            raise SystemExit("No plugin name given, only 'sb:' namespace")
        plugin_name += '_controller'
        module = importlib.import_module(f'plugins.stable_baselines.{plugin_name}')
        class_name = get_class_name(plugin_name)
        pclass = getattr(module, class_name)
        return pclass(*args)
    from plugins.base_controller import BaseController
    return BaseController()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Snake game')
    parser.add_argument('--controller', action='store', nargs='+', default=['user'], help='Input handler. To have a trained AI model play, use sb:ppo2 <model file path> (e.g. ./game.py --controller sb:ppo2 ppo2_model1). The trained model is expected to be in the models directory. The controller sb:ppo2 uses a plugin that wraps stable_baselines and uses the PPO2 algorithm. Default: user (keyboard controlled)')
    parser.add_argument('--playback', action='store', metavar='FILENAME')
    parser.add_argument('--renderer', action='store', default='pg_renderer', metavar='RENDERER', help='Render mode. Either pg_renderer or pg_sprite_renderer for sprite-based graphics. Default: pg_renderer')
    parser.add_argument('--speed', type=int, default=100, help='Game update period in ms. Default: 100')
    parser.add_argument('--seed', type=int, help='Integer seed for environment RNG')
    parser.add_argument('--grid_size', type=int, default=40, help='Size of a side in the square snake grid')
    parser.add_argument('--sound', choices=['on', 'off'], default='on')
    parser.add_argument('--record', metavar='FILENAME')
    args = parser.parse_args()
    controller = load_controller(args.controller[0], args.controller[1:])
    if args.playback:
        arg_env = MemoryPlayback(args.playback)
    else:
        arg_env = SnakeEnv(grid_size=args.grid_size, seed=args.seed)
    pls = [
        [args.renderer, arg_env]
    ]
    if args.sound == 'on':
        pls.append(['sound'])
    if args.record:
        pls.append(['memory_recorder', args.record])
    game = Game(controller, arg_env, args.speed, pls)
    game.run()


