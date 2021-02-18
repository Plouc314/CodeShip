import pygame
import numpy as np
import itertools
from game.block import Block, Generator, Shield, Turret, Engine
from lib.plougame import Interface, Form, Dimension, C
from lib.perfeval import Counter
from game.geometry import get_deg, get_rad, get_polar, get_cartesian, get_norm, to_vect
from data.spec import Spec

map_block = {1:Block, 2:Generator, 3:Shield, 4: Turret, 5: Engine}

indicator = Form((50,50), (3100, 1700), color=C.YELLOW)
indicator2 = Form((10, 10), (0,0), color=C.YELLOW)

class Ship:

    has_blocks = False
    color = C.BLUE

    blocks_priority = ['Generator', 'Engine', 'Shield', 'Turret', 'Block']

    def __init__(self, team, color=None):
        
        self.team = team

        # auxiliar acceleration
        self.is_aux_acc = False
        self.aux_acc = 0
        self.aux_timer = 0

        # movement vectors
        self.speed = np.array([0,0], dtype=float)
        self.acc = np.array([0,0], dtype=float)
        self.orien = 0 # rad
        self.circular_speed = 0
        self.circular_acc = 0
        self.mass = 0
        self.pos = np.array([0,0], dtype='int32')

        # blocks
        self.typed_blocks = {'Block':[], 'Generator':[], 'Engine':[], 'Shield':[], 'Turret':[]}
        self.abs_centers = {}
        self._mask = None

        if color:
            self.color = color

    @classmethod
    def from_grid(cls, grid, team, color=None):
        '''
        Create a ship given a grid representing the ship (see block map).
        '''
        if color == None:
            color = cls.color
        
        ship = cls(team, color)
        ship.set_blocks(grid)

        return ship

    def get_block_by_coord(self, coord, blocks=None):
        '''
        Return the block with the corresponding coord.  
        If `blocks` is specified, loop through the specified blocks.
        '''
        if blocks == None:
            blocks = self.blocks.values()

        for block in blocks:
            if np.all(block.coord == coord):
                return block

    def set_pos(self, pos, scaled=False):
        '''
        Set the position of the ship (ship's form).  
        `scaled` parameter specify if the given position is scaled to the current window's dimension.
        '''
        if scaled:
            pos = Dimension.inv_scale(pos)
        
        self.pos[:] = pos
        self.form.set_pos(self.pos, scale=(not scaled))

    def get_pos(self, scaled=False, center=False):
        '''
        Return the position of the ship (ship's form).  
        If `scaled=True`, the position will be scaled to the current window's dimension.  
        If `center=True`, return the center of the ship.
        '''
        if center:
            return np.array(self.form.get_center(scale=scaled))
        else:
            return np.array(self.form.get_pos(scaled=scaled))

    def get_surface(self, surf_type):
        '''
        Return the specified surface,
        can be:

        - original: the unscaled & unrotated surface  
        - main: the scaled & rotated main displayed surface  
        - font: if set, the font surface  
        '''
        return self.form.get_surface(surf_type=surf_type)

    def get_mask(self) -> pygame.mask.Mask:
        '''
        Return the pygame.mask.Mask object of the ship.
        '''
        if self._mask is None:
            self._process_mask()
            indicator.display()

        return self._mask

    def get_speed(self, scalar=False):
        '''
        Return the speed of the ship,  
        if `scalar=False`: return the vector speed,
        else return the norm of the vector.
        '''
        if scalar:
            return get_norm(self.speed)
        else:
            return self.speed

    def get_acc(self, scalar=False):
        '''
        Return the acceleration of the ship,  
        if `scalar=False`: return the vector acceleration,
        else return the norm of the vector.
        '''
        if scalar:
            return get_norm(self.acc)
        else:
            return self.acc

    def set_color(self, color):
        '''Set the color of the ship'''
        if self.has_blocks:
            self.color = color
            # change color of every block
            for block in self.blocks.values():
                block.set_color(self.color, update_original=True)
        else:
            self.color = color

    def set_auxiliary_acc(self, acc):
        '''
        Set an auxiliary source of acceleration,  
        `acc` is a vector (`np.dnarray`).  
        It will last for `Spec.AUX_TIMER` frames.
        '''
        self.is_aux_acc = True
        self.aux_acc = acc
        self.aux_timer = 0

    def get_auxiliary_acc(self):
        '''
        If a auxiliary force of acceleration is set, 
        will return it and update the timer.
        '''
        if not self.is_aux_acc:
            return np.zeros(2)
        
        if self.aux_timer == Spec.AUX_TIMER:
            self.is_aux_acc = False
            self.aux_timer = 0
            self.aux_acc = 0
        
        self.aux_timer += 1

        return self.aux_acc

    def set_blocks(self, grid):
        '''
        Create the blocks, set up the blocks' grid.

        Args:
            - grid: an array representing the ship with value of block map
        '''
        self.has_blocks = True

        self.blocks = {}
        # contains the blocks indexs on corresponding the cases
        self.blocks_grid = np.zeros(Spec.DIM_SHIP, dtype='int16')
        # correspond to the self.blocks indexs -> start at 1
        n_block = 0 
        
        # iterate over every case
        for x,y in itertools.product(range(grid.shape[0]), repeat=2):

            # create block corresponding to grid case value
            if grid[x,y] > 0:
                
                n_block += 1
                self.blocks_grid[x,y] = n_block

                # create the blocks
                block = map_block [ grid[x,y] ] ((x,y), color=self.color)
                block.ship = self

                self.blocks[n_block] = block
        
        # set the mass of the ship
        self.mass = 4 * n_block
        self.initial_n_block = n_block

        self.create_blocks_lists()

    def create_blocks_lists(self):
        '''
        Create lists of each type of blocks.  
        Store them in `.typed_blocks`.
        '''
        for block in self.blocks.values():
            self.typed_blocks[block.name].append(block)

    def remove_block(self, key):
        '''
        Remove one of the blocks of the ship,  
        given the the key of the block,  
        compile the entire ship.
        '''
        block = self.blocks.pop(key)

        block.on_death()

        # update mass of ship
        self.mass -= 4

        self.typed_blocks[block.name].remove(block)    
        self.abs_centers.pop(key)

        self.compile()

    def update_block(self, block=None, index=None):
        '''
        Update one block of the ship form surface,  
        given the block object or its index, compile it and blit it on the ship surface
        '''
        if index:
            block = self.blocks[index]

        pos = block.coord * Spec.SIZE_BLOCK
        surf = block.compile()

        self.form.get_surface('original').blit(surf, pos)

    def update_signal(self, block=None, shield=False, index=None):
        '''
        Update one signal of the ship form surface,  
        given the block object or its index, blit its signal on the ship surface.  
        If shield is True, update the shield signal
        '''
        if index:
            block = self.blocks[index]

        if shield:
            pos = Spec.SIZE_BLOCK * block.coord + Spec.POS_SIGNAL_SHIELD
            signal = block.get_signal_shield()
            if signal is None:
                return
        
        else:
            pos = Spec.SIZE_BLOCK * block.coord + Spec.POS_SIGNAL
            signal = block.get_signal_form()
        
        # blit signal surf on form's surface
        signal.display(surface=self.form.get_surface('original'), pos=pos)

    def compile(self):
        '''
        Compile all the blocks of the ship into one surface.  
        Set all signals. 
        '''
        # create a surface that contains all the blocks
        dim_surf = Spec.DIM_BLOCK * Spec.SIZE_GRID_SHIP
        surface = pygame.Surface(dim_surf)
        surface.set_colorkey(C.WHITE)
        surface.fill(C.WHITE)

        for block in self.blocks.values():
            pos = block.coord * Spec.DIM_BLOCK

            # get image of block
            block_surf = block.compile()

            # add block to surface
            surface.blit(block_surf, pos)

        surface = surface.convert()

        # create Form object with created surface
        self.form = Form(dim_surf, self.pos, surface=surface)

        self.set_signals()

        # create first mask
        self._mask = pygame.mask.from_surface(self.form.get_surface('main'))

    def set_signals(self):
        '''
        Set the signal of all the blocks of the ship.  
        Update the ship form surface.  
        '''
        for block in self.blocks.values():

            # don't display basic block signal -> it's useless
            if block.name != 'Block':
                self.update_signal(block)

            self.update_signal(block, shield=True)

    def rotate_surf(self, angle: float):
        '''
        Rotate the ship's surface to a given angle (rad).  
        '''
        # converts the angle into deg
        angle = -get_deg(angle)

        self.form.rotate(angle)

    @Counter.add_func
    def display(self):
        '''
        Display the ship  
        '''
        self.form.display()

    @Counter.add_func
    def run(self, remote_control=False):
        '''
        Execute all the ship's method that need to be executed during a frame.
        '''
        self.run_blocks()

        if not remote_control:
            self._update_local()    
        
        self.form.set_pos(self.pos, scale=True)

        self._compute_blocks_abs_centers()

        # update main surface
        self._update_surf()
        
        # udapte mask
        self._mask = None

    @Counter.add_func
    def _update_local(self):
        self.control_power_level()
        self.update_turrets()
        self.update_shields()
        self.update_state()

    @Counter.add_func
    def _update_surf(self):
        self.form.set_surface(surface=self.form.get_surface('original'))
        self.rotate_surf(self.orien)

    @Counter.add_func
    def _process_mask(self):
        # get white pixels
        self._mask = pygame.mask.from_threshold(self.form.get_surface('main'), C.WHITE, (1,1,1))
        # set mask to other pixels
        self._mask.invert()

    @Counter.add_func
    def update_turrets(self):
        '''
        Update all the turrets of the ships.
        '''
        for turret in self.typed_blocks['Turret']:
            turret.update_state()

    def update_shields(self):
        '''
        Update all the shields of the ships.
        '''
        for shield in self.typed_blocks['Shield']:
            shield.update_state()

    def update_state(self):
        '''
        Update the accelerations, speeds.  
        Update the position and orientation of the ship.  
        '''
        self.compute_acc()
        self.compute_speed()
        self.compute_circular_speed()
        
        self.orien += self.circular_speed
        #self.orien %= 2 * np.pi
        self.pos += self.speed.astype(int)

    @Counter.add_func
    def run_blocks(self):
        '''
        Call the run method of each block,  
        check if the color of the block has changed
        '''
        for block in self.blocks.values():
            block.run()
            
            if block.has_color_changed:
                block.has_color_changed = False
                self.update_block(block=block)
                
                if block.name != 'Block':
                    self.update_signal(block=block)
                    self.update_signal(block=block, shield=True)

    def compute_speed(self):
        '''Update the speed of the ship'''
        self.speed += self.acc

        norm_speed = get_norm(self.speed)

        if norm_speed == 0:
            return

        self.speed *= Spec.AIR_RESISTANCE ** max(1, np.log10(norm_speed))

    def compute_circular_speed(self):
        '''Update the circular speed of the ship'''
        self.circular_speed *= Spec.AIR_RESISTANCE
        self.circular_speed += self.circular_acc

        if abs(self.circular_speed) > Spec.MAX_CIRCULAR_SPEED:
            self.circular_speed = np.sign(self.circular_speed) * Spec.MAX_CIRCULAR_SPEED

    def compute_acc(self):
        '''
        Compute the acceleration of the ship.
        '''
        # get total motor force
        total_force = self.get_engines_power()
        total_force = to_vect(total_force, self.orien)

        # compute acceleration
        self.acc = total_force / self.mass
        self.acc += self.get_auxiliary_acc()

    def get_engines_power(self):
        '''
        Return the sum of the power of all the engines.
        '''
        force = 0
        for block in self.typed_blocks['Engine']:
            force += block.get_engine_force()
        return force 

    def get_power_level(self):
        '''
        Return the power level of the ship.  
        The power level is the sum of all the power outputs.
        '''
        power_level = 0

        for block in self.blocks.values():
            power_level += block.get_power_output()
        
        return power_level

    def control_power_level(self):
        '''
        Check that there is enough power to feed all the blocks.  
        If not, deactivate blocks randomly (according to the blocks priority)
        until there is enough power.
        '''
        power_level = self.get_power_level()
        
        if power_level >= 0:
            return
        
        else:
            # disable blocks until the power level is positive
            # goes trough every type except the Generator blocks
            for block_type in self.blocks_priority[:0:-1]:
                # shuffle the blocks
                blocks = self.typed_blocks[block_type].copy()
                np.random.shuffle(blocks)

                for block in blocks:
                    block.set_activate(False)

                    if self.get_power_level() >= 0:
                        return
    
    @Counter.add_func
    def _compute_blocks_abs_centers(self):
        '''
        Compute the absolute (scaled) center of all the blocks
        '''
        abs_center = np.array(self.form.get_center(scale=False), dtype=float)
        rel_center = abs_center - self.pos

        for key, block in self.blocks.items():
            
            coord = np.array(block.coord, dtype=float)
            coord *= Spec.SIZE_BLOCK
            coord += Spec.SIZE_BLOCK // 2
            coord -= rel_center

            length, alpha = get_polar(coord)
            
            alpha += self.orien

            coord = get_cartesian(length, alpha)

            coord += rel_center + self.pos

            self.abs_centers[key] = coord.astype(int)

    def get_key_by_pos(self, pos):
        '''
        Given a (unscaled) position,
        return the key of the nearest block.
        '''
        distances = {}
        pos = np.array(pos)

        # compute every distances
        for key, center in self.abs_centers.items():
            distances[key] = get_norm(center - pos)

        # get key of min distance
        key = min(distances.keys(), key=distances.get)

        return key

    def handeln_collision(self, bullet, intersect):
        '''
        Handeln collision with a bullet.
        '''
        # get coord of touched block
        key = self.get_key_by_pos(Dimension.inv_scale(intersect))

        self.blocks[key].hit(bullet.damage)
        
        if self.blocks[key].hp <= 0:
            self.remove_block(key)
                

