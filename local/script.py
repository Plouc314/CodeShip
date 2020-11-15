'''
Write the code of your ship here.
You have to create a main function, 
it will be run at each frame and will control the ship.
'''

from game.api import API, Block, Generator, Shield, Turret, Ship, Opponent
import random

i = 0

def main():
    global i
    i += 1
    if i % 10 == 0:
        turrets = Ship.get_blocks(type='Turret')

        for turret in turrets:

            if not turret.is_rotating():
                turret.rotate(random.randint(0, 360))
        
