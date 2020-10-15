import pygame
import numpy as np
from lib.interface import Interface, C, Form
from block import Block, Energie, Shield
from ship import Ship
import time

Interface.setup((3200,1600), 'CodeShip', font_color=C.BLACK)


ship = Ship.from_grid(np.array([
    [0,1,1,0],
    [1,4,4,1],
    [3,2,2,3],
    [1,5,5,1],
]))

ship.compile(180)

ship.pos[:] = (0,1000)


ship.circular_acc = -0.00025

while Interface.running:

    pressed, event = Interface.run()
    
    ship.display()

    ship.update_state()

    


