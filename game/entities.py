from .settings import *
import pygame as pg

def is_pressed(event, action):
    return event.key in CONFIG.get(action, [])


class Animation:
    def __init__(self, pack, variant="base", loop_duration=1.2):
        self.pack = pack
        self.variant = variant
        self.state = "idle"
        self.frames = self.pack[self.state][self.variant]
        self.loop_duration = loop_duration
        self.frame_duration = loop_duration / len(self.frames) if self.frames else 0
        self.frame = 0
        self.timer = 0
        self.current = self.frames[0] if self.frames else None

    def switch_to(self, state):
        if state != self.state and state in self.pack:
            self.state = state
            self.frames = self.pack[self.state][self.variant]
            self.frame_duration = self.loop_duration / len(self.frames) if self.frames else 0
            self.frame = 0
            self.timer = 0
            self.current = self.frames[0] if self.frames else None

    def update(self, dt):
        if not self.frames:
            return

        self.timer += dt
        if self.timer % self.frame_duration <= dt:
            self.frame = (self.frame + 1) % len(self.frames)
            self.current = self.frames[self.frame]


class Entity(pg.sprite.Sprite):
    def __init__(self, pos, entity_type="goblin"):
        super().__init__()
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(0, 0)
        self.speed = 100

        self.type = entity_type
        self.animation = Animation(ASSETS[self.type])
        self.image = self.animation.current
        self.rect = self.image.get_rect(topleft=self.pos)

        self.map_size = get_map_size()
        self.map_width, self.map_height = self.map_size

        self.state = "idle"
        self.is_right = True

    def update(self, dt):
        if self.vel.x:
            self.is_right = self.vel.x > 0

        self.pos += self.vel * dt
        self.pos.x = max(0, min(self.pos.x, self.map_width - self.rect.width))
        self.pos.y = max(0, min(self.pos.y, self.map_height - self.rect.height))
        self.rect.topleft = self.pos

        self.animation.switch_to(self.state)
        self.animation.update(dt)
        self.image = self.animation.current

    def draw(self, screen, offset=lambda x: x):
        rect = offset(self.rect)
        if not rect.colliderect(screen.get_rect()):
            return
        image = self.image.copy()
        if not self.is_right:
            image = pg.transform.flip(self.image, True, False)
        screen.blit(image, offset(self.rect))


class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, entity_type="human")
        self.keys = {"left": False, "right": False, "up": False, "down": False}

    def update(self, dt):
        self.vel.x = (self.keys["right"] - self.keys["left"]) * self.speed
        self.vel.y = (self.keys["down"] - self.keys["up"]) * self.speed

        self.state = "walk" if self.vel.length() > 0 else "idle"
        super().update(dt)

    def handle_event(self, event):
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            pressed = event.type == pg.KEYDOWN
            for action in self.keys:
                if is_pressed(event, action):
                    self.keys[action] = pressed

