import pygame
import numpy as np
from lib.plougame import Form, C
from lib.plougame.helper import Delayer
from game.bulletsystem import Bullet, BulletSystem
from game.geometry import get_deg, get_rad, get_polar, get_cartesian, get_length
from spec import Spec


# load imgs
folder = "game/imgs/"

img_shield = pygame.image.load(folder + 'shield.png')
img_shield = pygame.transform.scale(img_shield, Spec.DIM_ITEM)

img_generator = pygame.image.load(folder + 'generator.png')
img_generator = pygame.transform.scale(img_generator, Spec.DIM_ITEM)

img_engine = pygame.image.load(folder + 'engine.png')
img_engine = pygame.transform.scale(img_engine, Spec.DIM_ITEM)

img_turret = pygame.image.load(folder + 'turret.png')
img_turret = pygame.transform.rotate(img_turret, 270)
img_turret = pygame.transform.scale(img_turret, Spec.DIM_TURRET)

class Block(Form):

    name = 'Block'
    ship = None

    # activate/deactivate signal
    signal = Form(Spec.DIM_SIGNAL, (0,0))

    def __init__(self, coord, color=None, image=None, hp=None):

        if hp == None:
            self.hp = Spec.HP_BLOCK
        else:
            self.hp = hp

        self.active = True
        self.power_output = 0
        
        # for the ship to know if it needs to update the block on the surface
        self.has_color_changed = False

        # hit
        self.is_hit = False
        self.hit_effect_time = 0

        self.coord = np.array(coord, dtype='int16')

        # set up the surface
        if color == None:
            self.color = C.BLUE
        else:
            self.color = color
        
        if image == None:
            with_font = False
        else:
            with_font = True

        # the position doesn't matter as the block's surface will be compiled in the ship image
        super().__init__(Spec.DIM_BLOCK, (0,0), color=self.color, 
                        surface=image, with_font=with_font, marge=True)

        self.set_marge_width(Spec.DIM_BLOCK_MARGE, scale=True)

    def hit(self, damage):
        '''
        Hit the block, with a damage amound,  
        start the hit effect.
        '''
        self.hp -= damage

        self.set_color(C.RED)
        self.is_hit = True
        self.hit_effect_time = 0

    def set_color(self, color, update_original=False):
        '''
        Set the color of the block, set a call to update color.  
        If `update_original=True`, change permanent color of the block.
        '''
        super().set_color(color, marge=True)
        self.has_color_changed = True

        if update_original:
            self.color = color

    def run(self):
        '''
        '''
        self.run_hit_effect()

    def run_hit_effect(self):
        '''
        In case of hit effect, 
        update the effect duration and potentialy stop the effect.
        '''
        # check for hit effect
        if self.is_hit:
            self.hit_effect_time += 1

            if self.hit_effect_time == Spec.HIT_DURATION:
                self.is_hit = False
                self.set_color(self.color)

    def get_power_output(self):

        if self.is_active:
            return self.power_output
        else:
            return 0

    @property
    def is_active(self):
        return self.active
    
    @is_active.setter
    def is_active(self, value):
        self.active = value
        # update the signal on the ship
        if self.name != 'Block':
            self.ship.update_signal(self)

    def get_signal_form(self):
        '''
        Return the signal Form object with the correct color.  
        '''
        if self.active:
            self.signal.set_color(C.LIGHT_GREEN)
        else:
            self.signal.set_color(C.LIGHT_RED)
        
        return self.signal

    def __str__(self):
        return f'{self.name} object at {self.coord}'

    def __repr__(self):
        return self.__str__()

    def display(self):
        super().display(marge=True)


