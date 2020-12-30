import requests, json, threading, time
from lib.plougame import SubPage, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from data.spec import Spec
from lib.counter import Counter
import numpy as np

DIM_CADRE = np.array([600, 200])
POS_TEXT = np.array([100, 20])
DIM_INFO = np.array([540, 80])
POS_INFO = np.array([30, 100])

# components

cadre = Cadre(DIM_CADRE, (0,0))

text_state = TextBox(Spec.DIM_MEDIUM_TEXT, POS_TEXT, text='Looking for update...',
            font=Font.f(40), text_color=C.GREY)

text_info = TextBox(DIM_INFO, POS_INFO, font=Font.f(30))

components = [
    ('cadre', cadre),
    ('t state', text_state),
    ('t info', text_info)
]

states = ['base']

class Updater(SubPage):

    root_link = "https://raw.githubusercontent.com/Plouc314/CodeShip/master/CodeShip/"

    def __init__(self, pos):
        
        self.is_thread_active = False
        self.is_connection_error = False
        self.has_server_data = False
        self.is_update_done = False
        self.updating = False

        super().__init__(states, components, pos, active_states='all')

    def stop_thread(self, name):
        '''
        Call `join` method on the specified thread: `"server"` or `"update"`   
        Set `is_thread_active` attribute to `False` if both thread are dead.
        '''
        if name == 'server':
            self.thread_server.join()
        elif name == 'update':
            self.thread_update.join()
        
        if self.thread_server and not self.thread_server.is_alive():
            if self.thread_update and not self.thread_update.is_alive():
                self.is_thread_active = False
        
    def load_server_data(self):
        '''
        Load the json data from github in a separated thread.  
        `is_thread_active` attribute will be set to `True` as long as
        `thread` attribute is active.    
        `has_server_data` attribute will be set to `True` if
        the download was succesful.  
        `is_connection_error` attribute will be set to `True` if
        the connection couldn't be establish.
        '''
        self.is_thread_active = True
        self.thread_server = threading.Thread(target=self._load_data)
        self.thread_server.start()

    def _load_data(self):
        '''
        Load the json data from github.
        '''
        # let the user see that he's loading data
        time.sleep(.5)

        try:
            data = requests.get(self.root_link + "data/data.json").text

        except requests.exceptions.ConnectionError:
            self.is_connection_error = True

        self.server_data = json.loads(data)
        self.has_server_data = True

    def set_error_state(self):
        '''
        Set the text info to display an error message.
        '''
        self.set_text('t state', "Connection error")
        self.set_text('t info', "Couldn't reach github.com\nPlease check your internet connection.")

    def set_update_state(self):
        '''
        Set text info that the game is being updated.
        '''
        self.set_text('t state', "Updating...")
        self.get_component('t info').set_centered(False)
        # text info's text is set in self._update

    def set_ok_state(self):
        '''
        Set text info that the game is up to date.
        '''
        self.set_text('t state', "Up to date")
        self.get_component('t info').set_centered(True)
        self.set_text('t info', "Latest version installed.\n ")

    def is_outdated(self):
        '''
        Return if the local game is an outdated version
        (if an update has been released).
        '''
        with open('data/data.json', 'r') as file:
            self.local_data = json.load(file)
        
        return self.local_data['version'] != self.server_data['version']

    def update(self):
        '''
        Download and replace every file by the new version one, in a separated thread.  
        `updating` attribute will be set to `True`.  
        `is_thread_active` attribute will be set to `True` as long as
        `thread` attribute is active.    
        `is_update_done` attribute will be set to `True` if
        the update was succesful.  
        `is_connection_error` attribute will be set to `True` if
        the connection couldn't be establish.
        '''
        self.is_thread_active = True
        self.updating = True
        self.thread_update = threading.Thread(target=self._udpate)
        self.thread_update.start()

    @Counter.add_func
    def _udpate(self):
        '''
        Actual implementation of `update`,
        which only call `_update` in a separated thread.
        '''
        # download
        files_scr = []
        n_files = len(self.server_data['files'])

        for i, filename in enumerate(self.server_data['files']):
            
            try:
                response = requests.get(self.root_link + filename)
            
            except requests.exceptions.ConnectionError:
                self.is_connection_error = True
                return

            if response.status_code != 200:
                self.is_connection_error = True
                return
            
            files_scr.append(response)

            # update text info
            self.set_text('t info', f'({i+1}/{n_files}) {filename}')

        # update text info
        self.set_text('t info', "Writing files to disk...")

        # replace
        for filename, scr in zip(self.server_data['files'], files_scr):
            
            if '.png' in filename:
                with open(filename, 'wb') as file:
                    file.write(scr.content)
            
            else:
                with open(filename, 'w') as file:
                    file.write(scr.text)
        
        self.is_update_done = True