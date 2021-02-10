from lib.plougame import Page
from data.spec import Spec
import os, glob, json
import numpy as np

states = ['bases']

class Offline(Page):

    def __init__(self, client):

        components = Spec.formatter.get_components('ui/data/page.json')

        super().__init__(states, components, active_states='all')

        self.client = client

        self.get_component('script analyser').client = client
        self.get_component('ship editor').client = client

        self.add_button_logic('back', self.go_back)

        self.load_local_data()

        self.get_component('ship editor').set_grid(self.client.in_data['sh'])
    
    def load_local_data(self):
        '''
        Load the data that is stored in local.
        '''
        paths = glob.glob(os.path.join('data', 'accounts', '*.json'))
        path = paths[0]

        with open(path, 'r') as file:
            self.user_data = json.load(file)
        
        self.username = self.user_data['username']

        # set value in client
        self.client.in_data['sc'] = '\n'.join(self.user_data['script'])
        self.client.in_data['sh'] = np.array(self.user_data['ship'])
        self.client.in_data['scst'] = self.user_data['script status']
        self.client.in_data['shst'] = self.user_data['ship status']