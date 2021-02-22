from lib.plougame import Page, TextBox, Button, Font, C
from data.spec import Spec
import os, glob, json
import numpy as np


class Offline(Page):

    game = None

    def __init__(self, client):

        components = Spec.formatter.get_components('ui/data/offline.json')

        super().__init__(['base'], components, active_states='all')

        self.client = client
        self.loaded_data = False

        self.set_states_components([], ['t error', 'scroll accounts'])

        self.get_component('script analyser').client = client
        self.get_component('ship editor').client = client

        self.add_button_logic('b play', self.b_play)
        self.add_button_logic('b back', self.go_back)
        self.add_button_logic('b account', self.b_accounts)
        self.set_in_state_func('base', self.in_base)
        self.set_out_state_func('base', self.out_base)
    
    def in_base(self):
        '''
        Execute script analyser, ship editor in base methods
        '''
        # if not done, load data stored on local
        if not self.loaded_data:
            self.loaded_data = True
            self.load_local_data(Spec.JSON_DATA['active account'])
            self.get_component('ship editor').set_grid(self.client.in_data['sh'])

        self.get_component('ship editor').in_base()
        self.get_component('script analyser').in_base()
        self.change_display_state('t error', False)
        self.change_display_state('scroll accounts', False)

    def out_base(self):
        self.get_component('scroll accounts').clear()

    def b_play(self):
        '''
        Start a game against a bot
        '''
        # load up-to-date data
        self._load_user_data(self.username)

        if not self.user_data['ship status']:
            self.change_display_state('t error', True)
            self.set_text('t error', "The ship is not ready.")
            return
        
        if not self.user_data['script status']:
            self.change_display_state('t error', True)
            self.set_text('t error', "The script is not ready.")
            return

        # load grid
        grid = np.array(Spec.load_user_data(self.client.username)['ship'])

        self.game.setup_with_bot(1, grid, self.client.username)

    def b_accounts(self):
        '''
        Display the accounts existing on local,  
        give the possibility to change of current account.  
        Fill and display the scroll list of accounts
        '''
        self.change_display_state('scroll accounts', True)
        scroll = self.get_component('scroll accounts')

        paths = glob.glob('data/accounts/*.json')

        for path in paths:
            username = path.split('/')[-1].split('.')[0]
            
            line = self._create_account_choice(username)
            scroll.add_line(line)

    def load_local_data(self, username):
        '''
        Load the data of the given username.  
        If the client doesn't have any account,
        create a "Unregistered" account.  
        Setup client's data.
        '''
        if username == None:
            self._create_unregistered_account()
            username = "Unregistered"

            # set active account -> avoid regenerating an unregistered file each time
            Spec.set_json_variable('active account', "Unregistered")

        path = f"data/accounts/{username}.json"

        self._load_user_data(path=path)

        self.get_component('t username').set_text(self.username)
    
    def _load_user_data(self, username=None, path=None):
        '''
        Load the data of a user,  
        set the client's in_data attributes,
        and "username" attribute.
        '''
        if path == None:
            path = f"data/accounts/{username}.json"

        with open(path, 'r') as file:
            self.user_data = json.load(file)
        
        self.username = self.user_data['username']

        # set values in client
        self.client.username = self.username
        self.client.in_data['sc'] = '\n'.join(self.user_data['script'])
        self.client.in_data['sh'] = np.array(self.user_data['ship'])
        self.client.in_data['scst'] = self.user_data['script status']
        self.client.in_data['shst'] = self.user_data['ship status']

    def _create_unregistered_account(self):
        '''
        Create a default account in `data/accounts/Unregistered.json`
        '''
        
        with open('data/accounts/Unregistered.json', 'w') as file:
            json.dump({
                "username": "Unregistered",
                "updated": False,
                "script status": False,
                "ship status": False,
                "ship": np.zeros(Spec.SHAPE_GRID_SHIP, dtype=int).tolist(),
                "script": ['']
            }, file, indent=4)
    
    def _create_account_choice(self, username) -> list:
        '''
        Create the components of the scroll line
        corresponding to the given username.  
        Return them `[list]`
        '''
        text = TextBox([200, 50], [0, 0], text=username, font=Font.f(30),
                    centered=False)

        button_pick = Button([120, 40], [300, 5], color=C.LIGHT_BLUE, text="Pick",
                            font=Font.f(25))

        button_pick.set_logic(self._get_button_choice_logic(username))

        return [text, button_pick]
    
    def _get_button_choice_logic(self, username):
        '''
        Return the logic of the button "pick"
        '''
        def logic():
            self.load_local_data(username)
            self.change_state('base')
            
            # update data.json active account
            Spec.set_json_variable('active account', username)
        
        return logic