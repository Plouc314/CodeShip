'''
Write the code of your ship here.
You have to create a main function, 
it will be run at each frame and will control the ship.
'''

from game.api import API, Block, Generator, Shield, Turret, Ship, Opponent
import random

def main():

    #opp_pos = Opponent.get_position()
    #own_pos = Ship.get_position()

    #dist = ((opp_pos[0] - own_pos[0])**2 + (opp_pos[1] - own_pos[1])**2)**0.5

    #if dist < 1000:
    Ship.set_power_engines(1)

    # fire turrets
    turrets = Ship.get_blocks("Turret")

    for turret in turrets:
        turret.fire()

        if not turret.is_rotating():

            if turret.get_orientation() == 315:
                turret.rotate(60)
            else:
                turret.rotate(315)



#class Obj:
#    def __init__(self, a):
#        self.a = int(a)
#
#def foo():
#    def r():
#        Obj('a')
#    return r
#def a():
#    b()
#def b():
#    foo()()
#a()