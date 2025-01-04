from .settings import *
from .load import load_tiles
import pytmx


class Tile(pg.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)

class Object(pg.sprite.Sprite):
    def __init__(self, pos, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)


class Map:
    def __init__(self):
        self.map = load_tiles()
        self.tile_cache = {}
        self.layers = {}

        for layer in self.map.visible_layers:
            self._add_layer(layer.name, layer)

        self.tiles = pg.sprite.Group([
            Tile((x * surface.width, y * surface.height), surface)
            for layer in self.map.visible_layers if hasattr(layer, "tiles")
            for x, y, surface in layer.tiles()
        ])
        self.objects = pg.sprite.Group([
            Object((obj.x , obj.y), obj.image)
            for obj in self.map.objects
            if obj.image
        ])

    def _add_layer(self, layer_name, layer):
        """Add a tile layer to the layers dictionary."""
        if hasattr(layer, "tiles"):
            tiles = [
                Tile((x * surface.width, y * surface.height), self._get_surface(surface))
                for x, y, surface in layer.tiles()
            ]
            self.layers[layer_name] = pg.sprite.Group(tiles)
        elif layer.name == "Trees":
            objects = [
                Object((obj.x, obj.y), self._get_surface(obj.image))
                for obj in layer
            ]
            self.layers[layer_name] = pg.sprite.Group(objects)



    def get_layer(self, screen, layer_name, offset=lambda x: x):
        """Draw a specific layer."""
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")

        drawables = [
            (tile.image, offset(tile.rect), tile.rect.bottom)
            for tile in self.layers[layer_name]
            if offset(tile.rect).colliderect(screen.get_rect())
        ]
        return drawables

    def draw_layer(self, screen, layer_name, offset=lambda x: x):
        """Draw a specific layer."""
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")

        drawables = [
            (tile.image, offset(tile.rect).topleft)
            for tile in self.layers[layer_name]
            if offset(tile.rect).colliderect(screen.get_rect())
        ]
        screen.blits(drawables)

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


