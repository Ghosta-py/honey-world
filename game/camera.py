from .settings import *


class Camera:
    def __init__(self, width, height):
        self.offset = pg.Vector2(0, 0)
        self.width = width
        self.height = height
        self.speed = 30

    def follow(self, target):
        size = get_map_size()
        width,  height = size

        self.offset.x += (target.rect.centerx - self.width // 2 - self.offset.x) // self.speed
        self.offset.y += (target.rect.centery - self.height // 2 - self.offset.y) // self.speed

        self.offset.x = max(0, min(self.offset.x, width - self.width))
        self.offset.y = max(0, min(self.offset.y, height - self.height))

    def apply(self, rect):
        return rect.move(-self.offset.x, -self.offset.y)