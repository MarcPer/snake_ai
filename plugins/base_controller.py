"""Handles input that is always applied to game (e.g. QUIT command)
"""

import pygame as pg

class BaseController:
    def __init__(self, *args):
        pass

    def get_action(self, state, curr_dir):
        """Handles quit command; further processing needs to be implemented
        in a subclass.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 'QUIT'
            elif curr_dir is None:
                return 0
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return 'QUIT'
                elif event.key == pg.K_r:
                    return 'RESTART'
                return self._process(event.key, state, curr_dir)
        return self._computed_action(state, curr_dir)

    def types(self):
        return ['controller']

    def _process(self, _key, _state, _curr_dir):
        return 0

    def _computed_action(self, state, curr_dir):
        return 0
