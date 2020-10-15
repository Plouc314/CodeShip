import pygame
import numpy as np
import itertools
from block import Block, Energie, Shield, Turret, Engine
from lib.interface import Interface, Form, C
from spec import Spec

# grid: 1=base, 2=energie, 3=shield, 4=turret
map_block = {1:Block, 2:Energie, 3:Shield, 4: Turret, 5: Engine}


class Ship:

    has_blocks = False
    color = C.BLUE

    blocks_priority = ['Energie', 'Engine', 'Shield', 'Turret', 'Block']

    def __init__(self, color=None):
        
        # movement vectors
        self.speed = 0
        self.acc = 0
        self.orien = 0
        self.circular_speed = 0
        self.circular_acc = 0
        self.mass = 0
        self.pos = np.array([0,0], dtype='int32')

        # blocks
        self.typed_blocks = {'Block':[], 'Energie':[], 'Engine':[], 'Shield':[], 'Turret':[]}

        if color:
            self.color = color

    @classmethod
    def from_grid(cls, grid, color=None):
        '''
        Create a ship given a grid representing the ship (see block map).
        '''
        if color == None:
            color = cls.color
        
        ship = cls(color)
        ship.set_blocks(grid)

        return ship
    
    @classmethod
    def from_file(cls, filename, color=None):
        '''
        Create a ship given a .npy filename.
        '''
        grid = np.load(filename)

        return cls.from_grid(grid)

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

    def del_block(self, index):
        
        # remove block from dict
        self.blocks.pop(index, None)

        # remove block index on grid
        self.blocks_grid = np.where(self.blocks_grid == index, 0, self.blocks_grid)

    def compile(self, angle:int = None):
        '''
        Compile all the blocks of the ship into one surface.  
        Can rotate the surface before compile it.  
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
        
        if angle:
            surface = pygame.transform.rotate(surface, angle)

        # create Form object with created surface
        self.form = Form(dim_surf, self.pos, surface=surface)
    
    def rotate(self, angle: float):
        '''
        Rotate the ship of a given angle (rad).  
        '''
        # converts the angle into radian
        angle = round(-angle * 180 / np.pi)

        self.form.rotate(angle)

    def display(self):
        self.form.set_pos(self.pos, scale=True)
        self.form.display()
    
    def run(self):
        pass

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
        self.rotate(self.orien)

        x = np.cos(self.orien) * self.speed + self.pos[0]
        y = np.sin(self.orien) * self.speed + self.pos[1]

        self.pos[:] = (x, y)

    def compute_speed(self):
        '''Update the speed of the ship'''
        self.speed += self.acc

    def compute_circular_speed(self):
        '''Update the circular speed of the ship'''
        self.circular_speed += self.circular_acc

        if self.circular_speed > Spec.MAX_CIRCULAR_SPEED:
            self.circular_speed = Spec.MAX_CIRCULAR_SPEED

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


    def control_power_level(self):
        '''
        Check that there is enough power to feed all the blocks.  
        If not, deactivate blocks randomly (according to the blocks priority) until there is enough power.
        '''
        power_level = 0

        for block in self.blocks.values():
            power_level += block.get_power_output()
        
        if power_level >= 0:
            return
        
        else:
            # disable blocks until the power level is positive
            # goes trough every type except the Energie blocks
            for block_type in self.blocks_priority[:0:-1]:
                # shuffle the blocks
                blocks = np.random.shuffle(self.typed_blocks[block_type])
                
                for block in blocks:
                    block.is_active = False

                    if power_level >= 0:
                        return
    