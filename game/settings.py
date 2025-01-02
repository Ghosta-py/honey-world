import os
import pygame as pg


BASE = os.path.abspath(".")
ASSETS_DIR = os.path.join(BASE, "assets")
ASSETS = dict()

SCALE = 2
MIN_WIDTH = 720//SCALE
MIN_HEIGHT = 576//SCALE

STRIP_WIDTH = 96
STRIP_HEIGHT = 64

MAP_SIZE = None

CONFIG = {
    "left": {pg.K_LEFT, pg.K_a},
    "right": {pg.K_RIGHT, pg.K_d},
    "up": {pg.K_UP, pg.K_w},
    "down": {pg.K_DOWN, pg.K_s},
}

FULL_WINDOW = False

TYPES = set(os.listdir(ASSETS_DIR))
for path in os.listdir(ASSETS_DIR):
    if path.endswith(".png"):
        TYPES.remove(path)

def set_assets(assets):
    global ASSETS
    ASSETS |= assets

def set_map_size(size):
    global MAP_SIZE
    MAP_SIZE = size

def get_map_size():
    return MAP_SIZE
NAMEING_CONVENTION = "{NAME}_{ACTION}_{IMAGE_TYPE}{FRAME_COUNT}"
