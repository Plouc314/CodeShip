import pygame
import time
import numpy as np
from lib.plougame import Page, Form, Cadre, TextBox, Button, InputText, Font, C
from game.api import API
from game.player import Player
from game.geometry import get_deg
from data.spec import Spec
from lib.perfeval import Counter

### TOP BAR

Y_TB = np.array([0,100])
Y_TB2 = np.array([0,190])

X_TB = np.array([10,0])
X_TB2 = np.array([300,0])

POS_TIME = np.array([Spec.CENTER_X-Spec.DIM_MEDIUM_TEXT[0]//2, Y_TB[1]])
POS_CADRE1 = np.array([50,50])
POS_CADRE2 = np.array([2550,50])
DIM_CADRE = np.array([550, 400])
DIM_USER = np.array([400, 80])
POS_USER = np.array([100, 20])
DIM_TEXT_INFO = np.array([400, 290])
DIM_TEXT_VALUE = np.array([200, 190])
DIM_HP = np.array([230, 30])
POS_HP = X_TB2 + Y_TB + np.array([0, 10])
POS_SHIELD_HP = POS_HP + np.array([0, 38])
DIM_TWIN = np.array([600, 200])
POS_TWIN = np.array([Spec.CENTER_X-300, 200])
DIM_TCAUSE = np.array([600, 60])
POS_TCAUSE = POS_TWIN + np.array([0, 210])
POS_EXIT = np.array([POS_TWIN[0]+360 , POS_TWIN[1] + 280])

DIM_CADRE_ACTIONS = np.array([400, 400])
DIM_TITLE_ACTIONS = np.array([390, 50])
POS_CADRE_ACTS1 = np.array([600, 50])
POS_CADRE_ACTS2 = np.array([2150, 50])
POS_TITLE_ACTS = np.array([5,5])
POS_TEXT_ACTS = np.array([5, 60])
DIM_TEXT_ACTS = np.array([390, 390])

titles = ['HP', 'Shield', 'Engine', 'Speed', 'Orientation', 'Script errors']

### components ###

text_time = TextBox(Spec.DIM_MEDIUM_TEXT, POS_TIME, marge=True, color=C.XLIGHT_GREY, font=Font.f(40))

cadre_1 = Cadre(DIM_CADRE, POS_CADRE1)
cadre_2 = Cadre(DIM_CADRE, POS_CADRE2)
cadre_1.MARGE_WIDTH = 8
cadre_2.MARGE_WIDTH = 8

cadre_acts_1 = Cadre(DIM_CADRE_ACTIONS, POS_CADRE_ACTS1, color=C.XLIGHT_BLUE)
cadre_acts_2 = Cadre(DIM_CADRE_ACTIONS, POS_CADRE_ACTS2, color=C.XLIGHT_BLUE)

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

form_red_shield_hp1 = Form(DIM_HP, POS_CADRE1 + POS_SHIELD_HP, color=C.RED)
form_blue_shield_hp1 = Form(DIM_HP, POS_CADRE1 + POS_SHIELD_HP, color=C.NEO_BLUE)

form_red_shield_hp2 = Form(DIM_HP, POS_CADRE2 + POS_SHIELD_HP, color=C.RED)
form_blue_shield_hp2 = Form(DIM_HP, POS_CADRE2 + POS_SHIELD_HP, color=C.NEO_BLUE)

text_info1 = TextBox(DIM_TEXT_INFO, POS_CADRE1 + X_TB + Y_TB, font=Font.f(35), centered=False,
            text=titles, continuous_text=True)

text_info2 = TextBox(DIM_TEXT_INFO, POS_CADRE2 + X_TB + Y_TB, font=Font.f(35), centered=False,
            text=titles, continuous_text=True)

text_value1 = TextBox(DIM_TEXT_VALUE, POS_CADRE1 + X_TB2 + Y_TB2, font=Font.f(35),
            text=['' for _ in range(4)], continuous_text=True, centered=False)

text_value2 = TextBox(DIM_TEXT_VALUE, POS_CADRE2 + X_TB2 + Y_TB2, font=Font.f(35),
            text=['' for _ in range(4)], continuous_text=True, centered=False)

title_actions1 = TextBox(DIM_TITLE_ACTIONS, POS_CADRE_ACTS1 + POS_TITLE_ACTS, font=Font.f(35),
            text='Script Actions', color=C.XLIGHT_BLUE)

title_actions2 = TextBox(DIM_TITLE_ACTIONS, POS_CADRE_ACTS2 + POS_TITLE_ACTS, font=Font.f(35),
            text='Script Actions', color=C.XLIGHT_BLUE)

text_actions1 = TextBox(DIM_TEXT_VALUE, POS_CADRE_ACTS1 + POS_TEXT_ACTS, font=Font.f(25),
            continuous_text=True, centered=False, color=C.XLIGHT_BLUE)

text_actions2 = TextBox(DIM_TEXT_VALUE, POS_CADRE_ACTS2 + POS_TEXT_ACTS, font=Font.f(25),
            continuous_text=True, centered=False, color=C.XLIGHT_BLUE)

text_win = TextBox(DIM_TWIN, POS_TWIN, font=Font.f(90), marge=True)

text_cause = TextBox(DIM_TCAUSE, POS_TCAUSE, font=Font.f(30), color=C.XLIGHT_GREY, marge=True)

text_actions1.set_marge_text(5)
text_actions2.set_marge_text(5)

text_info1.set_text_color([C.DARK_GREEN, C.DARK_BLUE, C.DARK_YELLOW, C.BLACK, C.DARK_PURPLE, C.DARK_RED])
text_info2.set_text_color([C.DARK_GREEN, C.DARK_BLUE, C.DARK_YELLOW, C.BLACK, C.DARK_PURPLE, C.DARK_RED])

text_value1.set_text_color([C.DARK_YELLOW, C.BLACK, C.DARK_PURPLE, C.DARK_RED])
text_value2.set_text_color([C.DARK_YELLOW, C.BLACK, C.DARK_PURPLE, C.DARK_RED])

states = ['base', 'end']

components = [
    ('t time', text_time),
    ('cadre actions 1', cadre_acts_1),
    ('cadre actions 2', cadre_acts_2),
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
    ('f red shield hp1', form_red_shield_hp1),
    ('f blue shield hp1', form_blue_shield_hp1),
    ('f red shield hp2', form_red_shield_hp2),
    ('f blue shield hp2', form_blue_shield_hp2),
    ('title actions1', title_actions1),
    ('title actions2', title_actions2),
    ('t actions1', text_actions1),
    ('t actions2', text_actions2),
    ('t win', text_win),
    ('t cause', text_cause),
]

class GameInterface(Page):

    MAX_ACTIONS = 10

    def __init__(self, client):

        self.start_time = None
        self.clock_active = False
        self.client = client
        self.has_opp_max_shield = False

        super().__init__(states, components, active_states='all')

        self.set_states_components('end', ['b quit', 't win', 't cause'])

    def set_players(self, own_player: Player, opp_player: Player):
        '''
        Set the two players
        '''
        self.own_player = own_player
        self.opp_player = opp_player

        self.set_text(f't username{own_player.team}', own_player.username)
        self.set_text(f't username{opp_player.team}', opp_player.username)

    def start_clock(self):
        '''
        Set the time of the begining of the game
        '''
        self.clock_active = True
        self.start_time = time.time()

    def set_end_game(self, has_win, cause):
        '''
        Set the interface to the end game state.    
        `has_win`: if own user has win the game.  
        `cause`: the cause of the game's end
        '''
        text_title = self.get_component('t win')
        if has_win:
            text_title.set_text('You won!')
            text_title.set_color(C.GREEN, marge=True)
        else:
            text_title.set_text('You lost...')
            text_title.set_color(C.RED, marge=True)

        self.set_text('t cause', cause)

        # stop the clock
        self.clock_active = False

        self.change_state('end')

    def set_hp(self, team, ship):
        '''
        Set the hp info of the specified player
        '''
        # get total hp of ship
        total_hp = Spec.HP_BLOCK * ship.initial_n_block
        current_hp = sum((block.hp for block in ship.blocks.values()))

        # set green form length
        dim_x = (current_hp / total_hp) * DIM_HP[0]

        form = self.get_component(f'f green hp{team}')
        form.set_dim((dim_x, DIM_HP[1]), scale=True)

    def set_shield_hp(self, team, player):
        '''
        Set the shield info
        '''
        if not self.has_opp_max_shield:
            return

        shields = player.ship.typed_blocks['Shield']
        total_hp = player.total_shield_hp
        current_hp = sum((block.hp_shield for block in player.ship.blocks.values()))

        # set blue form length
        if total_hp == 0:
            dim_x = 0
        else:
            dim_x = (current_hp / total_hp) * DIM_HP[0]

        if dim_x <= 0:
            dim_x = DIM_HP[0]

        form = self.get_component(f'f blue shield hp{team}')
        form.set_dim((dim_x, DIM_HP[1]), scale=True)

    def _set_value(self, idx, value, team):
        '''
        Set the value of the line at the given index of the specified team.
        '''
        # change the line of text corresponding to the info
        text = self.get_component(f't value{team}')
        lines = text.get_text(lines=True)

        # check if the value is new
        if lines[idx] == value:
            return

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

    def update_api_actions(self, player):
        '''
        Update the API pending actions
        '''
        text = self.get_component(f't actions{player.team}')

        lines = []

        for action in player.get_cache(string_format=True):
            lines.append(action)

        if len(lines) == 0:
            lines = ''

        text.set_text(lines)

    def update(self):
        '''
        Update the interface's infos.
        '''
        # get opp shield info
        if not self.has_opp_max_shield:
            shield_hp = self.client.in_data['gis']
            if not shield_hp is None:
                self.has_opp_max_shield = True

        # update time
        if self.clock_active:
            current_time = time.time() - self.start_time
            string = time.strftime("%M:%S", time.gmtime(current_time))
            self.set_text('t time', string)

        self.update_api_actions(self.own_player)
        self.update_api_actions(self.opp_player)

        self.set_hp(self.own_player.team, self.own_player.ship)
        self.set_hp(self.opp_player.team, self.opp_player.ship)

        self.set_shield_hp(self.own_player.team, self.own_player)
        self.set_shield_hp(self.opp_player.team, self.opp_player)

        self.set_engine_level(self.own_player.team, self.own_player.ship)
        self.set_engine_level(self.opp_player.team, self.opp_player.ship)

        self._set_value(1, f'{self.own_player.ship.get_speed(scalar=True):.0f}',
            self.own_player.team)
        self._set_value(1, f'{self.opp_player.ship.get_speed(scalar=True):.0f}',
            self.opp_player.team)          

        self._set_value(2, f'{get_deg(self.own_player.ship.orien):.0f}', self.own_player.team)
        self._set_value(2, f'{get_deg(self.opp_player.ship.orien):.0f}', self.opp_player.team)

        self._set_value(3, f'{self.own_player.n_script_error}', self.own_player.team)
        self._set_value(3, f'{self.opp_player.n_script_error}', self.opp_player.team)