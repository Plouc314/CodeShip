import pygame
import numpy as np
from lib.interface import Interface, C, Form
from block import Block, Energie, Shield
from ship import Ship

Interface.setup((1600,1600), 'CodeShip', font_color=C.BLACK)

ship = Ship((500,500), C.BLUE)

ship.set_blocks(np.array([
    [0,4,0],
    [1,2,1],
    [2,3,2]
]))

ship.compile()

f = Form((100,100), (1000,1000))

a = 0

while Interface.running:
    pressed, event = Interface.run()
    
    ship.display()

    #f.rotate(a)
    f.display()

    if pressed[pygame.K_SPACE]:
        ship.form.set_pos((700, 500), scale=True)

