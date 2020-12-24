import pygame
import numpy as np
from lib.plougame import Interface, Form, Dimension, C
from game.geometry import get_deg, get_rad
from lib.spec import Spec

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
        self.mask = self.get_mask()

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
    game_client = None
    bullets = []
    explosions = []
    own_ship = None

    @classmethod
    def set_ship(cls, own_ship):
        '''
        Set a reference of own ship, use for the collisions.
        '''
        cls.own_ship = own_ship

    @classmethod
    def reset(cls):
        '''
        Reset the bulletsystem.
        '''
        cls.bulletts = []
        cls.explosions = []
        cls.own_ship = None

    @classmethod
    def add_bullet(cls, bullet):
        '''
        Add a bullet to be managed by the bullet system.
        '''
        cls.bullets.append(bullet)
    
    @classmethod
    def get_bullets_by_team(cls, team):
        '''
        Return all the bullets of the specified team.
        '''
        selected_bullets = []
        for bullet in cls.bullets:
            if bullet.team == team:
                selected_bullets.append(bullet)
        
        return selected_bullets

    @classmethod
    def erase_bullets_by_team(cls, team):
        '''
        Erase bullets of specified team.
        '''
        for bullet in cls.bullets:
            if bullet.team == team:
                cls.bullets.remove(bullet)

    @classmethod
    def get_bullet_by_pos(cls, pos, margin=2):
        '''
        Return the bullet with the specified position (unscaled),  
        Take a margin to catch any potential miss truncated,  
        if no bullet is found: return None
        '''
        pos = [int(pos[0]), int(pos[1])]

        for bullet in cls.bullets:
            
            is_it = True
            x, y = bullet.get_pos()
            x = int(x)
            y = int(y)

            if not x - margin <= pos[0] <= x + margin:
                is_it = False

            if not y - margin <= pos[1] <= y + margin:
                is_it = False

            if is_it:
                return bullet
            
    @classmethod
    def update_opp_bullets(cls):
        '''
        Update the opponent bullets.
        '''
        cls.erase_bullets_by_team(Spec.OPP_TEAM)

        cls.bullets.extend(cls.game_client.bullets)

        cls.game_client.bullets = []

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
        Display every bullet & explosion,  
        '''
        
        for bullet in cls.bullets:
            pos = np.array(bullet.get_pos(scaled=True))
            bullet.display(pos=pos)
        
        for expl in cls.explosions:
            pos = np.array(expl.get_pos(scaled=True))
            expl.display(pos=pos)
    
    @classmethod
    def check_in_dim(cls, margin_factor=2):
        '''
        For each bullet, check if its in the screen dimension,
        with a margin factor to handeln ships moving outside initial screen.  
        if not: remove the bullet.
        '''
        # get scaled window dimension
        window_x = margin_factor*Dimension.get_x(scaled=True)
        window_y = margin_factor*Dimension.get_y(scaled=True)

        for bullet in cls.bullets:
            x, y = bullet.get_pos(scaled=True)
            
            if not (0 < y < window_y) or not (0 < x < window_x):
                # remove bullet
                bullet.delete()
                cls.bullets.remove(bullet)

    @classmethod
    def check_collision(cls):
        '''
        Check if own ship has been hit by one of the bullet.
        '''
        mask_ship = cls.own_ship.get_mask()

        for bullet in cls.bullets:
            
            if bullet.team == cls.own_ship.team:
                continue

            pos_bullet = bullet.get_pos(scaled=True)

            pos_ship = cls.own_ship.get_pos(scaled=True)

            offset = np.array(pos_bullet - pos_ship, dtype='int32')

            intersect = mask_ship.overlap(bullet.mask, offset)

            if not intersect is None: 
                # collision occured
                cls.own_ship.handeln_collision(bullet, pos_bullet)
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

        