import pygame
from lib.plougame import Interface, Page, Form, TextBox, ScrollList, Cadre, Button, Font, C
from ui.chat import Chat
from game.ship import Ship
from lib.spec import Spec
import numpy as np

### TOP BAR ###

Y_TB = 100
Y_TB2 = 200
X_TB1 = 100
X_TB2 = 400
X_TB3 = 700

DIM_CADRE = np.array([1650, 420])
POS_CADRE = np.array([300, 400])

POS_TABLE = np.array([730, 540])
DX = np.array([300, 0])
DY = np.array([0, 80])
DIM_CASE = np.array([300, 80])

POS_CHAT = np.array([2100, 1000])
POS_BACK = np.array([X_TB1,Y_TB])
POS_TEXT_RDFR = np.array([2500, 830])

DIM_SHIP = np.array([380, 380])
POS_SHIP = np.array([320, 420])

DIM_SCR_FRS = np.array([600, 420])
POS_SCR_FRS = np.array([2500, 400])
POS_TITLE_SCR = np.array([2600, 320])

## fr line ##
DIM_FRL_CADRE = np.array([600, 80])
DIM_L_USERNAME = np.array([300, 60])
DIM_L_BUTTON = np.array([160, 40])
POS_L_BUTTON = np.array([340, 20])

DX_L = np.array([20, 0])
DY_L = np.array([0, 10])

### Components ###

img_question = pygame.image.load("imgs/question_mark.png")

chat = Chat(POS_CHAT, general_chat=False)

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

cadre = Cadre(DIM_CADRE, POS_CADRE)

form_ship = Cadre(DIM_SHIP, POS_SHIP)

title_games = TextBox(DIM_CASE, POS_TABLE, text='Games', 
                marge=True, font=Font.f(40))

title_wins = TextBox(DIM_CASE, POS_TABLE + DX, text='Wins', 
                marge=True, font=Font.f(40))

title_loss = TextBox(DIM_CASE, POS_TABLE + 2*DX, text='Loss', 
                marge=True, font=Font.f(40))

title_ratio = TextBox(DIM_CASE, POS_TABLE + 3*DX, text='Ratio W/L', 
                marge=True, font=Font.f(40))

text_games = TextBox(DIM_CASE, POS_TABLE + DY,
                marge=True, font=Font.f(50))

text_wins = TextBox(DIM_CASE, POS_TABLE + DY + DX, text_color=C.DARK_GREEN,
                marge=True, font=Font.f(50))

text_loss = TextBox(DIM_CASE, POS_TABLE + DY + 2*DX, text_color=C.DARK_RED,
                marge=True, font=Font.f(50))

text_ratio = TextBox(DIM_CASE, POS_TABLE + DY + 3*DX,
                marge=True, font=Font.f(50))

title_scroll = TextBox(Spec.DIM_BIG_TEXT, POS_TITLE_SCR, text='Friends', font=Font.f(50))

scroll_friends = ScrollList(DIM_SCR_FRS, POS_SCR_FRS, [])

text_rdfr = TextBox(None, POS_TEXT_RDFR, color=C.DARK_GREEN,
                font=Font.f(20), text_color=C.WHITE, dynamic_dim=True)

states = ['base']

components = [
    ('title', title),
    ('b back', button_back),
    ('chat', chat),
    ('cadre', cadre),
    ('f ship', form_ship),
    ('ti games', title_games),
    ('ti wins', title_wins),
    ('ti loss', title_loss),
    ('ti ratio', title_ratio),
    ('t games', text_games),
    ('t wins', text_wins),
    ('t loss', text_loss),
    ('t ratio', text_ratio),
    ('ti scr', title_scroll),
    ('s frs', scroll_friends),
    ('t rdfr', text_rdfr)
]

