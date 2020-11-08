from lib.plougame import Interface, Page, TextBox, InputText, Button, Font, C
from ui.chat import Chat
from spec import Spec
import numpy as np

### TOP BAR ###

Y_TB = 100
Y_TB2 = 200
X_TB1 = 100
X_TB2 = 550

POS_CHAT = np.array([2000, 900], dtype='int16')
POS_ERROR = np.array([X_TB1, Y_TB + 100], dtype='int16')
POS_NOTIF = np.array([X_TB2 + 230, Y_TB-20], dtype='int16')

### Components ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                            text="CodeShip", font=Font.f(80))
        
text_error = TextBox(Spec.DIM_MEDIUM_TEXT, POS_ERROR, color=C.DARK_RED,
                    text="", font=Font.f(25), marge=True, text_color=C.WHITE)

button_conn = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB), color=C.LIGHT_BLUE,
                    text="Connect", font=Font.f(40))

button_logout = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB2), color=C.LIGHT_BLUE,
                    text="Log out", font=Font.f(40))

text_username = TextBox(Spec.DIM_MEDIUM_TEXT, (X_TB1, Y_TB),
                    text="", font=Font.f(50), marge=True)

button_friends = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB2, Y_TB), color=C.LIGHT_BLUE,
                    text="Friends", font=Font.f(40))

button_ship = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB2, Y_TB2), color=C.LIGHT_BLUE,
                    text="Ship editor", font=Font.f(40))

notif = TextBox(Spec.DIM_NOTIF, POS_NOTIF, color=C.LIGHT_RED, text_color=C.WHITE,
                    text='0', font=Font.f(20))

chat = Chat(POS_CHAT, general_chat=True)

states = ['unlogged', 'logged']

components = [
    ('title', title),
    ('t error', text_error),
    ('b conn', button_conn),
    ('b logout', button_logout),
    ('t username', text_username),
    ('b friends', button_friends),
    ('b ship', button_ship),
    ('notif', notif),
    ('chat', chat)
]

class Menu(Page):

    def __init__(self, client):

        self.client = client
        self.username = None

        # set client in chat
        chat.client = client

        super().__init__(states, components)

        self.set_states_components(None, 'title')
        self.set_states_components('unlogged', ['b conn'])
        self.set_states_components('logged',
            ['t username', 'b friends', 'b ship', 'chat', 'b logout'])

        self.add_button_logic('b conn', self.conn)
        self.add_button_logic('b friends', self.friends)
        self.add_button_logic('b ship', self.ship)

        self.set_out_state_func('unlogged', self.out_unlogged)
        self.set_in_state_func('logged', self.to_logged)

    def out_unlogged(self):
        # reset text error
        self.change_display_state("t error", False)

    def to_logged(self):
        # set the username
        self.set_text('t username', self.username)

    def friends(self):
        # go to the friends page
        self.change_page(Spec.PAGE_FRIENDS)
        
    def ship(self):
        # go to the ship page
        self.change_page(Spec.PAGE_SHIP)

    def conn(self):
        # try to connect to the server
        if not self.client.connected:
            is_connected = self.client.connect()
        else:
            is_connected = True

        if is_connected:
            # go to the connection page
            self.change_page(Spec.PAGE_CONN)
        else:
            # set text error
            self.set_text("t error","Couldn't connect to the server.")
            self.change_display_state("t error", True)