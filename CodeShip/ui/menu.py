from lib.plougame import Interface, Page, TextBox, InputText, Button, Font, C
from ui.chat import Chat
from ui.updater import Updater
from data.spec import Spec
import numpy as np

### TOP BAR ###

Y_TB = 100
Y_TB2 = 200
X_TB1 = 100
X_TB2 = 400
X_TB3 = 700

POS_UPDATER = np.array([2500, 300])
POS_CHAT = np.array([2100, 1000])
POS_ERROR_CONN = np.array([X_TB1, Y_TB + 100])
POS_ERROR_PLAY = np.array([1800, 420])
POS_NOTIF = np.array([X_TB2 + 230, Y_TB2-20])
POS_PLAY = np.array([1440, 400])

### Components ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                            text="CodeShip", font=Font.f(80))
        
text_error = TextBox(None, POS_ERROR_CONN, color=C.DARK_RED, dynamic_dim=True,
                    text="", font=Font.f(25), marge=True, text_color=C.WHITE)

button_conn = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB), color=C.LIGHT_BLUE,
                    text="Connect", font=Font.f(40))

button_logout = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB2), color=C.LIGHT_BLUE,
                    text="Log out", font=Font.f(40))

text_username = TextBox(None, (X_TB1, Y_TB), dynamic_dim=True,
                    text="", font=Font.f(50), marge=True)

button_friends = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB2, Y_TB2), color=C.LIGHT_BLUE,
                    text="Friends", font=Font.f(40))

button_editor = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB3, Y_TB2), color=C.LIGHT_BLUE,
                    text="Editor", font=Font.f(40))

button_play = Button(Spec.DIM_BIG_BUTTON, POS_PLAY, color=C.LIGHT_BLUE,
                    text="Play", font=Font.f(60))

notif = TextBox(Spec.DIM_NOTIF, POS_NOTIF, color=C.LIGHT_RED, text_color=C.WHITE,
                    text='0', font=Font.f(25))

chat = Chat(POS_CHAT, general_chat=True)
updater = Updater(POS_UPDATER)

states = ['unlogged', 'logged']

components = [
    ('title', title),
    ('t error', text_error),
    ('b conn', button_conn),
    ('b logout', button_logout),
    ('t username', text_username),
    ('b friends', button_friends),
    ('b editor', button_editor),
    ('b play', button_play),
    ('notif', notif),
    ('chat', chat),
    ('updater', updater)
]

class Menu(Page):

    def __init__(self, client):

        self.client = client

        # set client in chat
        chat.client = client

        self.waiting_game = False

        super().__init__(states, components)

        self.set_states_components(None, 'title')
        self.set_states_components('unlogged', ['b conn', 'updater'])
        self.set_states_components('logged',
        ['t username', 'b friends', 'b editor', 'chat', 'b logout', 'b play'])

        self.add_button_logic('b conn', self.b_conn)
        self.add_button_logic('b friends', self.b_friends)
        self.add_button_logic('b editor', self.b_ship)
        self.add_button_logic('b play', self.b_play)

        self.set_out_state_func('unlogged', self.out_unlogged)
        self.set_out_state_func('logged', self.out_logged)
        self.set_in_state_func('logged', self.to_logged)

    def out_unlogged(self):
        # reset text error
        self.change_display_state("t error", False)

    def out_logged(self):
        # set error pos
        self.get_component('t error').set_pos(POS_ERROR_CONN, scale=True)

    def to_logged(self):
        # set the username
        self.set_text('t username', self.client.username)

        # set error pos
        self.change_display_state('t error', False)
        self.get_component('t error').set_pos(POS_ERROR_PLAY, scale=True)

    def reset_play(self):
        '''
        Set the play button in his normal state
        '''
        self.waiting_game = False
            
        # change button text
        button = self.get_component('b play')
        button.font = Font.f(60)
        button.set_text("Play")

    def b_play(self):
        '''
        If not waiting for a game:
        Check if the user is ready to start a game,
        if yes: set the user waiting for a game.  
        Else:
        Cancel waiting for game.
        '''
        if not self.waiting_game:
            # get status without context manager
            # -> keep info for potential later call
            ship_status = self.client.in_data['shst']
            script_status = self.client.in_data['scst']

            if ship_status == 0:
                self.change_display_state('t error', True)
                self.set_text('t error', "The ship is not ready.")
                return

            if script_status == 0:
                self.change_display_state('t error', True)
                self.set_text('t error', "The script is not ready.")
                return

            self.waiting_game = True

            # set the user waiting to enter the game
            self.client.send_wait_game_status(True)
            
            # change button text
            button = self.get_component('b play')
            button.font = Font.f(30)
            button.set_text("Waiting for opponent...")
        
        else:
            # remove the user from waiting list
            self.client.send_wait_game_status(False)

            self.reset_play()

    def b_friends(self):
        # go to the friends page
        self.change_page(Spec.PAGE_FRIENDS)
        
    def b_ship(self):
        # go to the ship page
        self.change_page(Spec.PAGE_SHIP)

    def b_conn(self):
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
            self.set_text("t error", "Couldn't connect to the server.")
            self.change_display_state("t error", True)