"""Renders game state on screen using PyGame.
"""

import pygame as pg
import numpy as np
from plugins.base_renderer import BaseRenderer
from plugins.snake_env import SnakeEnv
from os import path

pg.font.init()
pg.display.init()
_TARGET_DISPLAY_SIZE = 600
_HEADER_SIZE = 50 # Where score and other info is shown
_BASE_CAPTION = "Snake AI"
_BLACK = (0, 0, 0)
_BLUE = (0, 0, 255)
_GREEN = (0, 255, 0)
_RED = (255, 0, 0)
_WHITE = (255, 255, 255)
_LIGHT_GRAY = (200, 200, 200)
_GRAY = (50, 50, 50)
_FONT = pg.font.Font(None, 26)
_BIG_FONT_SIZE = 42
_BIG_FONT = pg.font.Font(None, _BIG_FONT_SIZE)

            


        
class PgSpriteRenderer(BaseRenderer):
    def __init__(self, env):
        BaseRenderer.__init__(self, env)
        self.grid_size = env.grid_size
        self.scale_factor = _TARGET_DISPLAY_SIZE // self.grid_size
        self.arena_size = env.grid_size * self.scale_factor
        self.screen = pg.display \
                        .set_mode(size=(self.arena_size, self.arena_size + _HEADER_SIZE), depth=8)
        self.header = pg.Surface(size=(self.arena_size, _HEADER_SIZE), depth=8)
        self.header = self.header.convert()
        self.header_rect = self.header.get_rect(topleft=(0, 0))
        self.background = pg.Surface(size=(self.arena_size, self.arena_size))
        self.background.convert()
        self.background.fill(_BLACK)
        images = self.load_spritesheet('spritesheet.png')
        self.im_snake_head = images[0]
        self.im_snake_body = images[1]
        self.im_snake_tail = images[2]
        self.im_snake_curve = images[3]
        self.im_apple = pg.transform.rotate(images[4], 270)
        self.head = None
        self.tail = None
        self.dirty_rects = []
        self.blink_count = 0

    def load_spritesheet(self, filename, tile_size=16, colorkey=None):
        fullpath = path.join('data', filename)
        try:
            image_sheet = pg.image.load(fullpath)
        except pg.error as message:
            print("Cannot load spritesheet file:", fullpath)
            raise SystemExit(message)
        image_sheet = image_sheet.convert()

        sheet_rect = image_sheet.get_rect()
        sheet_width = sheet_rect.width
        sheet_height = sheet_rect.height
        images = []
        for y in range(0, sheet_height // tile_size):
            for x in range(0, sheet_width // tile_size):
                rect = pg.Rect((x*tile_size, y*tile_size), (tile_size, tile_size))
                img = pg.Surface(rect.size).convert()
                img.blit(image_sheet, (0, 0), rect)
                if colorkey is not None:
                    if colorkey is -1:
                        colorkey = img.get_at((0, 0))
                    img.set_colorkey(colorkey, pg.RLEACCEL)
                img = pg.transform.scale(img, (self.scale_factor, self.scale_factor))
                images.append(img)
        return images

    def set_caption(self, text):
        """Appends text to base caption."""
        if not text:
            return
        pg.display.set_caption(f"{_BASE_CAPTION} - {text}")

    def blit_snake(self, snake, curr_dir):
        if not snake:
            return
        for i, pos in enumerate(snake):
            next_dir = None
            if i == 0:
                direction = curr_dir
                image = pg.Surface.copy(self.im_snake_head)
            elif i == len(snake) - 1:
                direction, next_dir = self.get_direction(snake[i-1:])
                image = pg.Surface.copy(self.im_snake_tail)
            else:
                direction, next_dir = self.get_direction(snake[i-1: i+2])
                image = self.get_body_image(direction, next_dir)
            snake_rect = pg.Rect(
                (pos[1] * self.scale_factor, pos[0] * self.scale_factor + _HEADER_SIZE),
                (self.scale_factor, self.scale_factor)
            )
            if next_dir is None:
                image = self.rotate(image, direction)
            self.screen.blit(image, snake_rect)
            self.dirty_rects.append(snake_rect)

    def get_body_image(self, dir1, dir2):
        if 'l' in [dir1, dir2]:
            if 'r' in [dir1, dir2]:
                return pg.Surface.copy(self.im_snake_body)
            if 'd' in [dir1, dir2]:
                return pg.transform.rotate(self.im_snake_curve, 270)
            return pg.transform.rotate(self.im_snake_curve, 180)
        if 'd' in [dir1, dir2]:
            if 'u' in [dir1, dir2]:
                return pg.transform.rotate(self.im_snake_body, 90)
            if 'r' in [dir1, dir2]:
                return pg.Surface.copy(self.im_snake_curve)
        return pg.transform.rotate(self.im_snake_curve, 90)

    def get_direction(self, snake_section):
        """Returns relative directions of a snake segment, so that the proper
        tile can be chosen for drawing.
        
        Returns two directions, the value being one of 'u', 'd', 'r', 'l'.
        Given a 3-element section of the snake, the first direction is
        the one that takes the element from i=1 to i=0, i being the section index.
        For example, if the element i=0 has y=1 and i=1 has y=2, the direction
        should be 'u', since upwards is the direction of decreasing y.
        
        The second direction is the one that takes element i=1 to i=2.
        For example, if the element i=1 has x=3 and i=2 has x=4, the direction is
        'r', the direction if increasing x.

        If given a 2-element section, the element i=1 represents the end of the snake
        and therefore only the first direction is returned, the other output being None.
        """
        sec_other = snake_section[0]
        sec_curr = snake_section[1]
        if sec_curr[0] - sec_other[0] < 0:
            direction = 'd'
        elif sec_curr[0] - sec_other[0] > 0:
            direction = 'u'
        elif sec_curr[1] - sec_other[1] < 0:
            direction = 'r'
        else:
            direction = 'l'

        if len(snake_section) < 3:
            return direction, None

        sec_other = snake_section[2]
        if sec_curr[0] - sec_other[0] < 0:
            next_direction = 'd'
        elif sec_curr[0] - sec_other[0] > 0:
            next_direction = 'u'
        elif sec_curr[1] - sec_other[1] < 0:
            next_direction = 'r'
        else:
            next_direction = 'l'
        return direction, next_direction

    def rotate(self, surf, direction):
        if direction == 'r':
            return pg.transform.rotate(surf, 180)
        elif direction == 'd':
            return pg.transform.rotate(surf, 90)
        elif direction == 'u':
            return pg.transform.rotate(surf, 270)
        else:
            return surf


    def render(self, state, env, score, info):
        """Read raw state and convert to pixel array. Each cell on the raw grid should
        be inflated by scale_factor, so it becomes a scale_factor x scale_factor pixel array.
        """
        for rect in self.dirty_rects:
            self.screen.blit(self.background, rect)
        self.dirty_rects = []
        self.blit_snake(env.snake, env.curr_dir)

        # Apple
        if env.apple:
            apple_rect = pg.Rect(
                (env.apple[1] * self.scale_factor, env.apple[0] * self.scale_factor + _HEADER_SIZE),
                (self.scale_factor, self.scale_factor)
            )
            self.screen.blit(self.im_apple, apple_rect)
            self.dirty_rects.append(apple_rect)
        
        
        # Score
        self.header.fill(_BLACK)
        text_surf, text_rect = create_text(f"Score: {score}", _FONT, _WHITE, (10, 10))
        self.header.blit(text_surf, text_rect)

        if info['is_playback']:
            if self.blink_count < 30:
                pb_surf, pb_rect = create_text(
                    f"-- Playback --", _FONT, _LIGHT_GRAY,
                    (self.header_rect.centerx, self.header_rect.bottom - 10), 'midbottom')
                self.header.blit(pb_surf, pb_rect)
            self.blink_count += 1
            if self.blink_count >= 60:
                self.blink_count = 0

        # Blit header
        self.screen.blit(self.header, self.header_rect)

        # Divider
        pg.draw.line(self.screen, _GRAY, (0, _HEADER_SIZE), (self.arena_size, _HEADER_SIZE))

        # Game over
        if info['dead']:
            arena_center = self.arena_size // 2
            go_surf, go_rect = create_text(
                "Game Over", _BIG_FONT, _WHITE, (arena_center, arena_center + _HEADER_SIZE),
                'center')
            self.screen.blit(go_surf, go_rect)
            self.dirty_rects.append(go_rect)
            if info['is_playback']:
                text = "Press 'Space' to continue or 'R' to restart"
            else:
                text = "Press 'R' to restart"
            key_surf, key_rect = create_text(
                text, _BIG_FONT, _WHITE,
                (arena_center, arena_center + _HEADER_SIZE + _BIG_FONT_SIZE),
                'center')
            self.dirty_rects.append(key_rect)
            self.screen.blit(key_surf, key_rect)

        pg.display.flip()

def create_text(text, font, color, pos, pos_mode='topleft'):
    """Creates a text surface with rendered text and corresponding rect.
    """
    text_surf = font.render(text, True, color, _BLACK)
    if pos_mode == 'topleft':
        text_rect = text_surf.get_rect(topleft=pos)
    elif pos_mode == 'center':
        text_rect = text_surf.get_rect(center=pos)
    elif pos_mode == 'midbottom':
        text_rect = text_surf.get_rect(midbottom=pos)

    return text_surf, text_rect
