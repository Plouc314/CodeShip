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
    def __init__(self, pos, dim, _type, coord=None, color=None):
        
        self.type = _type
        self.coord = coord

        if color == None:
            color = C.LIGHT_PURPLE
        
        if _type == 0:
            color = C.WHITE
        
        self.base_color = color

        surface = self._get_surf(_type, dim=dim)

        super().__init__(dim, pos, color=color, surface=surface, 
                    with_font=True)

    def reset_color(self):
        '''
        Set the base color as color
        '''
        self.set_color(self.base_color, marge=True)

    def set_surf_by_type(self, _type):
        '''
        Change the surface of the block and its type.
        '''
        self.type = _type

        if _type == 0:
            color = C.WHITE
        else:
            color = C.LIGHT_PURPLE
        
        self.base_color = color

        surface = self._get_surf(_type)

        self.set_color(color, marge=True)
        self.set_surface(surface, with_font=True)

    def _get_surf(self, _type, dim=None):
        '''
        Return the surface corresponding to one block type
        '''
        if dim is None:
            dim = self.get_dim()

        map_block = {0:None, 1:None, 2:img_generator, 3:img_shield, 4:img_turret, 5:img_engine}
        img = map_block[_type]

        if img == None:
            surface = None
        else:
            surface = pygame.Surface(dim, pygame.SRCALPHA)
            surface.blit(img, REL_POS_IMG)
        
        return surface

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
DIM_GR_TEXT = np.array([280, 60])

POS_GRID = np.array([800, 400])
POS_INFO = np.array([800, 1320])

### base ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Ship editor", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB), color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

button_edit = Button(DIM_GR_BUTT, (X_GR1, Y_GR), color=C.LIGHT_BLUE,
                text="Edit", font=Font.f(30))

button_save = Button(DIM_GR_BUTT, (X_GR1, Y_GR), color=C.LIGHT_BLUE,
                text="Save", font=Font.f(30))

text_info = TextBox(None, POS_INFO, color=C.DARK_GREEN,
                font=Font.f(25), text_color=C.WHITE, dynamic_dim=True)

text_credits = TextBox(DIM_GR_TEXT, (X_GR2, Y_GR),
                    text="", font=Font.f(30), marge=True)

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
    ('t info', text_info),
    ('t credits', text_credits),
    ('b block', button_block),
    ('b generator', button_generator),
    ('b engine', button_engine),
    ('b shield', button_shield),
    ('b turret', button_turret)
]

map_credits = {
    0:0,
    1:Spec.PRICE_BLOCK,
    2:Spec.PRICE_GENERATOR,
    3:Spec.PRICE_SHIELD,
    4:Spec.PRICE_TURRET,
    5:Spec.PRICE_ENGINE
}

