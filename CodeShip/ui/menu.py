from lib.plougame import Interface, Page, TextBox, InputText, Button, Font, C
from data.spec import Spec
import numpy as np

POS_ERROR_CONN = np.array([100, 200])
POS_ERROR_PLAY = np.array([1800, 420])

states = ['unlogged', 'logged', 'ask data']

class Menu(Page):

    def __init__(self, client):

        components = Spec.formatter.get_components('ui/data/menu.json')

        super().__init__(states, components)

        self.waiting_game = False

        self.client = client
        self.get_component('chat').client = client

        self.set_states_components(None, 'title')
        self.set_states_components('unlogged', ['doc', 'updater', 'b offline'])
        self.set_states_components('logged',
        ['t username', 'b friends', 'b editor', 'chat', 'b logout', 'b play'])

        self.set_states_components('ask data', 
            ['t title data', 't info data', 'b keep data', 'b revert data'])

        # logic play set in app.py
        self.add_button_logic('b conn', self.b_conn)
        self.add_button_logic('b friends', self.b_friends)
        self.add_button_logic('b editor', self.b_ship)
        self.add_button_logic('b play', self.b_play)
        self.add_button_logic('b offline', self.b_offline)
        self.add_button_logic('b revert data', self.b_revert)
        self.add_button_logic('b keep data', self.b_keep)

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
        button.set_font(**Font.f(60))
        button.set_text("Play")

    def check_user_data(self):
        '''
        Check if there is data of the user on local,  
        if so, check if there was an update on this data,  
        if so, ask wether to keep these updates or revert them.
        '''
        if Spec.is_user_data(self.client.username):
            data = Spec.load_user_data(self.client.username)
            
            if data['updated']:
                self.change_state('ask data')

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
            button.set_font(**Font.f(30))
            button.set_text("Waiting for opponent...")
        
        else:
            # remove the user from waiting list
            self.client.send_wait_game_status(False)

            self.reset_play()

    def b_keep(self):
        ''' Send local data to the server '''
        data = Spec.load_user_data(self.client.username)

        script = '\n'.join(data['script'])
        grid = np.array(data['ship'])

        self.client.in_data['scst'] = data['script status']
        self.client.in_data['sc'] = script
        self.client.in_data['sh'] = grid
        self.client.in_data['shst'] = data['ship status']

        self.client.send_script(script)
        self.client.send_script_status(data['script status'])
        self.client.send_ship_config(grid)

        # go to logged state
        self.change_state('logged')

    def b_revert(self):
        ''' Go to logged state (data will be stored on local when quiting)'''
        # go to logged state
        self.change_state('logged')

    def b_offline(self):
        # go to the offline page
        self.change_page(Spec.PAGE_OFFLINE)

    def b_friends(self):
        # go to the friends page
        self.change_page(Spec.PAGE_FRIENDS)
        
    def b_ship(self):
        # go to the ship page
        self.change_page(Spec.PAGE_EDITOR)

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