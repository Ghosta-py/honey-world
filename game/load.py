import pygame as pg
from .settings import *
from pytmx.util_pygame import load_pygame



def load_image(file, alpha=True, colorkey=None):
    try:
        image = pg.image.load(file)
        if alpha:
            image = image.convert_alpha()
    except pg.error as message:
        print("Cannot load image:", file)
        raise SystemExit(message)

    if not alpha:
        image = image.convert()

    if colorkey:
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image

def load_dir(dir, alpha=True, colorkey=None):
    return [load_image(os.path.join(dir, file), alpha, colorkey) for file in os.listdir(dir) if not file.endswith(".png")]

def load_strip(file, size, alpha=True, colorkey=None):
    main = load_image(file, alpha, colorkey)
    strips = []
    for x in range(0, main.get_width(), size[0]):
        strip = pg.Surface(size, pg.SRCALPHA)
        strip.blit(main, (0, 0), (x, 0, size[0], size[1]))
        strips.append(strip)
    return strips

def load_characters(root_dir):
    assets = {}

    for root, _, files in os.walk(root_dir):
        if "Characters" not in root:
            continue

        category = os.path.relpath(root, root_dir).split(os.sep)
        if len(category) < 2:
            continue

        name = category[1].lower()
        if name not in assets:
            assets[name] = {}

        for file in files:
            if not file.endswith(".png"):
                continue

            file_path = os.path.join(root, file)
            base_name, _ = os.path.splitext(file)

            parts = base_name.split("_")
            if len(parts) < 2:
                print(f"File {file} does not follow naming convention.")
                continue

            action = parts[1].lower()
            variant = "base"

            if name == "human":
                if len(parts) > 2 and "_strip" in parts[-1]:
                    variant = "_".join(parts[2:-1]).lower()
                elif len(parts) > 2:
                    variant = parts[0].lower()

            if name not in assets:
                assets[name] = {}
            if action not in assets[name]:
                assets[name][action] = {}

            if variant not in assets[name][action]:
                assets[name][action][variant] = []

            if "_strip" in file:
                strip_info = base_name.split("_strip")[-1]
                try:
                    frame_count = int(strip_info)
                    frame_width = load_image(file_path).get_width() // frame_count
                    frame_height = load_image(file_path).get_height()
                    frames = load_strip(file_path, (frame_width, frame_height))
                except ValueError:
                    print(f"Invalid strip format in file: {file}")
                    continue
            else:
                frames = [load_image(file_path)]

            assets[name][action][variant].extend(frames)

    return assets


def load_tiles():
    tilemap = load_pygame(os.path.join(BASE, "maps", "map2.tmx"))
    set_map_size((tilemap.width * tilemap.tilewidth, tilemap.height * tilemap.tileheight))
    return tilemap