class Generator(Block):

    name = 'Generator'

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        self.power_output = Spec.POWER_ENERGIE

        # blit the generator image on the surface -> can resize the image
        self.get_surface('original').blit(img_generator, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(self.get_surface('original'))

    def set_color(self, color, update_original=False):
        '''
        Set the color of the block, set a call to update color 
        '''
        super().set_color(color, update_original=update_original)
        surf = pygame.Surface(Spec.DIM_BLOCK)
        surf.fill(color)
        surf.blit(img_generator, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(surface=surf)

class Engine(Block):

    name = 'Engine'

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        self.power_output = -Spec.POWER_CONS_MOTOR
        self.activation_per = 1 # % of activation

        # blit the engine image on the surface -> can resize the image
        self.get_surface('original').blit(img_engine, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(self.get_surface('original'))
    
    @property
    def is_active(self):
        return self.active

    @is_active.setter
    def is_active(self, value):
        if value == False:
            self.activation_per = 0
            self.active = False
        else:
            # by default: activate the engine on full power
            self.activation_per = 1
            self.active = True

        self.ship.update_signal(self)

    def get_engine_power(self):
        '''Return the force generated by the engine.'''
        return Spec.MOTOR_POWER * self.activation_per

    def set_color(self, color, update_original=False):
        '''
        Set the color of the block, set a call to update color 
        '''
        super().set_color(color, update_original=update_original)
        surf = pygame.Surface(Spec.DIM_BLOCK)
        surf.fill(color)
        surf.blit(img_engine, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(surface=surf)

class Shield(Block):

    name = 'Shield'

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        self.power_output = -Spec.POWER_CONS        

        # blit the shield image on the surface -> can resize the image
        self.get_surface('original').blit(img_shield, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(self.get_surface('original'))

    def set_color(self, color, update_original=False):
        '''
        Set the color of the block, set a call to update color 
        '''
        super().set_color(color, update_original=update_original)
        surf = pygame.Surface(Spec.DIM_BLOCK)
        surf.fill(color)
        surf.blit(img_shield, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(surface=surf)

class Turret(Block):

    name = 'Turret'

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        self.power_output = -Spec.POWER_CONS
        self.orien = 0 # deg
        self.fire_delay = 0 # timer
        
        # color that is displayed
        self.current_color = color

        # in deg -> makes calculations easier
        self.target_angle = 0 # deg
        self.circular_speed = 0 # deg
        self.is_rotating = False

        # blit the turret image on the surface -> can resize the image
        self.get_surface('original').blit(img_turret, (Spec.DIM_BLOCK-Spec.DIM_TURRET)//2)
        self.set_surface(self.get_surface('original'))
    
    def update_state(self):
        '''
        Update the turret's fire delay timer,  
        rotate the turret according to its circular speed.
        '''
        # update timer
        self.fire_delay += 1

        # update orientation
        if self.circular_speed != 0:
            self.orien += self.circular_speed

            if self.orien < 0:
                self.orien += 360
            elif self.orien > 360:
                self.orien -= 360

            # check if the orientation is near to the target_angle
            low = self.target_angle - Spec.TURRET_MAX_SPEED
            high = self.target_angle + Spec.TURRET_MAX_SPEED

            if low <= self.orien <= high: # orien in bounds
                self.is_rotating = False
                self.orien = self.target_angle
                self.circular_speed = 0

            self.rotate_surf(self.orien)

    def rotate_surf(self, angle: float):
        '''
        Rotate the turret surface of a given angle (deg)
        '''
        self.orien = angle

        # rotate the turret image, then blit on the surf
        img = pygame.transform.rotate(img_turret, angle)
        dim_img = np.array(img.get_size(), dtype='int32')
        pos = (Spec.DIM_BLOCK - dim_img) // 2

        # update surface - use a new one -> original already has an img blited on
        form = Form(Spec.DIM_BLOCK, (0,0), self.current_color)
        surface = form.get_surface('original')
        form.delete()

        surface.blit(img, pos)
        self.set_surface(surface)

        # update ship's surface
        self.ship.update_block(self)
        self.ship.update_signal(self)

    def rotate(self, angle: float):
        '''
        In game method.  
        Rotate the turret (at a certain speed) until reaching the target angle (deg).
        '''
        self.is_rotating = True
        self.target_angle = angle

        # select the smallest path to the angle
        path1 = (abs(self.orien - 360) + angle) % 360
        path2 = 360 - abs(self.orien - angle)

        if path1 <= path2:
            self.circular_speed = Spec.TURRET_MAX_SPEED
        else:
            self.circular_speed = -Spec.TURRET_MAX_SPEED

    def compute_bullet_pos(self):
        '''
        Compute the position where the bullet should appear on the screen
        '''
        len_center_turret = np.sqrt(2*(Spec.SIZE_BLOCK//2)**2)
        
        # compute turret center according to ship's orientation
        x = np.cos(self.ship.orien + np.pi/4) * len_center_turret
        y = np.sin(self.ship.orien + np.pi/4) * len_center_turret
        center_turret = np.array([x,y])

        # compute dif turret
        cannon_length = Spec.SIZE_TURRET//2
        angle = -get_rad(self.orien) + self.ship.orien

        x = np.cos(angle) * cannon_length
        y = np.sin(angle) * cannon_length
        dif_turret = center_turret + np.array([x,y])

        # compute pos on ship
        block_pos = self.coord * Spec.SIZE_BLOCK
        center_ship = np.array(self.ship.form.get_center()) - self.ship.pos
        
        block_dif = block_pos - center_ship
        length, angle = get_polar(block_dif) 
        angle += self.ship.orien
        pos_on_ship = center_ship + get_cartesian(length, angle)

        # add turret_dif
        pos_on_ship += dif_turret
        
        return self.ship.pos + pos_on_ship

    def create_bullet(self): 
        '''
        Return a Bullet object
        '''
        pos = self.compute_bullet_pos()
        
        # compute bullet orientation
        orien = -self.ship.orien + get_rad(self.orien)

        return Bullet(self.ship.team, pos, orien)

    def fire(self):
        '''
        If possible, fire a bullet -> add it in the bulletsystem.
        '''

        if not self.active:
            return
        
        if self.fire_delay >= Spec.TURRET_FIRE_DELAY:
            # reset timer
            self.fire_delay = 0

            BulletSystem.add_bullet(self.create_bullet())

    def set_color(self, color, update_original=False):
        '''
        Set the color of the block, set a call to update color 
        '''
        super().set_color(color, update_original=update_original)
        self.current_color = color

        # call rotate surf to change the color
        self.rotate_surf(self.orien)