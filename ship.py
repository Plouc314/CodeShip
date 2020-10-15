import pygame
import numpy as np
import itertools
from block import Block, Energie, Shield, Turret
from lib.interface import Interface, Form
from spec import Spec

# grid: 1=base, 2=energie, 3=shield, 4=turret
map_block = {1:Block, 2:Energie, 3:Shield, 4: Turret}


class Ship:
    def __init__(self, pos, color):
        
        self.pos = pos
        self.color = color

    def set_blocks(self, grid):
        '''
        Create the blocks, set up the blocks' grid.

        Args:
            - grid: an array representing the ship with value of block map
        '''
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

    def compile(self):
        '''
        Compile all the blocks of the ship into one surface.
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
    
    def display(self):
        self.form.display()