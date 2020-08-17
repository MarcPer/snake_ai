"""Renders game state on screen using PyGame.
"""

import pygame as pg
from plugins.base_renderer import BaseRenderer

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

class PgRenderer(BaseRenderer):
    def __init__(self, env):
        self.grid_size = env.grid_size
        self.scale_factor = _TARGET_DISPLAY_SIZE // self.grid_size
        self.arena_size = env.grid_size * self.scale_factor
        self.header = pg.Surface(size=(self.arena_size, _HEADER_SIZE), depth=8)
        self.header_rect = self.header.get_rect(topleft=(0, 0))
        self.arena = pg.Surface(size=(self.arena_size, self.arena_size), depth=8)
        self.arena_rect = self.arena.get_rect(topleft=(0, _HEADER_SIZE))
        self.screen = pg.display \
                        .set_mode(size=(self.arena_size, self.arena_size + _HEADER_SIZE), depth=8)
        self.arena.set_palette([_BLACK, _BLUE, _GREEN, _RED, _WHITE, _GRAY])
        self.blink_count = 0

    def set_caption(self, text):
        """Appends text to base caption."""
        if not text:
            return
        pg.display.set_caption(f"{_BASE_CAPTION} - {text}")

    def render(self, state, score, info):
        """Read raw state and convert to pixel array. Each cell on the raw grid should
        be inflated by scale_factor, so it becomes a scale_factor x scale_factor pixel array.
        """
        pix_array = state.squeeze().T.reshape(self.grid_size, self.grid_size) \
                         .repeat(self.scale_factor, axis=0).repeat(self.scale_factor, axis=1)
        pg.surfarray.blit_array(self.arena, pix_array)
        self.screen.blit(self.arena, self.arena_rect)

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
            if info['is_playback']:
                text = "Press 'Space' to continue or 'R' to restart"
            else:
                text = "Press 'R' to restart"
            go_surf, go_rect = create_text(
                text, _BIG_FONT, _WHITE,
                (arena_center, arena_center + _HEADER_SIZE + _BIG_FONT_SIZE),
                'center')
            self.screen.blit(go_surf, go_rect)

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
