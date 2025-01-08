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


class Decor(pg.sprite.Sprite):
    def __init__(self, pos, surface, hitbox=None):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = pg.Rect(hitbox.x, hitbox.y, hitbox.width, hitbox.height) if hitbox else None


class Collision(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.rect = pg.Rect(pos, size)


class Map:
    def __init__(self):
        self.map = load_tiles()
        self.tile_cache = {}
        self.layers = {}
        self.collidables = pg.sprite.Group()

        for layer in self.map.visible_layers:
            print(getattr(self.map.get_layer_by_name(layer.name), "class"))
            self._process_layer(layer)

        self.tiles = self._create_tiles()
        self.objects = self._create_objects()

    def _process_layer(self, layer):
        class_ = getattr(layer, "class")
        """Process each layer and add it to the appropriate group."""
        match class_:
            case "static":
                self.layers[layer.name] = self._create_layer_tiles(layer)
            case "hitbox":
                self.layers[layer.name] = self._create_layer_decor(layer)
            case "colls":
                self.layers[layer.name] = self._create_layer_collisions(layer)

    def _create_layer_tiles(self, layer):
        return pg.sprite.Group([
            Tile((x * surface.width, y * surface.height), self._get_surface(surface))
            for x, y, surface in layer.tiles()
        ])

    def _create_layer_decor(self, layer):
        decor_group = pg.sprite.Group([
            Decor((obj.x, obj.y), obj.image, self.map.get_object_by_id(obj.hitbox))
            for obj in self.map.objects if obj.image and obj.properties.get("hitbox")
        ])
        self.collidables.add(decor_group)
        return decor_group

    def _create_layer_collisions(self, layer):
        collision_group = pg.sprite.Group([
            Collision((obj.x, obj.y), (obj.width, obj.height))
            for obj in self.map.get_layer_by_name("Collisions")
        ])
        self.collidables.add(collision_group)
        return collision_group

    def _create_tiles(self):
        return pg.sprite.Group([
            Tile((x * surface.width, y * surface.height), surface)
            for layer in self.map.visible_layers if hasattr(layer, "tiles")
            for x, y, surface in layer.tiles()
        ])

    def _create_objects(self):
        return pg.sprite.Group([
            Object((obj.x, obj.y), obj.image)
            for obj in self.map.objects if obj.image
        ])

    def _get_surface(self, surface):
        if surface not in self.tile_cache:
            self.tile_cache[surface] = surface.convert_alpha()
        return self.tile_cache[surface]

    def get_layer(self, screen, layer_name, offset=lambda x: x):
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")
        if DEBUG:
            for tile in self.layers[layer_name]:
                if hasattr(tile, "hitbox"):
                    pg.draw.rect(screen, (0, 255, 0), offset(tile.hitbox), 1)
                if hasattr(tile, "rect"):
                    pg.draw.rect(screen, (255, 0, 0), offset(tile.rect), 1)

            for tile in self.layers["Collisions"]:
                if hasattr(tile, "hitbox"):
                    pg.draw.rect(screen, (0, 255, 0), offset(tile.hitbox), 1)
                if hasattr(tile, "rect"):
                    pg.draw.rect(screen, (255, 0, 0), offset(tile.rect), 1)


        return [
            (tile.image, offset(tile.rect), tile.rect.bottom)
            for tile in self.layers[layer_name]
            if offset(tile.rect).colliderect(screen.get_rect())
        ]


    def draw_layer(self, screen, layer_name, offset=lambda x: x):
        """Draw a specific layer."""
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")

        for tile in self.layers[layer_name]:
            if offset(tile.rect).colliderect(screen.get_rect()):
                screen.blit(tile.image, offset(tile.rect))

    def draw(self, screen, offset=lambda x: x):
        """Draw all layers and tiles."""
        for layer_name in self.layers:
            self.draw_layer(screen, layer_name, offset)


