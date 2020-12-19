import pygame, numpy as np
from lib.plougame.helper import Delayer
from game.geometry import get_deg
from spec import Spec

collision_deco = Delayer(15)

class CollisionSystem:
    '''
    Handeln collision between ships
    '''

    @classmethod
    def set_ships(cls, own_ship, opp_ship):
        '''
        Set ships,  
        NOTE: ship must be in correct order.
        '''
        cls.own_ship = own_ship
        cls.opp_ship = opp_ship

    @classmethod
    def run(cls):
        '''
        Check if the ships are overlaping,
        in that case: make the ships bounce (elastic collisions)
        '''
        if cls.is_collision():
            cls.bounce()

    @classmethod
    @collision_deco
    def is_collision(cls):
        '''
        Return if a collision occured between the ships.
        '''

        mask_own = cls.own_ship.get_mask()
        mask_opp = cls.opp_ship.get_mask()

        pos_own = cls.own_ship.get_pos(scaled=True)
        pos_opp = cls.opp_ship.get_pos(scaled=True)

        offset = np.array(pos_own - pos_opp, dtype='int32')

        intersect = mask_opp.overlap(mask_own, offset)

        return not intersect is None
    
    @classmethod
    def bounce(cls):
        '''
        Make own ship bounce after collision
        Set acceleration of own ship.
        '''
        # compensate the ship's motor power
        cls.own_ship.set_auxiliary_acc(-Spec.BOUNCE_ACC-cls.own_ship.acc)

        # inverse ship speed
        cls.own_ship.speed *= -1

        # add random rotation
        dif = (2*np.random.random() - 1) * Spec.BOUNCE_ROTATION_MAGNITUDE

        cls.own_ship.orien += dif