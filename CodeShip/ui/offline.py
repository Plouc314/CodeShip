from lib.plougame import Page
from data.spec import Spec
import os, glob, json
import numpy as np

states = ['base']

class Offline(Page):

    game = None

    def __init__(self, client):

        components = Spec.formatter.get_components('ui/data/offline.json')

        super().__init__(states, components, active_states='all')

        self.client = client

        self.get_component('script analyser').client = client
        self.get_component('ship editor').client = client

        self.add_button_logic('b play', self.b_play)
        self.add_button_logic('b back', self.go_back)
        self.set_in_state_func('base', self.in_base)

        self.load_local_data()

        self.get_component('ship editor').set_grid(self.client.in_data['sh'])
    
    def in_base(self):
        '''
        Execute script analyser, ship editor in base methods
        '''
        self.get_component('ship editor').in_base()
        self.get_component('script analyser').in_base()

    def b_play(self):
        '''
        Start a game against a bot
        '''
        # load grid
        grid = np.array(Spec.load_user_data(self.client.username)['ship'])

        self.game.setup_with_bot(1, grid, self.client.username)

    def load_local_data(self):
        '''
        Load the data that is stored in local.  
        Setup client's data.
        '''
        paths = glob.glob(os.path.join('data', 'accounts', '*.json'))
        path = paths[0]

        with open(path, 'r') as file:
            self.user_data = json.load(file)
        
        self.username = self.user_data['username']

        self.get_component('t username').set_text(self.username)

        # set values in client
        self.client.username = self.username
        self.client.in_data['sc'] = '\n'.join(self.user_data['script'])
        self.client.in_data['sh'] = np.array(self.user_data['ship'])
        self.client.in_data['scst'] = self.user_data['script status']
        self.client.in_data['shst'] = self.user_data['ship status']