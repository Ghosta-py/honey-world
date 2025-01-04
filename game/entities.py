from .settings import *
import pygame as pg
from typing import Dict, List, Optional, Callable


def is_pressed(event, action):
    return event.key in CONFIG.get(action, [])


class Animation:
    def __init__(self, pack: Dict[str, Dict[str, List[pg.Surface]]], variant: str = "base", loop_duration: float = 1.2, one_time: bool = False):
        self.done = False
        self.one_time = one_time
        self.pack = pack
        self.variant = variant
        self.state = "idle"
        self.frames = self.pack[self.state][self.variant]
        self.loop_duration = loop_duration
        self.frame_duration = self._calculate_frame_duration()
        self.frame = 0
        self.timer = 0
        self.current = self.frames[0] if self.frames else None

    def _calculate_frame_duration(self) -> float:
        return self.loop_duration / len(self.frames) if self.frames else float("inf")

    def can_switch_state(self, state: str) -> bool:
        return self.state != state and (self.one_time and not self.done) and state in self.pack

    def switch_to(self, state: str, one_time: bool = False, loop_duration: Optional[float] = None) -> None:
        if state not in self.pack:
            raise ValueError(f"Invalid state: {state}. Available states: {list(self.pack.keys())}")
        if state != self.state:
            self.done = False
            self.one_time = one_time
            self.state = state
            self.frames = self.pack[self.state][self.variant]
            self.loop_duration = loop_duration if loop_duration else self.loop_duration
            self.frame_duration = self._calculate_frame_duration()
            self.frame = 0
            self.timer = 0
            self.current = self.frames[0] if self.frames else None

    def update(self, dt: float) -> None:
        if not self.frames or self.done:
            return

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer %= self.frame_duration
            self.frame += 1
            if self.frame >= len(self.frames):
                if self.one_time:
                    self.done = True
                    self.frame = len(self.frames) - 1
                else:
                    self.frame = 0
            self.current = self.frames[self.frame]

class Entity(pg.sprite.Sprite):
    def __init__(self, pos: tuple, entity_type: str = "goblin", space=None):
        super().__init__()
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(0, 0)
        self.speed = 100
        self.type = entity_type
        self.animation = Animation(ASSETS[self.type])
        self.image = self.animation.current
        self.rect = self.image.get_rect(topleft=self.pos)
        self.mask = pg.mask.from_surface(self.image)
        self.set_hitbox()

        self.state = "idle"
        self.movables = {"roll", "idle", "walk", "run", "jump"}
        self.is_right = True
        self.z_index = self.rect.bottom

        # Pymunk integration
        self.body = pymunk.Body(0.1, 1, body_type=pymunk.Body.DYNAMIC)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size=self.hitbox.size)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5

        if space:
            space.add(self.body, self.shape)

    def set_hitbox(self):
        mask_rect = self.mask.get_bounding_rects()[0]
        self.hitbox = pg.Rect(
            self.pos.x + mask_rect.x,
            self.pos.y + mask_rect.y,
            mask_rect.width,
            mask_rect.height
        )

    def update(self, dt: float) -> None:
        if self.vel.x:
            self.is_right = self.vel.x > 0

        # Update position and velocity via Pymunk
        self.body.velocity = self.vel.x, self.vel.y
        self.pos = pg.Vector2(self.body.position)

        self.set_hitbox()
        self.rect.topleft = self.pos
        self.z_index = self.hitbox.bottom

        if self.animation.can_switch_state(self.state):
            self.animation.switch_to(self.state)
        self.animation.update(dt)
        self.image = self.animation.current

    def draw(self, screen: pg.Surface, offset: Callable = lambda x: x) -> None:
        rect = offset(self.rect)
        if not rect.colliderect(screen.get_rect()):
            return
        image = self.image
        if not self.is_right:
            image = pg.transform.flip(image, True, False)
        screen.blit(image, rect)

    def get_drawable(self, screen, offset=lambda x: x):
        """Return the entity as a drawable with its z-index."""
        rect = offset(self.rect)
        image = self.image
        self.hitbox = offset(self.hitbox)
        pg.draw.rect(screen, (0, 255, 0), self.hitbox, 1)
        if not self.is_right:
            image = pg.transform.flip(image, True, False)
        result = image, rect, self.z_index
        return [result]


class Player(Entity):
    def __init__(self, pos: tuple, space=None):
        super().__init__(pos, entity_type="human", space=space)
        self.keys = {
            "left": False,"right": False, "up": False, "down": False,
            "attack": False, "roll": False, "run": False
        }
        self.immutables = {"attack", "roll"}

    def can_switch_state(self, new_state: str) -> bool:
        if self.state == new_state:
            return False
        if self.state in self.immutables and not self.animation.done:
            return False
        return True

    def update(self, dt: float) -> None:
        """
        It's important to handle immutables before movement states
        """
        # Handle immutable states
        if self.state in self.immutables:
            self.vel = pg.Vector2(0, 0)
            if self.state == "roll" and not self.animation.done:
                if self.vel.length() == 0:
                    direction = pg.Vector2(
                        self.keys["right"] - self.keys["left"],
                        self.keys["down"] - self.keys["up"]
                    )
                self.vel = 5 * self.speed * direction
            elif self.animation.done:
                self.keys[self.state] = False
                self.state = "idle"
                self.animation.switch_to(self.state, loop_duration=1.2)
                self.vel = pg.Vector2(0, 0)

        # Handle movement states (walk/run)
        elif self.keys["left"] or self.keys["right"] or self.keys["up"] or self.keys["down"]:
            new_state = "run" if self.keys["run"] else "walk"
            self.state = new_state
            self.animation.switch_to(self.state)

            current_speed = self.speed * (1.5 if self.state == "run" else 1)
            self.vel.x = (self.keys["right"] - self.keys["left"]) * current_speed
            self.vel.y = (self.keys["down"] - self.keys["up"]) * current_speed

        # Idle state if no keys are pressed
        else:
            if not any(self.keys.values()):
                self.state = "idle"
                self.animation.switch_to(self.state, loop_duration=1.2)
            self.vel = pg.Vector2(0, 0)

        super().update(dt)

    def debug_state(self):
        print(f"State: {self.state}, Velocity: {self.vel}, Animation Done: {self.animation.done}, Is roll: {self.keys["roll"]}", end="\r")

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type in (pg.KEYDOWN, pg.KEYUP):
            pressed = event.type == pg.KEYDOWN
            for action, keys in CONFIG.items():
                if event.key in keys:
                    if action in self.immutables:
                        if pressed and self.can_switch_state(action):
                            self.state = action
                            self.animation.switch_to(self.state, one_time=True, loop_duration=0.2)
                            self.keys[action] = True
                    else:
                        self.keys[action] = pressed

