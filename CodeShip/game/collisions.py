import pygame, numpy as np
from lib.plougame.helper import Delayer
from game.geometry import get_deg, get_norm, to_vect, cal_direction
from data.spec import Spec
from lib.counter import Counter

collision_deco = Delayer(15)

class CollisionSystem:
    '''
    Handeln collision between ships
    '''

    HISTORY_SIZE = 10
    intersect = None
    speed_history = {
        'own': [],
        'opp': []
    }

    @classmethod
    def reset(cls):
        '''
        Clear history of speeds
        '''
        cls.intersect = None
        cls.speed_history = {
            'own': [],
            'opp': []
        }

    @classmethod
    def set_ships(cls, own_ship, opp_ship):
        '''
        Set ships,  
        NOTE: ship must be in correct order.
        '''
        cls.own_ship = own_ship
        cls.opp_ship = opp_ship

    @classmethod
    def update_history(cls):
        '''
        Update history of the speeds.
        '''
        cls.speed_history['own'].append(cls.own_ship.get_speed(scalar=True))
        cls.speed_history['opp'].append(cls.opp_ship.get_speed(scalar=True))

        if len(cls.speed_history['own']) > cls.HISTORY_SIZE:
            cls.speed_history['own'].pop(0)
        
        if len(cls.speed_history['opp']) > cls.HISTORY_SIZE:
            cls.speed_history['opp'].pop(0)

    @classmethod
    def run(cls):
        '''
        Check if the ships are overlaping,
        in that case: make the ships bounce (elastic collisions)
        '''
        cls.update_history()

        if cls.is_collision():
            cls.bounce()

    @classmethod
    @Counter.add_func
    @collision_deco
    def is_collision(cls):
        '''
        Return if a collision occured between the ships AND the intersection point.
        '''
        mask_own = cls.own_ship.get_mask()
        mask_opp = cls.opp_ship.get_mask()

        pos_own = cls.own_ship.get_pos(scaled=True)
        pos_opp = cls.opp_ship.get_pos(scaled=True)

        offset = np.array(pos_own - pos_opp, dtype='int32')

        intersect = mask_opp.overlap(mask_own, offset)

        if intersect is not None:
            cls.intersect = pos_opp + np.array(intersect, dtype=int)
            return True
        else:
            return False
    
    @classmethod
    def bounce(cls):
        '''
        Make own ship bounce after collision
        Set acceleration of own ship.
        '''
        # compensate the ship's motor power
        cls.own_ship.set_auxiliary_acc(-cls.own_ship.get_acc())

        # get mean speed
        own_speed = cls.speed_history['own'][0]
        opp_speed = cls.speed_history['opp'][0]
        speed = (own_speed + opp_speed) / 2
        
        # compute angle of collision
        center = cls.own_ship.get_pos(scaled=True, center=True)

        angle = cal_direction(center, cls.intersect)

        cls.own_ship.speed = -to_vect(speed, angle)

        # add random rotation
        if np.random.random() < .5:
            sign = -1
        else:
            sign = 1
        
        cls.own_ship.circular_speed = sign * Spec.BOUNCE_CIRCULAR_SPEED