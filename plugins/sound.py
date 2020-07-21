"""Play sounds.
"""

import pygame as pg
from os import path
from plugins.base_sound import BaseSound

pg.mixer.pre_init(buffer=128)
pg.mixer.init()

def load_sound(name):
    class NoneSound:
        def play(self):
            pass
    if not pg.mixer:
        return NoneSound()
    fullname = path.join('data', name)
    try:
        sound = pg.mixer.Sound(fullname)
    except pg.error as message:
        print("Could not load sound:", name)
        raise SystemExit(message)
    return sound
    

class Sound(BaseSound):
    """Manages game sounds.
    """
    def __init__(self, *_args):
        self.eat_snd = load_sound('eat.wav')

    def play_eat(self):
        """Play apple eating sound.
        """
        self.eat_snd.play()

    def types(self):
        return ["sound"]
