'''
Write the code of your ship here.
You have to create a main function, 
it will be run at each frame and will control the ship.
'''

from game.api import Ship, Opponent, Block, Generator, Shield, Turret, Engine, Constants


class Globals:
    v = False

def main():

    if not Globals.v:
        Globals.v = True
        Ship.rotate_angle(45)

    # fire turrets
    turrets = Ship.get_blocks("Turret")

    for turret in turrets:
        turret.fire()

        if not turret.is_rotating():

            if turret.get_orientation() == 315:
                turret.rotate(60)
            else:
                turret.rotate(315)
