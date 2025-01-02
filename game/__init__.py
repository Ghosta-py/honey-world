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
            self.screen = pg.Surface((MIN_WIDTH, MIN_HEIGHT))
        else:
            self.display = pg.display.set_mode(pg.Vector2((MIN_WIDTH, MIN_HEIGHT)), pg.SCALED|pg.RESIZABLE|pg.DOUBLEBUF|pg.HWSURFACE)
            self.screen = self.display.copy()

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

    def draw(self):
        self.screen.fill((70, 70, 70))
        self.map.draw(self.screen, self.camera.apply)
        self.test.draw(self.screen, self.camera.apply)
        self.player.draw(self.screen, self.camera.apply)

        if FULL_WINDOW:
            self.display.blit(pg.transform.scale(self.screen, self.display.size), (0, 0))
        else:
            self.display.blit(self.screen, (0, 0))
        pg.display.flip()

    def run(self):
        global last_snapshot_time
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.update(dt)
            self.handle_events()
            self.draw()
        pg.quit()
