import pygame
from lib.plougame import SubPage, TextBox, Button, Font, C
from data.spec import Spec
import numpy as np

DIM_BLOCK = np.array([150,150])
DIM_IMG = np.array([110,110])
REL_POS_IMG = (DIM_BLOCK - DIM_IMG)//2

# load imgs
folder = "game/imgs/"

img_shield = pygame.image.load(folder + 'shield.png').convert_alpha()
img_shield = pygame.transform.scale(img_shield, DIM_IMG)

img_generator = pygame.image.load(folder + 'generator.png').convert_alpha()
img_generator = pygame.transform.scale(img_generator, DIM_IMG)

img_engine = pygame.image.load(folder + 'engine.png').convert_alpha()
img_engine = pygame.transform.scale(img_engine, DIM_IMG)

img_turret = pygame.image.load(folder + 'turret.png').convert_alpha()
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

desc_block = f'''
Block
No utility except to add hps.
Price: {Spec.PRICE_BLOCK}   HP: {Spec.HP_BLOCK}
Power consumption: 0
'''
desc_generator = f'''
Generator
Powers up the other blocks.
Price: {Spec.PRICE_GENERATOR}   HP: {Spec.HP_BLOCK}
Power output: {Spec.POWER_ENERGIE}
'''
desc_shield = f'''
Shield
Provide hp to other blocks.
Price: {Spec.PRICE_SHIELD}   HP: {Spec.HP_BLOCK}
Power consumption: {Spec.POWER_CONS} - {Spec.POWER_CONS*Spec.SHIELD_MAX_INTENSITY}
'''
desc_turret = f'''
Turret
Can rotate, shoots bullets.
Price: {Spec.PRICE_TURRET}   HP: {Spec.HP_BLOCK}
Power consumption: {Spec.POWER_CONS}
'''
desc_engine = f'''
Engine
Drives the ship forward.
Price: {Spec.PRICE_ENGINE}   HP: {Spec.HP_BLOCK}
Power consumption: {Spec.POWER_CONS_MOTOR}
'''

map_blocks = {
    'b block': desc_block.strip(),
    'b generator': desc_generator.strip(),
    'b engine': desc_engine.strip(),
    'b shield': desc_shield.strip(),
    'b turret': desc_turret.strip()
}

map_credits = {
    0:0,
    1:Spec.PRICE_BLOCK,
    2:Spec.PRICE_GENERATOR,
    3:Spec.PRICE_SHIELD,
    4:Spec.PRICE_TURRET,
    5:Spec.PRICE_ENGINE
}

class ShipEditor(SubPage):
    
    def __init__(self, pos, offline=False):

        self.offline = offline
        self.client = None

        self.blocks = None
        self.credits = 0

        self.active_block = None
        self.is_grab_active = False
        self.grab_block = Block((0,0), DIM_BLOCK, 0)

        states = ['base', 'edit']

        components = Spec.formatter.get_components('ui/data/ship_editor.json')

        super().__init__(states, components, pos)

        self.set_states_components('base', 'b edit')
        self.set_states_components('edit',
            ['b save', 't credits', 
            'b block', 'b generator', 'b shield', 'b engine', 'b turret'])

        self.add_button_logic('b edit', self.b_edit)
        self.add_button_logic('b save', self.b_save)

        self._add_block_buttons_logic()

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
            
            # store/save grid
            if self.offline:
                Spec.update_local_profil(self.client.username,
                        'ship', self.grid.tolist())
                Spec.update_local_profil(self.client.username,
                        'ship status', True)
            else:
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
        To be executed when entering in base state.  
        Check if the server sent a ship conf,
        if yes, set the ship conf
        '''
        self.change_display_state('t info', False)

        # set grid ship
        ship_arr = self.client.in_data['sh']

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
                    DIM_BLOCK[0] * x,
                    DIM_BLOCK[1] * y,
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

        self.manage_text_block()

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

    def display(self, **kwargs):

        super().display(**kwargs)

        if self.is_grab_active:
            self.grab_block.display()

    def manage_text_block(self):
        '''
        Manage the text block, 
        if it's displayed,
        what text does it display
        '''
        # reset text block
        self.change_display_state('t block', False)

        for name, text in map_blocks.items():
            block = self.get_component(name)
            
            if block.on_it():
                self._set_text_block(block, text)

    def _set_text_block(self, block:Block, text:str):
        '''
        Set the text block corresponding to the active block.
        '''
        text_block = self.get_component('t block')

        # set pos of block text
        x, y = block.get_pos()

        x += self.get_component('b block').get_dim()[0]

        text_block.set_pos((x,y), scale=True)

        text_block.set_text(text)

        self.change_display_state('t block', True)

    def _change_grid_block(self, block: Block):
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
        # will contain every connected block's coordinate
        self.block_chain = []

        # get a block
        n_active_block = 0
        first_block = None
        for block in self.blocks:
            if block.type > 0:
                n_active_block += 1
                first_block = block

        if n_active_block == 0:
            return False

        # add first block to chain
        self.block_chain.append(first_block.coord)

        self._is_connected_chain(*first_block.coord)

        # check that every block is in the block chain
        return len(self.block_chain) == n_active_block

    def _is_connected_chain(self, x, y):
        '''
        Get all blocks connected to the given one,  
        add each of them to the block chain if they're not already in it.  
        If no new block is found, stop.
        '''
        coords = self._check_block_connected(x, y)

        new = False

        for coord in coords:
            if not coord in self.block_chain:
                new = True
                self.block_chain.append(coord)

        if not new:
            return

        for coord in coords:
            self._is_connected_chain(*coord)

    def _check_block_connected(self, x, y):
        '''
        Return a list of the block's coord that are next the given coordinate
        '''
        coords = []
        
        if x != 0:
            if self.grid[x - 1, y] > 0:
                coords.append((x-1, y))
        
        if x != Spec.SIZE_GRID_SHIP - 1:
            if self.grid[x + 1, y] > 0:
                coords.append((x+1, y))
        
        if y != 0:
            if self.grid[x, y - 1] > 0:
                coords.append((x, y-1))
        
        if y != Spec.SIZE_GRID_SHIP - 1:
            if self.grid[x, y + 1] > 0:
                coords.append((x, y+1))
        
        return coords
