import pygame
import numpy as np
from lib.plougame import Form, C
from lib.plougame.helper import Delayer
from game.bulletsystem import Bullet, BulletSystem
from game.geometry import get_deg, get_rad, get_polar, get_cartesian, get_norm
from data.spec import Spec


# load imgs
folder = "game/imgs/"

img_shield = pygame.image.load(folder + 'shield.png').convert_alpha()
img_shield = pygame.transform.scale(img_shield, Spec.DIM_ITEM)

img_generator = pygame.image.load(folder + 'generator.png').convert_alpha()
img_generator = pygame.transform.scale(img_generator, Spec.DIM_ITEM)

img_engine = pygame.image.load(folder + 'engine.png').convert_alpha()
img_engine = pygame.transform.scale(img_engine, Spec.DIM_ITEM)

img_turret = pygame.image.load(folder + 'turret.png').convert_alpha()
img_turret = pygame.transform.rotate(img_turret, 270)
img_turret = pygame.transform.scale(img_turret, Spec.DIM_TURRET)

class Block(Form):

    name = 'Block'
    ship = None

    # activate/deactivate signal
    signal_red = Form(Spec.DIM_SIGNAL, (0,0), color=C.LIGHT_RED)
    
    signal_green = Form(Spec.DIM_SIGNAL, (0,0), color=C.LIGHT_GREEN)
    
    signal_shield = Form(Spec.DIM_SIGNAL, (0,0), color=Spec.COLOR_SIGNAL_SHIELD)

    def __init__(self, coord, color=None, image=None, hp=None):

        if hp == None:
            self.hp = Spec.HP_BLOCK
        else:
            self.hp = hp
        
        self.active = True
        self.power_output = 0
        
        # shield
        self.hp_shield = 0
        self.has_shield = False
        self.has_signal_shield = False
        
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
        # start by hiting the shield
        self.hp_shield -= damage
        
        if self.hp_shield <= 0:
            # if shield got over hit, report damage on hp
            self.hp -= -round(self.hp_shield)
            self.hp_shield = 0

            self.set_color(C.RED)

        else:
            self.set_color(C.NEO_BLUE)
        
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

    def set_signal_shield(self):
        '''
        Update the shield signal
        '''
        self.ship.update_signal(self, shield=True)

    def run(self):
        '''
        '''
        self.run_hit_effect()

        # check shield signal
        if not self.has_signal_shield and self.hp_shield > 0:
            self.has_signal_shield = True
            self.set_signal_shield()
        
        elif self.has_signal_shield and self.hp_shield == 0:
            self.has_signal_shield = False
            self.set_signal_shield()

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

        if self.active:
            return self.power_output
        else:
            return 0

    def get_activate(self):
        '''
        Return if the block is activate.
        '''
        return self.active
    
    def set_activate(self, value: bool):
        '''
        Set if the block is activate.
        '''
        # don't update signal if new value is equal to old one
        if self.active == value:
            return

        self.active = value
        # update the signal on the ship
        if self.name != 'Block':
            self.ship.update_signal(self)

    def get_signal_form(self):
        '''
        Return the signal Form object with the correct color.  
        '''
        if self.active:
            return self.signal_green
        else:
            return self.signal_red

    def get_signal_shield(self):
        '''
        Return the signal Form object, if doesn't have an active shield
        return a see-through surface.
        '''
        if self.hp_shield > 0:
            return self.signal_shield
        else:
            return None

    def on_death(self):
        '''
        Function executed when the block is removed at runtime,  
        handeln the effect of the removal of the block
        (by ex: for Shield block remove shield hps)
        '''
        pass

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

    def set_activate(self, value: bool):
        '''
        Set if the block is activate.
        '''
        if value == False:
            self.activation_per = 0
            self.active = False
        else:
            # by default: activate the engine on full power
            self.activation_per = 1
            self.active = True

        super().set_activate(value)

    def get_power_output(self):
        return self.power_output * self.activation_per

    def get_engine_force(self):
        '''Return the force generated by the engine.'''
        return Spec.MOTOR_FORCE * self.activation_per

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

        self.n_prtc_block = 0
        self.blocks = []
        self.intensity = None

        # blit the shield image on the surface -> can resize the image
        self.get_surface('original').blit(img_shield, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surface(self.get_surface('original'))

    def is_block(self, block) -> bool:
        '''
        Return if the given block is protected by the shield.
        '''
        for info in self.blocks:
            if info['block'] is block:
                return True
            
        return False

    def update_state(self):
        '''
        Regenerate shield of protected blocks.
        '''
        n_damaged = 0

        for info in self.blocks:
            if info['block'].hp_shield < info['max hp']:
                n_damaged += 1
        
        if n_damaged == 0:
            return

        regen_hp = Spec.SHIELD_REGEN_RATE / n_damaged

        for info in self.blocks:
            info['block'].hp_shield += regen_hp
            if info['block'].hp_shield > info['max hp']:
               info['block'].hp_shield = info['max hp']

    def balance(self, hp_shield_bonus=0):
        '''
        Balance the shield distribution amongs the protected blocks.  
        if hp_shield_bonus is set, it will be added in addition to the current hps.
        '''
        current_shield = hp_shield_bonus
        for info in self.blocks:
            current_shield += info['block'].hp_shield
        
        # can happen when decreasing intensity
        if current_shield < 0:
            current_shield = 0

        balanced_shield = current_shield / self.n_prtc_block
        balanced_max_shield = Spec.SHIELD_HP * self.intensity / self.n_prtc_block

        for info in self.blocks:
            info['block'].hp_shield = balanced_shield
            info['max hp'] = balanced_max_shield
            info['frozen hp'] = balanced_shield

    def set_intensity(self, value: int, at_runtime=False):
        '''
        Set the intensity of the shield,
        which defines the power consumption
        and amound of shield hp available.  
        If at_runtime is True, will update the shields hp of every blocks
        to balance the distributed hps.
        '''
        value = round(value)
        if value > Spec.SHIELD_MAX_INTENSITY:
            value = Spec.SHIELD_MAX_INTENSITY
        
        old_value = self.intensity
        self.intensity = value

        if at_runtime:
            self.balance(Spec.SHIELD_HP * (self.intensity - old_value))

    def setup(self):
        '''
        Dispatch shield hp to all added blocks.
        '''
        if self.n_prtc_block == 0:
            return

        if self.intensity == None:
            # by default the intensity is the same as the number of protected blocks.
            self.intensity = self.n_prtc_block

        # set number of shield hp per block
        hp = Spec.SHIELD_HP * self.intensity / self.n_prtc_block

        for i in range(len(self.blocks)):
            
            # set shield hp on block
            self.blocks[i].hp_shield = hp

            self.blocks[i] = {
                'block': self.blocks[i],
                'max hp': hp,
                'frozen hp': hp, # hp stored when shield goes inactivate
            }

    def add_prtc_block(self, block: Block, at_runtime=False):
        '''
        In setup stage.  
        Add a block to be protected by the shield  
        If at_runtime is True, will update the shields hp of every blocks
        to balance the distributed hps.
        '''
        if self.n_prtc_block >= Spec.SHIELD_MAX_PRTC:
            return
        
        if block in self.blocks:
            return

        # can only have one shield by block
        if block.has_shield:
            return

        block.has_shield = True
        self.n_prtc_block += 1
        
        if at_runtime:
            self.blocks.append({
                'block': block,
                'max hp': 0,
                'frozen hp': 0,
            })
            self.balance()
        else:
            self.blocks.append(block)

        # inform that the block was added
        return True

    def remove_prtc_block(self, block: Block, at_runtime=False):
        '''
        In setup stage.  
        Remove one of the protected block.  
        If at_runtime is True, will update the shields hp of every blocks
        to balance the distributed hps.
        '''
        if not block in self.blocks:
            return
        
        block.has_shield = False
        self.n_prtc_block -= 1
        
        if at_runtime:
            idx = None
            
            for i, info in enumerate(self.blocks):
                if info['block'] is block:
                    idx = i

            if idx == None:
                raise IndexError(f"Given block is not protected: {block}")

            self.blocks.pop(i)
            self.balance()
        else:
            self.blocks.remove(block)            

    def get_power_output(self):
        if self.active:
            return self.intensity * self.power_output
        else:
            return 0
    
    def set_activate(self, value):
        '''
        Set if the block is activate.
        '''
        if self.active == value:
            return

        if value == False:
            for info in self.blocks:
                info['frozen hp'] = info['block'].hp_shield
                info['block'].hp_shield = 0
            
        else:
            for info in self.blocks:
                info['block'].hp_shield = info['frozen hp']

        super().set_activate(value)

    def on_death(self):
        '''
        Remove shield from protected blocks
        '''
        for info in self.blocks:
            info['block'].hp_shield = 0

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
        if not self.active:
            return

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
            low = self.target_angle - 2*Spec.TURRET_MAX_SPEED
            high = self.target_angle + 2*Spec.TURRET_MAX_SPEED

            if low <= self.orien <= high: # orien in bounds
                self.is_rotating = False
                self.orien = self.target_angle
                self.circular_speed = 0

            self.rotate_surf(self.orien)

        # if active -> fire
        if self.active:
            self.fire()

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
        surface = pygame.Surface(Spec.DIM_BLOCK)
        surface.fill(self.current_color)

        surface.blit(img, pos)
        self.set_surface(surface)

        # update ship's surface
        self.ship.update_block(self)
        self.ship.update_signal(self)
        self.ship.update_signal(self, shield=True)

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