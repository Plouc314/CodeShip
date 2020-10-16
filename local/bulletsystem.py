import pygame
import numpy as np
from lib.interface import Interface, Form, C
from geometry import get_deg, get_rad
from spec import Spec

img_bullet = pygame.image.load('imgs/bullet.png')
img_bullet = pygame.transform.rotate(img_bullet, -90)
img_bullet = pygame.transform.scale(img_bullet, Spec.DIM_BULLET)

class Bullet(Form):
    '''
    Bullet object.  

    Args:
        - pos : the initial position of the bullet (center)
        - orien : the orientation of the bullet (rad)
    '''

    def __init__(self, pos, orien, speed=None, damage=None):

        super().__init__(Spec.DIM_BULLET, pos, surface=img_bullet, center=True)

        # rotate the bullet according to its orientation
        self.rotate(get_deg(orien))

        self.orien = orien

        if speed == None:
            self.speed = Spec.SPEED_BULLET
        else:
            self.speed = speed
        
        if damage == None:
            self.damage = Spec.DAMAGE_BULLET
        else:
            self.damage = damage
    
    def update_state(self):
        '''
        Update the position of the bullet.
        '''
        x = np.cos(-self.orien) * self.speed + self.pos[0]
        y = np.sin(-self.orien) * self.speed + self.pos[1]

        self.set_pos((x,y))

class BulletSystem:
    '''
    Static object.  
    Manage every bullet,  
    Update position, display, collisions
    '''
    bullets = []

    @classmethod
    def add_bullet(cls, bullet):
        '''
        Add a bullet to be managed by the bullet system.
        '''
        cls.bullets.append(bullet)
    
    @classmethod
    def run(cls):
        '''
        Manage the bullets,  
        Update the positions, handeln the collisions
        '''
        for bullet in cls.bullets:
            bullet.update_state()
        
        cls.check_in_dim()
    
    @classmethod
    def display(cls):
        '''
        Display every bullet
        '''
        for bullet in cls.bullets:
            bullet.display()
    
    @classmethod
    def check_in_dim(cls):
        '''
        For each bullet, check if its in the screen dimension,  
        if not: remove the bullet.
        '''
        # get scaled window dimension
        window_x = Interface.dim.rx
        window_y = Interface.dim.ry

        for bullet in cls.bullets:
            x, y = bullet.pos
            
            if not (0 < y < window_y) or not (0 < x < window_x):
                # remove bullet
                bullet.delete()
                cls.bullets.remove(bullet)
