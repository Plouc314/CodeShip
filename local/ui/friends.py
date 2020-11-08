import pygame
from lib.plougame import Page, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from ui.chat import Chat
from spec import Spec
import numpy as np

Y_TB = 100
X_TB1 = 100
X_TB2 = 550

POS_CHAT = np.array([2000, 900])
POS_SCR_FRS = np.array((500, 500))
DIM_SCR_FRS = np.array((1200, 600))

POS_SCR_DFRS = np.array((2500, 180))
DIM_SCR_DFRS = np.array((600, 400))

DIM_TITLE_DFR = np.array([DIM_SCR_DFRS[0], 80])
POS_TITLE_DFR = np.array([POS_SCR_DFRS[0], POS_SCR_DFRS[1]-80])

POS_BACK = np.array([X_TB1,Y_TB])
POS_ADD_FR = np.array([1460,440])

POS_CADRE = np.array([POS_ADD_FR[0] + 250,POS_ADD_FR[1]])
POS_USER = np.array([POS_CADRE[0] + 10,POS_CADRE[1] + 10])
POS_SEND = np.array([POS_USER[0] + 410,POS_USER[1]])

POS_ERROR = np.array([POS_CADRE[0],POS_CADRE[1]+70])

DIM_CADRE = np.array([630,60])

## friend line ##
DIM_CONN = np.array([30,30])
POS_CONN = np.array([500,25])
POS_PROFIL = np.array([700,20])
POS_PLAY = np.array([930,20])

DIM_CADRE_LINE = np.array([1160,80])

## dfr line ##
DIM_DFR_BUTT = np.array([60,40])
DIM_ICON = np.array([512, 512])
POS_ICON = (15*DIM_DFR_BUTT - DIM_ICON)//2

POS_DFR_TEXT = np.array([20, 00])
POS_YES = np.array([400, 10])
POS_NO = np.array([480, 10])

DIM_CADRE_LINE_DFR = np.array([560,60])

### Components ###

### base ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Friends", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

button_add_fr = Button(Spec.DIM_MEDIUM_BUTTON, POS_ADD_FR, color=C.LIGHT_BLUE,
                text="Add friend", font=Font.f(30))

scroll_frs = ScrollList(DIM_SCR_FRS, POS_SCR_FRS, [])

chat = Chat(POS_CHAT, general_chat=False)

### dfr ###

title_dfr = TextBox(DIM_TITLE_DFR, POS_TITLE_DFR, 
                text="Friend requests", font=Font.f(40))

scroll_dfrs = ScrollList(DIM_SCR_DFRS, POS_SCR_DFRS, [])

img_vu = pygame.image.load("imgs/correct.png")
vu = pygame.Surface(15*DIM_DFR_BUTT, pygame.SRCALPHA)
vu.blit(img_vu, POS_ICON)

img_cross = pygame.image.load("imgs/cross.png")
cross = pygame.Surface(15*DIM_DFR_BUTT, pygame.SRCALPHA)
cross.blit(img_cross, POS_ICON)


### add fr ###

cadre_add_fr =  Cadre(DIM_CADRE, POS_CADRE)

input_userame = InputText(Spec.DIM_SMALL_TEXT, POS_USER, has_marge=False,
                pretext="Enter a username...", font=Font.f(25))

button_send = Button(Spec.DIM_SMALL_BUTTON, POS_SEND, color=C.LIGHT_BLUE,
                text="Send", font=Font.f(25))

text_rdfr = TextBox(Spec.DIM_SMALL_TEXT, POS_ERROR, color=C.DARK_RED,
                font=Font.f(20), text_color=C.WHITE)

states = ['base', 'add fr']

components = [
    ('title', title),
    ('title dfr', title_dfr),
    ('b back', button_back),
    ('b add fr', button_add_fr),
    ('s frs', scroll_frs),
    ('s dfrs', scroll_dfrs),
    ('c add fr', cadre_add_fr),
    ('i username', input_userame),
    ('b send', button_send),
    ('t rdfr', text_rdfr),
    ('chat', chat)
]

