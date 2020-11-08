import pygame
from lib.plougame import Page, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from spec import Spec
import numpy as np

DIM_BLOCK = np.array([150,150])
DIM_IMG = np.array([110,110])
REL_POS_IMG = (DIM_BLOCK - DIM_IMG)//2

# load imgs
folder = "game/imgs/"

img_shield = pygame.image.load(folder + 'shield.png')
img_shield = pygame.transform.scale(img_shield, DIM_IMG)

img_generator = pygame.image.load(folder + 'generator.png')
img_generator = pygame.transform.scale(img_generator, DIM_IMG)

img_engine = pygame.image.load(folder + 'engine.png')
img_engine = pygame.transform.scale(img_engine, DIM_IMG)

img_turret = pygame.image.load(folder + 'turret.png')
img_turret = pygame.transform.rotate(img_turret, 270)
img_turret = pygame.transform.scale(img_turret, DIM_IMG)


class Block(Button):
    def __init__(self, pos, dim, block_type, color=None):
        
        self.block_type = block_type

        map_block = {0:None, 1:None, 2:img_generator, 3:img_shield, 4:img_turret, 5:img_engine}
        img = map_block[block_type]

        if color == None:
            color = C.LIGHT_PURPLE
        
        if block_type == 0:
            color = C.WHITE
        
        if img == None:
            surface = None
        else:
            surface = pygame.Surface(dim, pygame.SRCALPHA)
            surface.blit(img, REL_POS_IMG)

        super().__init__(dim, pos, color=color, surface=surface, 
                    with_font=True)

### Components ###

Y_TB = 100
X_TB1 = 100

Y_GR = 330
X_GR1 = 800
X_GR2 = 990

X_LB = 1720
Y_LB1 = 400
Y_LB2 = 570
Y_LB3 = 740
Y_LB4 = 910
Y_LB5 = 1080

DIM_GR_BUTT = np.array([180, 60])
POS_GRID = np.array([800, 400])

### base ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Ship editor", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB), color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

button_edit = Button(DIM_GR_BUTT, (X_GR2, Y_GR), color=C.LIGHT_BLUE,
                text="Edit", font=Font.f(30))

button_save = Button(DIM_GR_BUTT, (X_GR1, Y_GR), color=C.LIGHT_BLUE,
                text="Save", font=Font.f(30))

button_block = Block((X_LB, Y_LB1), DIM_BLOCK, 1, color=C.LIGHT_GREEN)
button_generator = Block((X_LB, Y_LB2), DIM_BLOCK, 2, color=C.LIGHT_GREEN)
button_shield = Block((X_LB, Y_LB3), DIM_BLOCK, 3, color=C.LIGHT_GREEN)
button_turret = Block((X_LB, Y_LB4), DIM_BLOCK, 4, color=C.LIGHT_GREEN)
button_engine = Block((X_LB, Y_LB5), DIM_BLOCK, 5, color=C.LIGHT_GREEN)

states = ['base', 'edit']

components = [
    ('title', title),
    ('b back', button_back),
    ('b edit', button_edit),
    ('b save', button_save),
    ('b block', button_block),
    ('b generator', button_generator),
    ('b engine', button_engine),
    ('b shield', button_shield),
    ('b turret', button_turret),
]

class Ship(Page):
    
    def __init__(self, client):

        self.client = client
        self.blocks = None
        self.active_block = None

        super().__init__(states, components)
        
        self.set_states_components(None, ['title', 'b back', 'b save'])
        self.set_states_components('base', 'b edit')
        self.set_states_components('edit',
            ['b block', 'b generator', 'b shield', 'b engine', 'b turret'])

        self.add_button_logic('b back', self.go_back)
        self.add_button_logic('b edit', self.edit)
    
        self.set_grid(np.array([
            [0,0,0,0,0,0],
            [0,2,2,0,0,0],
            [4,3,3,4,0,1],
            [1,5,5,1,2,1],
            [4,3,3,4,3,1],
            [4,3,3,4,5,1]
        ])[::-1])

    def set_grid(self, grid):
        '''
        Set the grid of the ship (a np.ndarray)
        '''
        self.grid = grid
        self._create_blocks()
    
    def edit(self):
        self.change_state('edit')

    def _create_blocks(self):
        '''
        Create the blocks that represent the ship.
        '''
        self.blocks = []
        
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                
                pos = [
                    POS_GRID[0] + DIM_BLOCK[0] * x,
                    POS_GRID[1] + DIM_BLOCK[1] * y,
                ]

                block = Block(pos, DIM_BLOCK, self.grid[x,y])

                self.add_component(f'block{x}{y}', block)
                self.blocks.append(block)
        
    def react_events(self, pressed, events):

        super().react_events(pressed, events)

        if self.get_state() == "edit":
            for block in self.blocks:
                if block.pushed(events):
                    # set active block
                    self._change_active_block(block)
                
                
    def _change_active_block(self, block):
        '''
        Change the active block, handeln the color changes
        '''
        if self.active_block != None:
            self.active_block.set_color(C.LIGHT_PURPLE)
        
        block.set_color(block.marge_color, marge=False)
        self.active_block = block