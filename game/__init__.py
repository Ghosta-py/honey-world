import pygame as pg
from .settings import *
from .load import  load_characters
from .entities import Entity, Player
from .camera import Camera
from .tiles import Map


class Game:
    def __init__(self):
        pg.init()

        if FULL_WINDOW:
            self.display = pg.display.set_mode((0, 0), pg.FULLSCREEN, pg.SCALED|pg.DOUBLEBUF|pg.HWSURFACE)
            self.screen = pg.Surface((MIN_WIDTH, MIN_HEIGHT), pg.SCALED|pg.DOUBLEBUF|pg.HWSURFACE)
        else:
            self.display = pg.display.set_mode(pg.Vector2((MIN_WIDTH, MIN_HEIGHT)), pg.SCALED|pg.RESIZABLE|pg.DOUBLEBUF|pg.HWSURFACE)
            self.screen = self.display.copy()
        self.aspect = self.screen.width / self.screen.height

        self.clock = pg.time.Clock()
        self.running = True
        set_assets(load_characters("assets"))
        self.map = Map()

        self.camera = Camera(self.screen.width, self.screen.height)
        self.player = Player((0, 0))
        self.test = Entity((0, 0))

    def update(self, dt):
        self.player.update(dt)
        self.test.update(dt)
        self.camera.follow(self.player)

    def handle_events(self):
        global FULL_WINDOW
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
                self.running = False
            if keys[pg.K_SPACE]:
                FULL_WINDOW = not FULL_WINDOW
                self.__init__()
            self.player.handle_event(event)

    def add_drawable(self, drawable, target):
        if target:
            drawable += target

    def draw(self):
        self.screen.fill((70, 70, 70))
        drawables = []
        self.map.draw_layer(self.screen, "Base",self.camera.apply)

        self.add_drawable(drawables, self.test.get_drawable(self.screen, self.camera.apply))
        self.add_drawable(drawables, self.player.get_drawable(self.screen, self.camera.apply))
        self.add_drawable(drawables, self.map.get_layer(self.screen, "Decor",self.camera.apply))
        self.add_drawable(drawables, self.map.get_layer(self.screen, "Trees",self.camera.apply))
        drawables = sorted(drawables, key=lambda x: x[2])

        for image, pos, _ in drawables:
            pg.draw.rect(self.screen, (_ % 255, 0, 0), pos, 1)
            self.screen.blit(image, pos)

        new_height = int(self.display.width / (self.aspect))
        scaled_screen = pg.transform.scale(self.screen, (self.display.width, new_height))
        self.display.blit(scaled_screen, (0, 0))
        pg.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.update(dt)
            self.handle_events()
            self.draw()
        pg.quit()