class Profil(Page):

    def __init__(self, client):

        self.client = client
        chat.client = client
        
        # username of current active friend
        self.target = None

        # store the messages of every private conv
        self.convs = {}
        # store a count of the number of unread messages by conv
        self.unreads = {}

        super().__init__(states, components, active_states='all')

        self.set_states_components([], 't rdfr')

        self.add_button_logic('b back', self.on_leave)

    def on_leave(self):
        '''
        Leave page,
        reset target,
        store messages.
        '''
        self.target = None
        self.store_messages()
        self.go_back()
        self.change_display_state('t rdfr', False)

    def reset(self):
        '''
        Clear convs, unreads and chat.
        '''
        self.target = None
        self.convs = {}
        self.unreads = {}
        self.get_component('chat').reset()

    def get_n_unreads(self):
        '''
        Return the total number of unreads message
        '''
        return sum(self.unreads.values())

    def add_message(self, sender, msg):
        '''
        Add a message to the profil page (from the server).  
        Can be the active friend or not.
        '''
        # initialise conv if not done yet
        if not sender in self.convs.keys():
            self.convs[sender] = []
            self.unreads[sender] = 0

        # if is current target -> add msg to chat
        if sender == self.target:
            chat = self.get_component('chat')
            chat.add_msg(sender, msg)
        
        else: # store msg for later
            self.convs[sender].append({'username':sender, 'message':msg})
            self.unreads[sender] += 1

    def store_messages(self):
        '''
        Store the messages of the private conv
        '''
        chat = self.get_component('chat')
        msgs = chat.get_messages()
        chat.reset()

        username = self.get_component('title').get_text()
        self.convs[username] = msgs

    def set_chat(self, username):
        '''
        If the chat had already a private conv -> set it back,  
        given the username of the friend
        '''
        if not username in self.convs.keys():
            return

        chat = self.get_component('chat')

        for container in self.convs[username]:
            chat.add_msg(container['username'], container['message'])

    def setup_page(self, username, wins, loss, friends, grid):
        '''
        Set up the page given the all the infos
        '''
        self.target = username
        self.set_text('title', username)
        self.set_text('t games', str(wins + loss))
        self.set_text('t wins', str(wins))
        self.set_text('t loss', str(loss))

        if loss == 0:
            ratio = wins
        else:
            ratio = wins/loss

        self.set_text('t ratio', f'{ratio:.2f}')

        scroll = self.get_component('s frs')
        scroll.clear()
        
        for friend in friends:
            self._add_fr_line(friend)

        self.get_component('chat').target = username
        self.set_chat(username)
        self.setup_ship(grid)
        self.unreads[username] = 0

    def setup_ship(self, grid):
        '''
        Create the ship surface
        '''
        # create ship surface
        form_ship = self.get_component('f ship')
        
        # if not ship set -> put question mark image
        if not np.any(grid):
            form_ship.set_surface(img_question)
        else:
            ship = Ship.from_grid(0, grid)
            ship.compile()

            form_ship.set_surface(ship.get_surface('original'))

    def set_rdfr(self, response):
        '''
        Get the response from the server of if the friend demand occured an error.
        '''
        text = self.get_component('t rdfr')
        self.change_display_state('t rdfr', True)

        if response == 1:
            text.set_color(C.DARK_GREEN)
            text.set_text("Demand sent succesfully.")
        else:
            text.set_color(C.DARK_RED)
            text.set_text("Something went wrong...")

    def _add_fr_line(self, username):
        '''
        Add a line to the friend scroll list.
        '''
        cadre = Cadre(DIM_FRL_CADRE, (0,0))
        
        text_username = TextBox(DIM_L_USERNAME, DX_L + DY_L, text=username, 
                        font=Font.f(40))
        
        button_requests = Button(DIM_L_BUTTON, POS_L_BUTTON, color=C.LIGHT_BLUE,
                            text='Add', font=Font.f(25))

        scroll = self.get_component('s frs')

        scroll.add_line([
            cadre,
            text_username,
            button_requests
        ])

        # set buttons logic
        line = scroll.get_line(-1)
    
        button_requests.set_logic(self._get_request_logic(line))

    def _get_request_logic(self, line):
        '''
        Return a function composing the logic of the requests button
        '''
        def logic():
            username = line[1].get_text()

            self.client.send_demand_friend(username)
        
        return logic