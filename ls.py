import pygame as pg
import pymunk
import pymunk.pygame_util

# Initialize Pygame
pg.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 40

# Set up the game screen
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()

# Pymunk space setup
space = pymunk.Space()
space.gravity = (0, 500)  # Set gravity to something realistic

def add_static_box(space, x, y, width, height):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = x, y
    shape = pymunk.Poly.create_box(body, (width, height))
    space.add(body, shape)
    return shape

def add_kinematic_player(space, x, y, width, height):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = x, y
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.elasticity = 0.9  # Bouncy collisions
    shape.collision_type = 1
    space.add(body, shape)
    return body, shape

# Collision handler for the player
def on_collision_begin(arbiter, space, data):
    print("Collision detected!")
    return True  # Allow the collision to happen

handler = space.add_collision_handler(1, 1)
handler.begin = on_collision_begin

# Add static box and kinematic player
static_box = add_static_box(space, 400, 500, 200, 20)
player_body, player_shape = add_kinematic_player(space, 100, 100, PLAYER_WIDTH, PLAYER_HEIGHT)

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000  # Time step in seconds
    screen.fill((30, 30, 30))   # Clear the screen

    # Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # Handle player movement (manual for kinematic object)
    keys = pg.key.get_pressed()
    velocity = [0, 0]
    if keys[pg.K_LEFT]:
        velocity[0] = -200
    if keys[pg.K_RIGHT]:
        velocity[0] = 200
    if keys[pg.K_UP]:
        velocity[1] = -200
    if keys[pg.K_DOWN]:
        velocity[1] = 200

    # Update player position manually
    player_body.position += pymunk.Vec2d(*velocity) * dt

    # Step the physics simulation
    space.step(dt)

    # Pymunk debugging
    options = pymunk.pygame_util.DrawOptions(screen)
    space.debug_draw(options)

    pg.display.flip()

pg.quit()
