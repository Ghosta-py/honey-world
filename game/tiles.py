from .settings import *
from .load import load_tiles


class Tile(pg.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)


class Map:
    def __init__(self):
        self.map = load_tiles()
        self.tile_cache = {}
        self.tiles = pg.sprite.Group([
            Tile((x * surface.width, y * surface.height), surface)
            for layer in self.map.visible_layers if hasattr(layer, "tiles")
            for x, y, surface in layer.tiles()
        ])
        self.objects = pg.sprite.Group([
            Tile((obj.x , obj.y), obj.image)
            for obj in self.map.objects
        ])

    def _get_surface(self, surface):
        if surface not in self.tile_cache:
            self.tile_cache[surface] = surface.convert_alpha()
        return self.tile_cache[surface]

    def draw(self, screen, offset=lambda x: x):
        drawables = [
            (tile.image, offset(tile.rect).topleft)
            for tile in self.tiles
            if offset(tile.rect).colliderect(screen.get_rect())
        ]
        screen.blits(drawables)


