"""User plugin: reads keyboard input to select game actions.
"""

import pygame as pg
from plugins.base_controller import BaseController

# Possible actions
# 'QUIT': End game
# 0: Do nothing
# 1: Turn left
# 2: Turn right
_ACT_QUIT = 'QUIT'
_ACT_NOTHING = 0
_ACT_LEFT = 1
_ACT_RIGHT = 2
class User(BaseController):
    """Keyboard based input handling. Used for normal gameplay with arrows.
    """
    def _process(self, key, _state, curr_dir):
        action = 0
        if key == pg.K_DOWN and curr_dir == 'l': action = _ACT_LEFT
        elif key == pg.K_DOWN and curr_dir == 'r': action = _ACT_RIGHT
        elif key == pg.K_UP and curr_dir == 'l': action = _ACT_RIGHT
        elif key == pg.K_UP and curr_dir == 'r': action = _ACT_LEFT
        elif key == pg.K_RIGHT and curr_dir == 'd': action = _ACT_LEFT
        elif key == pg.K_RIGHT and curr_dir == 'u': action = _ACT_RIGHT
        elif key == pg.K_LEFT and curr_dir == 'd': action = _ACT_RIGHT
        elif key == pg.K_LEFT and curr_dir == 'u': action = _ACT_LEFT
        return action
