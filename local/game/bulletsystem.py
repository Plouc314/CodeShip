import pygame
import numpy as np
from lib.plougame import Interface, Form, Dimension, C
from game.geometry import get_deg, get_rad
from spec import Spec

# load images
folder = "game/imgs/"

img_bullet = pygame.image.load(folder + 'bullet.png')
img_bullet = pygame.transform.rotate(img_bullet, -90)
img_bullet = pygame.transform.scale(img_bullet, Spec.DIM_BULLET)

img_expl = pygame.image.load(folder + 'explosion.png')
img_expl = pygame.transform.scale(img_expl, Spec.DIM_MAX_EXPL)

class Bullet(Form):
    '''
    Bullet object.  

    Args:
        - pos : the initial position of the bullet (center)
        - orien : the orientation of the bullet (rad)
    '''

    def __init__(self, team, pos, orien, speed=None, damage=None):

        super().__init__(Spec.DIM_BULLET, pos, surface=img_bullet, center=True)

        self.team = team

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
        pos = self.get_pos(scaled=True)

        x = np.cos(-self.orien) * self.speed + pos[0]
        y = np.sin(-self.orien) * self.speed + pos[1]

        self.set_pos((x,y))


class Explosion(Form):
    '''
    Visual effect of an explosion
    '''

    def __init__(self, pos):

        # start with an intermediate dimension
        dim = (Spec.DIM_MAX_EXPL + Spec.DIM_MIN_EXPL)//2

        super().__init__(dim, pos, surface=img_expl, center=True, scale_pos=False)

        self.lifetime = Spec.TIME_EXPL
        self.to_delete = False

    def choose_dim(self):
        '''
        Return a random new dimension.
        '''
        low = Spec.DIM_MIN_EXPL[0]
        high = Spec.DIM_MAX_EXPL[0]
        return np.random.randint(low, high, size=2)

    def update_state(self):
        '''
        Rotate and rescale explosions.  
        Update lifetime
        '''
        self.lifetime -= 1
        if self.lifetime == 0:
            self.to_delete = True
            return

        dim = self.choose_dim()
        self.set_dim(dim, scale=True)

        angle = np.random.randint(360)
        self.rotate(angle)


class BulletSystem:
    '''
    Static object.  
    Manage bullets, explosions.    
    Update position, display, collisions...
    '''
    bullets = []
    explosions = []
    ships = []

    @classmethod
    def set_ships(cls, ships):
        '''
        Set a reference of each ship, use for the collisions.
        '''
        cls.ships = list(ships)

    @classmethod
    def add_bullet(cls, bullet):
        '''
        Add a bullet to be managed by the bullet system.
        '''
        cls.bullets.append(bullet)
    
    @classmethod
    def run(cls):
        '''
        Manage the bullets and explosions,  
        Update the positions, handeln the collisions
        '''
        for expl in cls.explosions:
            expl.update_state()
            
            if expl.to_delete:
                expl.delete()
                cls.explosions.remove(expl)

        for bullet in cls.bullets:
            bullet.update_state()
        
        cls.check_in_dim()
        cls.check_collision()
    
    @classmethod
    def display(cls):
        '''
        Display every bullet & explosion
        '''
        for bullet in cls.bullets:
            bullet.display()
        
        for expl in cls.explosions:
            expl.display()
    
    @classmethod
    def check_in_dim(cls):
        '''
        For each bullet, check if its in the screen dimension,  
        if not: remove the bullet.
        '''
        # get scaled window dimension
        window_x = Dimension.get_x(scaled=True)
        window_y = Dimension.get_y(scaled=True)

        for bullet in cls.bullets:
            x, y = bullet.get_pos()
            
            if not (0 < y < window_y) or not (0 < x < window_x):
                # remove bullet
                bullet.delete()
                cls.bullets.remove(bullet)

    @classmethod
    def check_collision(cls):
        '''
        Check if one of the ship has been hit by one of the bullet.
        '''
        for ship in cls.ships:
            mask_ship = ship.get_mask()

            for bullet in cls.bullets:
                
                if bullet.team == ship.team:
                    continue

                pos_bullet = bullet.get_pos(scaled=True)
                mask_bullet = bullet.get_mask()

                pos_ship = ship.get_pos(scaled=True)

                offset = np.array(pos_bullet - pos_ship, dtype='int32')

                intersect = mask_ship.overlap(mask_bullet, offset)

                if not intersect is None: 
                    # collision occured
                    ship.handeln_collision(bullet, pos_bullet)
                    cls.handeln_collision(bullet, pos_bullet)

    @classmethod
    def handeln_collision(cls, bullet, intersect):
        '''
        Remove bullet.  
        Create an explosion object.
        '''
        bullet.delete()
        cls.bullets.remove(bullet)

        expl = Explosion(intersect)
        cls.explosions.append(expl)

        