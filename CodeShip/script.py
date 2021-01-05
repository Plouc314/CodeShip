'''
Write the code of your ship here.
You have to create a main function, 
it will be run at each frame and will control the ship.
'''

from game.api import API, Block, Generator, Shield, Turret, Ship, Opponent
import random

class Foo:
    v = False

def main():

    #Ship.set_power_engines(1)

    if not Foo.v:
        Foo.v = True
        Ship.rotate(90)

    # fire turrets
    turrets = Ship.get_blocks("Turret")

    for turret in turrets:
        turret.fire()

        if not turret.is_rotating():

            if turret.get_orientation() == 315:
                turret.rotate(60)
            else:
                turret.rotate(315)
