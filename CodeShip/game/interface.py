import pygame
import time
import numpy as np
from lib.plougame import Page, Form, Cadre, TextBox, Button, InputText, Font, C
from game.api import API
from data.spec import Spec
from lib.counter import Counter

### TOP BAR

Y_TB = np.array([0,100])
Y_TB2 = np.array([0,150])

X_TB = np.array([10,0])
X_TB2 = np.array([350,0])

POS_TIME = np.array([Spec.CENTER_X-Spec.DIM_MEDIUM_TEXT[0]//2, Y_TB[1]])
POS_CADRE1 = np.array([50,50])
POS_CADRE2 = np.array([2550,50])
DIM_CADRE = np.array([600, 400])
DIM_USER = np.array([400, 80])
POS_USER = np.array([100, 20])
DIM_TEXT_INFO = np.array([400, 290])
DIM_TEXT_VALUE = np.array([200, 230])
DIM_HP = np.array([230, 30])
POS_HP = X_TB2 + Y_TB + np.array([0, 10])
DIM_TWIN = np.array([600, 200])
POS_TWIN = np.array([Spec.CENTER_X-300, 200])
POS_EXIT = np.array([POS_TWIN[0]+360 , POS_TWIN[1] + 220])

### components ###

text_time = TextBox(Spec.DIM_MEDIUM_TEXT, POS_TIME, marge=True, color=C.XLIGHT_GREY)

cadre_1 = Cadre(DIM_CADRE, POS_CADRE1)
cadre_2 = Cadre(DIM_CADRE, POS_CADRE2)
cadre_1.MARGE_WIDTH = 8
cadre_2.MARGE_WIDTH = 8

text_username1 = TextBox(DIM_USER, POS_CADRE1 + POS_USER,
            text_color=Spec.DCOLOR_P1, font=Font.f(60))

text_username2 = TextBox(DIM_USER, POS_CADRE2 + POS_USER,
            text_color=Spec.DCOLOR_P2, font=Font.f(60))

button_quit = Button(Spec.DIM_MEDIUM_BUTTON, POS_EXIT, color=C.LIGHT_BLUE,
                text="Quit", font=Font.f(30))

form_red_hp1 = Form(DIM_HP, POS_CADRE1 + POS_HP, color=C.RED)
form_green_hp1 = Form(DIM_HP, POS_CADRE1 + POS_HP, color=C.GREEN)

form_red_hp2 = Form(DIM_HP, POS_CADRE2 + POS_HP, color=C.RED)
form_green_hp2 = Form(DIM_HP, POS_CADRE2 + POS_HP, color=C.GREEN)

text_info1 = TextBox(DIM_TEXT_INFO, POS_CADRE1 + X_TB + Y_TB, font=Font.f(40), centered=False,
            text=['HP', 'Engine', 'Speed', 'Acceleration'], continuous_text=True)

text_info2 = TextBox(DIM_TEXT_INFO, POS_CADRE2 + X_TB + Y_TB, font=Font.f(40), centered=False,
            text=['HP', 'Engine', 'Speed', 'Acceleration'], continuous_text=True)

text_value1 = TextBox(DIM_TEXT_VALUE, POS_CADRE1 + X_TB2 + Y_TB2, font=Font.f(40),
            text=['','',''], continuous_text=True, centered=False)

text_value2 = TextBox(DIM_TEXT_VALUE, POS_CADRE2 + X_TB2 + Y_TB2, font=Font.f(40),
            text=['','',''], continuous_text=True, centered=False)

text_win = TextBox(DIM_TWIN, POS_TWIN, font=Font.f(90), marge=True)

states = ['base', 'end']

components = [
    ('t time', text_time),
    ('cadre 1', cadre_1),
    ('t username1', text_username1),
    ('cadre 2', cadre_2),
    ('t username2', text_username2),
    ('b quit', button_quit),
    ('t info1', text_info1),
    ('t info2', text_info2),
    ('t value1', text_value1),
    ('t value2', text_value2),
    ('f red hp1', form_red_hp1),
    ('f green hp1', form_green_hp1),
    ('f red hp2', form_red_hp2),
    ('f green hp2', form_green_hp2),
    ('t win', text_win),
]

class GameInterface(Page):

    def __init__(self, client):

        self.start_time = None
        self.clock_active = False
        self.client = client

        super().__init__(states, components, active_states='all')

        self.set_states_components('end', ['b quit', 't win'])

    def start_clock(self):
        '''
        Set the time of the begining of the game
        '''
        self.clock_active = True
        self.start_time = time.time()

    def set_end_game(self, has_win):
        '''
        Set the interface to the end game state.    
        `has_win`: if own user has win the game.
        '''
        text = self.get_component('t win')
        if has_win:
            text.set_text('You won!')
            text.set_color(C.GREEN, marge=True)
        else:
            text.set_text('You lost...')
            text.set_color(C.RED, marge=True)

        # stop the clock
        self.clock_active = False

        self.change_state('end')

    def set_hp(self, team, ship):
        '''
        Set the hp info of the specified player
        '''
        # get total hp of ship
        total_hp = Spec.HP_BLOCK * ship.initial_n_block
        current_hp = 0
        for block in ship.blocks.values():
            current_hp += block.hp
        
        # set green form length
        dim_x = (current_hp / total_hp) * DIM_HP[0]

        form = self.get_component(f'f green hp{team}')
        form.set_dim((dim_x, DIM_HP[1]), scale=True)

    def _set_value(self, idx, value, team):
        '''
        Set the value of the line at the given index of the specified team.
        '''
        # change the line of text corresponding to the info
        text = self.get_component(f't value{team}')
        lines = text.get_text(lines=True)

        lines[idx] = value
        text.set_text(lines)

    def set_engine_level(self, team, ship):
        '''
        Set the engine level info of the specified player
        '''
        # get total motor force (percentage)
        total_force = 0
        for block in ship.typed_blocks['Engine']:
            total_force += block.activation_per

        self._set_value(0, f'{100*total_force}%', team)

    @Counter.add_func
    def update(self, ship1, ship2):
        '''
        Update the interface's infos given the ships,  
        ship1 should correspond to user1 and same for ship2.
        '''
        # update time
        if self.clock_active:
            current_time = time.time() - self.start_time
            string = time.strftime("%M:%S", time.gmtime(current_time))
            self.set_text('t time', string)

        self.set_hp(1, ship1)
        self.set_hp(2, ship2)

        self.set_engine_level(1, ship1)
        self.set_engine_level(2, ship2)

        self._set_value(1, f'{ship1.get_speed(scalar=True):.0f}', 1)
        self._set_value(1, f'{ship2.get_speed(scalar=True):.0f}', 2)

        self._set_value(2, f'{ship1.get_acc(scalar=True):.2f}', 1)
        self._set_value(2, f'{ship2.get_acc(scalar=True):.2f}', 2)

    def set_users(self, user1, user2):
        '''
        Set the two users,  
        user1 should be the one with the position 1 (`Spec.POS_P1`),  
        user2 should be the one with the position 2 (`Spec.POS_P2`)
        '''
        self.set_text('t username1', user1)
        self.set_text('t username2', user2)