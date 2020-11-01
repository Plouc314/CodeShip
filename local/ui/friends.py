from lib.plougame import Interface, Page, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from spec import Spec
import numpy as np

Y_TB = 100
X_TB1 = 100
X_TB2 = 550

POS_SCR = (500, 500)
DIM_SCR = (1200, 600)

POS_BACK = np.array([X_TB1,Y_TB], dtype='int16')
POS_ADD_FR = np.array([1460,440], dtype='int16')

POS_CADRE = np.array([POS_ADD_FR[0] + 250,POS_ADD_FR[1]], dtype='int16')
POS_USER = np.array([POS_CADRE[0] + 10,POS_CADRE[1] + 10], dtype='int16')
POS_SEND = np.array([POS_USER[0] + 410,POS_USER[1]], dtype='int16')

POS_ERROR = np.array([POS_CADRE[0],POS_CADRE[1]+70], dtype='int16')

DIM_CADRE = np.array([630,60], dtype='int16')

## friend line ##
DIM_CONN = np.array([30,30], dtype='int16')
POS_CONN = np.array([500,25], dtype='int16')
POS_PROFIL = np.array([700,20], dtype='int16')
POS_PLAY = np.array([930,20], dtype='int16')

DIM_CADRE_LINE = np.array([1160,80], dtype='int16')

### Components ###

### base ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Friends", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

button_add_fr = Button(Spec.DIM_MEDIUM_BUTTON, POS_ADD_FR, color=C.LIGHT_BLUE,
                text="Add friend", font=Font.f(30))

scroll_frs = ScrollList(DIM_SCR, POS_SCR, [])

### add fr ###

cadre_add_fr =  Cadre(DIM_CADRE, POS_CADRE)

input_userame = InputText(Spec.DIM_SMALL_TEXT, POS_USER, has_marge=False,
                pretext="Enter a username...", font=Font.f(25))

button_send = Button(Spec.DIM_SMALL_BUTTON, POS_SEND, color=C.LIGHT_BLUE,
                text="Send", font=Font.f(25))

text_error = TextBox(Spec.DIM_SMALL_TEXT, POS_ERROR, color=C.LIGHT_RED,
                font=Font.f(20), text_color=C.WHITE)

states = ['base', 'add fr']

components = [
    ('title', title),
    ('b back', button_back),
    ('b add fr', button_add_fr),
    ('s frs', scroll_frs),
    ('c add fr', cadre_add_fr),
    ('i username', input_userame),
    ('b send', button_send),
    ('t error', text_error)
]

class Friends(Page):

    def __init__(self, client):

        self.client = client
        self.friends = {} # dict:dict {connected} store info of friends: 

        super().__init__(states, components)

        self.set_in_state_func(self.in_base)

        self.set_states_components(None, ['title', 'b back'])
        self.set_states_components(['base','add fr'], ['b add fr', 's frs'])
    
        self.set_states_components('add fr', ['c add fr', 'i username', 'b send'])

        self.add_button_logic('b add fr', self.b_add_friend)
        self.add_button_logic('b back', self.b_back)
        self.add_button_logic('b send', self.b_send)

    def in_base(self):
        self.change_display_state('t error', False)

    def b_back(self):
        '''go back of one state'''
        self.go_back()
    
    def b_add_friend(self):
        '''pass to add fr state'''
        self.change_state('add fr')

    def b_send(self):
        '''Send (try to) a friend demand'''
        self.change_display_state('t error', True)

        inp = self.get_component('i username')

        username = inp.get_text()
        inp.reset_text(pretext="Try again...")

        self.set_text('t error', f'There is no user named "{username}".')

    def add_friend(self, username, connected):
        '''
        Set up a new friend, 
        store info of it, 
        create line on scroll list
        '''
        self.friends[username] = {'connected':connected}
        
        self._add_friend_line(username)

    def _add_friend_line(self, username):
        '''
        Add a line to the scroll list.
        '''
        cadre = Cadre(DIM_CADRE_LINE, (0,0))

        text_username = TextBox(Spec.DIM_MEDIUM_TEXT, (20, 10),
                            text=username, font=Font.f(30))
        
        if self.friends[username]['connected']:
            color = C.GREEN
        else:
            color = C.RED

        form_connected = Form(DIM_CONN, POS_CONN, color)

        button_profil = Button(Spec.DIM_SMALL_BUTTON, POS_PROFIL, color=C.LIGHT_BLUE,
                        text="Profil", font=Font.f(25))

        button_play = Button(Spec.DIM_SMALL_BUTTON, POS_PLAY, color=C.LIGHT_GREEN,
                        text="Play", font=Font.f(25))

        # add line
        scroll = self.get_component('s frs')

        scroll.add_line([
            cadre, 
            text_username, 
            form_connected, 
            button_profil,
            button_play
        ])