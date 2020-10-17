import pygame
import numpy as np
from lib.interface import Interface, C, Form

# first setup the interface -> to create Form objects
Interface.setup((3200,1600), 'CodeShip', font_color=C.BLACK, FPS=30)

from block import Block, Generator, Shield
from ship import Ship
from bulletsystem import BulletSystem
import time, random

ship1 = Ship.from_grid(1, np.array([
    [0,1,1,0],
    [1,4,4,1],
    [3,2,2,3],
    [1,5,5,1],
])[::-1])

ship2 = Ship.from_grid(2, np.array([
    [0,1,1,0],
    [1,4,4,1],
    [3,2,2,3],
    [1,5,5,1],
])[::-1])

ship1.compile()
ship2.compile()

ship1.pos[:] = (0,1000)
ship2.pos[:] = (2000,1000)

ship2.orien = np.pi
ship2.rotate_surf(np.pi)

ship2.circular_speed = 0.05

BulletSystem.set_ships((ship1, ship2))

gens = ship1.typed_blocks['Engine']

for gen in gens:
    gen.activation_per = 0

gens = ship2.typed_blocks['Engine']

for gen in gens:
    gen.activation_per = 0

i = 0

while Interface.running:

    st = time.time()

    pressed, event = Interface.run()
    
    ship1.run()
    ship2.run()

    ship1.display()
    ship2.display()
    
    BulletSystem.display()

    BulletSystem.run()

    ship1.typed_blocks['Turret'][0].fire()
    ship1.typed_blocks['Turret'][1].fire()

    if pressed[pygame.K_SPACE]:
        if i % 10  == 0:
            #energies = ship.typed_blocks['Generator']
            #random.choice(energies).is_active = False
        
            ship1.typed_blocks['Turret'][0].rotate(320)
        i += 1

    t_frame = time.time() - st

    #print(f'FPS: {1/t_frame:.2f}')


