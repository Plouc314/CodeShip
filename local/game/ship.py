import pygame
import numpy as np
import itertools
from game.block import Block, Generator, Shield, Turret, Engine
from lib.plougame import Interface, Form, Dimension, C
from game.geometry import get_deg, get_rad, get_polar, get_cartesian, get_length
from spec import Spec

# grid: 1=base, 2=generator, 3=shield, 4=turret
map_block = {1:Block, 2:Generator, 3:Shield, 4: Turret, 5: Engine}


class Ship:

    has_blocks = False
    color = C.BLUE

    blocks_priority = ['Generator', 'Engine', 'Shield', 'Turret', 'Block']

    def __init__(self, team, color=None):
        
        self.team = team

        # movement vectors
        self.speed = 0
        self.acc = 0
        self.orien = 0 # rad
        self.circular_speed = 0
        self.circular_acc = 0
        self.mass = 0
        self.pos = np.array([0,0], dtype='int32')

        # blocks
        self.typed_blocks = {'Block':[], 'Generator':[], 'Engine':[], 'Shield':[], 'Turret':[]}

        if color:
            self.color = color

    @classmethod
    def from_grid(cls, team, grid, color=None):
        '''
        Create a ship given a grid representing the ship (see block map).
        '''
        if color == None:
            color = cls.color
        
        ship = cls(team, color)
        ship.set_blocks(grid)

        return ship
    
    @classmethod
    def from_file(cls, team, filename, color=None):
        '''
        Create a ship given a .npy filename.
        '''
        grid = np.load(filename)

        return cls.from_grid(grid, team, color=color)

    def get_block_by_coord(self, coord):
        '''
        Return the block with the corresponding coord
        '''
        for block in self.blocks.values():
            if np.all(block.coord == coord):
                return block

    def get_pos(self, scaled=False):
        '''
        Return the position of the ship (ship's form).  
        If `scaled=True`, the position will be scaled to the current window's dimension.
        '''
        return np.array(self.form.get_pos(scaled=scaled))

    def get_mask(self):
        '''
        Return the pygame.mask.Mask object of the ship.
        '''
        return self.form.get_mask()

    def set_color(self):
        '''Set the color of the ship'''
        if self.has_blocks:
            self.color = color
            # change color of every block
            for block in self.blocks.values():
                block.set_color(self.color)
        else:
            self.color = color

    def set_pos(self, pos: (int, int)):
        '''Set the position of the ship'''
        self.pos[:] = pos

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

        self.create_blocks_lists()

    def create_blocks_lists(self):
        '''
        Create lists of each type of blocks.  
        Store them in .typed_blocks.
        '''
        for block in self.blocks.values():
            self.typed_blocks[block.name].append(block)

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
        self.form.set_surface(surface=self.form.get_surface('original'))

    def update_signal(self, block=None, index=None):
        '''
        Update one signal of the ship form surface,  
        given the block object or its index, blit its signal on the ship surface
        '''
        if index:
            block = self.blocks[index]

        pos = Spec.SIZE_BLOCK * block.coord + Spec.POS_SIGNAL
        signal = block.get_signal_form()
        
        # blit signal surf on form's surface
        signal.display(surface=self.form.get_surface('original'), pos=pos)

        self.form.set_surface(surface=self.form.get_surface('original'))

    def compile(self):
        '''
        Compile all the blocks of the ship into one surface.  
        Set all signals. 
        '''
        # create a surface that contains all the blocks
        dim_surf = Spec.DIM_BLOCK * Spec.SIZE_GRID_SHIP
        surface = pygame.Surface(dim_surf, pygame.SRCALPHA)

        for block in self.blocks.values():
            pos = block.coord * Spec.DIM_BLOCK

            # get image of block
            block_surf = block.compile()

            # add block to surface
            surface.blit(block_surf, pos)

        # create Form object with created surface
        self.form = Form(dim_surf, self.pos, surface=surface)

        self.set_signals()
    
    def set_signals(self):
        '''
        Set the signal of all the blocks of the ship.  
        Update the ship form surface.  
        '''
        for block in self.blocks.values():
            
            # don't display basic block signal -> it's useless
            if block.name == 'Block':
                continue
                
            self.update_signal(block)

    def rotate_surf(self, angle: float):
        '''
        Rotate the ship's surface of a given angle (rad).  
        '''
        # converts the angle into radian
        angle = -get_deg(angle)

        self.form.rotate(angle)

    def display(self):
        self.form.set_pos(self.pos, scale=True)
        self.form.display()
    
    def run(self):
        '''
        Execute all the ship's method that need to be executed during a frame.
        '''
        self.control_power_level()
        self.update_turrets()
        self.update_state()

    def update_turrets(self):
        '''
        Update all the turrets of the ships.
        '''
        for turret in self.typed_blocks['Turret']:
            turret.update_state()

    def update_state(self):
        '''
        Update the accelerations, speeds.  
        Update the position and orientation of the ship.  
        Rotate the ship to the current orientation.  
        '''
        self.compute_acc()
        self.compute_speed()
        self.compute_circular_speed()
        
        self.orien += self.circular_speed
        
        self.rotate_surf(self.orien)

        x = np.cos(self.orien) * self.speed + self.pos[0]
        y = np.sin(self.orien) * self.speed + self.pos[1]

        self.pos[:] = (x, y)

    def compute_speed(self):
        '''Update the speed of the ship'''
        self.speed += self.acc

    def compute_circular_speed(self):
        '''Update the circular speed of the ship'''
        self.circular_speed += self.circular_acc

        if abs(self.circular_speed) > Spec.MAX_CIRCULAR_SPEED:
            self.circular_speed = np.sign(self.circular_speed) * Spec.MAX_CIRCULAR_SPEED

    def set_circular_acc(self, value: int):
        '''
        Set the circular acceleration (deg) of the ship.  
        The acceleration depends of the mass of the ship.
        '''
        if value / self.mass > Spec.MAX_CIRCULAR_ACC:
            value = Spec.MAX_CIRCULAR_ACC
        
        self.circular_acc = value / self.mass

    def compute_acc(self):
        '''
        Compute the acceleration of the ship.
        '''
        # get total motor force
        total_force = 0
        for block in self.typed_blocks['Engine']:
            total_force += block.get_engine_power()
        
        # compute acceleration
        self.acc = (total_force - 2 * self.speed) / self.mass

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
                    block.is_active = False

                    if self.get_power_level() >= 0:
                        return
    
    def get_coord(self, pos):
        '''
        Given a position, return the coordinates of the corresponding block.
        '''
        # get distance to center of ship
        center = np.array(self.form.get_center(scale=True))
        dif_center, alpha = get_polar(pos - center)
        alpha -= self.orien

        # inv scale the dif center -> compare to none rotated/scaled dimensions
        dif_center = Dimension.inv_scale(dif_center)

        # get not scaled/rotated pos from center
        pos = get_cartesian(dif_center, alpha)

        # add center to position 
        relative_center = np.array([
            self.form.get_dim()[0]//2,
            self.form.get_dim()[1]//2,
        ])
        pos += relative_center

        # get coord from position
        coord = np.floor(pos / Spec.SIZE_BLOCK)

        # when coord is out of bounds -> replace to the limits
        coord = np.where(coord < 0, 0, coord)
        
        max_coord = Spec.SIZE_GRID_SHIP
        coord = np.where(coord >= max_coord, max_coord-1, coord)

        return coord

    def handeln_collision(self, bullet, intersect):
        '''
        Handeln collision with a bullet.
        '''
        # get coord of touched block
        coord = self.get_coord(intersect)

        block = self.get_block_by_coord(coord)

        if block:
            block.is_active = False
        