class Friends(Page):

    def __init__(self, client):

        self.client = client
        self.friends = {} # dict:dict {connected, index} store info of friends: 
        self.demand_friends = []

        super().__init__(states, components)

        self.set_in_state_func('base', self.in_base)

        self.set_states_components(None, ['title', 'b back'])
        self.set_states_components(['base','add fr'], 
                ['b add fr', 's frs', 's dfrs', 'title dfr'])
    
        self.set_states_components('add fr', ['c add fr', 'i username', 'b send'])

        self.add_button_logic('b add fr', self.add_friend)
        self.add_button_logic('b back', self.go_back)
        self.add_button_logic('b send', self.send)

    def reset(self):
        '''
        Reset friends and friend demands
        '''
        self.get_component('s frs').clear()
        self.get_component('s dfrs').clear()

        self.friends = {}
        self.demand_friends = []

    def in_base(self):
        # reset demand friend components
        self.change_display_state('t rdfr', False)
        self.get_component('i username').reset_text(pretext="Enter a username...")
    
    def add_friend(self):
        '''pass to add fr state'''
        self.change_state('add fr')

    def send(self):
        '''Send (try to) a friend demand'''

        inp = self.get_component('i username')

        username = inp.get_text()

        # send friend demand
        self.client.send_demand_friend(username)

    def get_n_dfr(self):
        '''
        Return the number of active friend demands
        '''
        return len(self.demand_friends)

    def set_rdfr(self, response):
        '''
        Get the response from the server of if the friend demand occured an error.
        '''
        inp = self.get_component('i username')
        text = self.get_component('t rdfr') 
        username = inp.get_text()
        
        self.change_display_state('t rdfr', True)

        if response == 1:
            inp.reset_text(pretext="Enter username...")

            text.set_color(C.DARK_GREEN)
            text.set_text(f'Demand sent succesfully to "{username}".')

        else:
            inp.reset_text(pretext="Try again...")

            text.set_color(C.DARK_RED)
            text.set_text(f'There is no user named "{username}".')

    def set_friend(self, username, connected):
        '''
        Set up a friend, if already setup update it,   
        else store info of it, 
        create line on scroll list
        '''
        if not username in self.friends.keys():
            self.friends[username] = {
                'connected': connected,
                'index': len(self.friends)
            }
            self._add_friend_line(username)
        
        else:
            self.friends[username]['connected'] = connected

            scroll = self.get_component('s frs')
            line = scroll.get_line(self.friends[username]['index'])

            # update connected color
            line[2].set_color(self._get_color_connected(username))

    def set_demand_friend(self, username):
        '''
        Set up a friend demand, if already setup update it,   
        else store info of it, 
        create line on scroll list
        '''
        if not username in self.demand_friends:
            self.demand_friends.append(username)

            self._add_demand_friend_line(username)

    def _get_color_connected(self, username):
        '''
        return color corresponding of if the friend is connected.
        '''
        if self.friends[username]['connected']:
            return C.GREEN
        else:
            return C.RED

    def _add_friend_line(self, username):
        '''
        Add a line to the friend scroll list.
        '''
        cadre = Cadre(DIM_CADRE_LINE, (0,0))

        text_username = TextBox(Spec.DIM_MEDIUM_TEXT, (20, 10),
                            text=username, font=Font.f(30))
        
        color = self._get_color_connected(username)

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
    
    def _add_demand_friend_line(self, username):
        '''
        Add a line to the demand friend scroll list.
        '''
        cadre = Cadre(DIM_CADRE_LINE_DFR, (0,0))

        text_username = TextBox(Spec.DIM_MEDIUM_TEXT, POS_DFR_TEXT,
                            text=username, font=Font.f(30))

        button_yes = Button(DIM_DFR_BUTT, POS_YES, color=C.LIGHT_GREEN,
                        surface=vu, with_font=True)
        
        button_no = Button(DIM_DFR_BUTT, POS_NO, color=C.LIGHT_RED,
                        surface=cross, with_font=True)

        # add line
        scroll = self.get_component('s dfrs')

        scroll.add_line([
            cadre, 
            text_username, 
            button_yes,
            button_no
        ])

        line = scroll.get_line(-1)

        # set buttons logic
        button_yes.set_logic(self._get_dfr_logic(line, True))
        button_no.set_logic(self._get_dfr_logic(line, False))
    
    def _get_dfr_logic(self, line, response):
        '''
        Return a function composing the logic of one of the demand friend button
        '''
        scroll = self.get_component('s dfrs')
        
        def logic():
            username = line[1].get_text()

            self.client.send_response_dfr(username, response)

            # remove dfr
            self.demand_friends.remove(username)
            scroll.remove_line(line=line)
        
        return logic