class Ship(Page):
    
    def __init__(self, client):

        self.client = client
        self.blocks = None
        self.credits = 0

        self.active_block = None
        self.is_grab_active = False
        self.grab_block = Block((0,0), DIM_BLOCK, 0)

        super().__init__(states, components)
        
        self.set_states_components(None, ['title', 'b back'])
        self.set_states_components('base', 'b edit')
        self.set_states_components('edit',
            ['b save', 't credits', 
            'b block', 'b generator', 'b shield', 'b engine', 'b turret'])

        self.add_button_logic('b back', self.go_back)
        self.add_button_logic('b edit', self.b_edit)
        self.add_button_logic('b save', self.b_save)

        self._add_block_buttons_logic()

        self.set_in_state_func('base', self.in_base)
        self.set_in_state_func('edit', self.in_edit)
        self.set_out_state_func('edit', self.out_edit)

    def set_grid(self, grid):
        '''
        Set the grid of the ship (a np.ndarray)
        '''
        self.grid = grid
        self._create_blocks()
        self._set_credits()

    def b_edit(self):
        self.change_state('edit')

    def b_save(self):
        '''
        Send the current ship config to the server
        '''
        if self._check_ship_integrity():
            self.client.send_ship_config(self.grid)

            self.change_state('base')
            
            # set text info
            self.set_text('t info', "Ship saved succesfully.")
            self.set_color('t info', C.DARK_GREEN)
            self.change_display_state('t info', True)

        else:
            # set text info
            self.set_text('t info', "Ship must be made in one continuous form.")
            self.set_color('t info', C.DARK_RED)
            self.change_display_state('t info', True)

    def in_edit(self):
        '''set text credits'''
        self.set_text('t credits', f'Credits: {self.credits}')

    def out_edit(self):
        '''
        Reset the edit vars
        '''
        self.active_block = None
        self.is_grab_active = False

    def in_base(self):
        '''
        Check if the server sent a ship conf,
        if yes, set the ship conf
        '''
        self.change_display_state('t info', False)

        with self.client.get_data('sh') as ship_arr:

            if ship_arr is None:
                return
            
            self.set_grid(ship_arr)

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

                block = Block(pos, DIM_BLOCK, self.grid[x,y], coord=(x,y))

                # set keys of blocks to be their ids
                self.add_component(id(block), block)
                self.blocks.append(block)

    def _add_block_buttons_logic(self):
        '''Add logic to the grab buttons'''

        for name, _type in [('b block', 1),
                                  ('b generator', 2),
                                  ('b engine', 5),
                                  ('b shield', 3),
                                  ('b turret', 4)]:

            logic = self._get_button_logic(_type)

            self.add_button_logic(name, logic)

    def _get_button_logic(self, _type):
        '''
        Return the function that will be the logic of the button
        '''
        def logic():

            # reset potential active block
            self._change_active_block(None)

            # reset potential error msg
            self.change_display_state('t info', False)

            # check that can afford new block
            if self.credits >= map_credits[_type]:

                self.is_grab_active = True
                
                self.grab_block.set_surf_by_type(_type)

            else:
                # display an error msg
                self.set_text('t info', "No enough credits.")
                self.set_color('t info', C.DARK_RED, marge=True)
                self.change_display_state('t info', True)

        return logic

    def react_events(self, pressed, events):

        super().react_events(pressed, events)

        # must be in edit mode
        if self.get_state() != "edit":
            return

        for block in self.blocks:
            if block.pushed(events):
                
                if self.is_grab_active:
                    # set new block
                    self._change_grid_block(block)

                else:
                    # set active block
                    self._change_active_block(block)

        # set the position of the grab block
        if self.is_grab_active:
            self.grab_block.set_pos(pygame.mouse.get_pos(), center=True)

        if pressed[pygame.K_BACKSPACE]:
            self._remove_active_block()

    def display(self):

        super().display()

        if self.is_grab_active:
            self.grab_block.display()

    def _change_grid_block(self, block):
        '''
        Change the caracteristic of a block of the grid by the cara of the grap block
        '''
        self.credits += map_credits[block.type]

        block.set_surf_by_type(self.grab_block.type)
        self.is_grab_active = False

        # update grid
        self.grid[block.coord] = block.type

        # update credits
        self.credits -= map_credits[block.type]
        self.set_text('t credits', f'Credits: {self.credits}')

    def _remove_active_block(self):
        '''
        Remove the active block of the grid,  
        set it to be a "there-is-no-block-here" block (type 0)
        '''
        if self.active_block is None:
            return
        
        self.active_block.set_surface()
        self.active_block.set_color(C.WHITE, marge=True)

        # update grid
        self.grid[self.active_block.coord] = 0

        # update credits
        self.credits += map_credits[self.active_block.type]
        self.set_text('t credits', f'Credits: {self.credits}')

        self.active_block.type = 0
        self.active_block = None

    def _change_active_block(self, block):
        '''
        Change the active block, handeln the color changes.  
        If `block=None`, their won't be any active block (like a reset)
        '''
        if self.active_block != None:
            self.active_block.reset_color()
        
        if block != None:
            block.set_color(block.marge_color, marge=False)
        
        self.active_block = block
    
    def _set_credits(self):
        '''
        Set the number of credits left.
        '''
        self.credits = Spec.CREDITS_TOTAL

        for block in self.blocks:
            
            self.credits -= map_credits[block.type]
    
    def _check_ship_integrity(self):
        '''
        Check of the ship is made in one continuous form.
        '''
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[0]):
                
                if self.grid[x,y] > 0:
                    if not self._check_block_connected(x,y):
                        return False
        
        return True

    def _check_block_connected(self, x, y):
        '''
        Check that the block at the given coord is linked to at least one other block
        '''
        if x != 0:
            if self.grid[x - 1, y] > 0:
                return True
        
        if x != 7:
            if self.grid[x + 1, y] > 0:
                return True
        
        if y != 0:
            if self.grid[x, y - 1] > 0:
                return True
        
        if y != 7:
            if self.grid[x, y + 1] > 0:
                return True
        
        return False