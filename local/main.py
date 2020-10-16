import pygame
import numpy as np
from lib.interface import Interface, C, Form

# first setup the interface -> to create Form objects
Interface.setup((3200,1600), 'CodeShip', font_color=C.BLACK, FPS=30)

from block import Block, Generator, Shield
from ship import Ship
from bulletsystem import BulletSystem
import time, random

ship = Ship.from_grid(np.array([
    [0,1,1,0],
    [1,4,4,1],
    [3,2,2,3],
    [1,5,5,1],
])[::-1])


ship.compile()

ship.pos[:] = (0,1000)

ship.circular_speed = -0.0025

energies = ship.typed_blocks['Generator']
#energies[0].is_active = False
#energies[1].is_active = False

i = 0

while Interface.running:

    st = time.time()

    pressed, event = Interface.run()
    
    ship.run()

    ship.display()
    BulletSystem.display()

    BulletSystem.run()


    ship.typed_blocks['Turret'][0].fire()

    if pressed[pygame.K_SPACE]:
        if i % 10  == 0:
            #energies = ship.typed_blocks['Generator']
            #random.choice(energies).is_active = False
        
            ship.typed_blocks['Turret'][0].rotate(37)
        i += 1

    t_frame = time.time() - st

    #print(f'FPS: {1/t_frame:.2f}')


