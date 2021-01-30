import threading, pickle
from lib.tcp import ClientTCP, Message, ErrorTCP
from lib.console import Console
from data.spec import Spec
import numpy as np

class UIClient(ClientTCP):

    def __init__(self, addr, connect=False):

        super().__init__(addr, connect=connect)
        self.username = None

        self._script_cache = []

        # store the identifiers of the comm as key
        # the values are the msg send by the server
        self.in_data = {
            'rlg' : None, # response login
            'rsg' : None, # response sign up
            'frs' : None, # friends connected
            'rdfr': None, # response on friend demand
            'rdg' : None, # response on game demand
            'dfr' :   [], # friend demands (from other users) 
            'dg'  :   [], # game demands (from other users) 
            'gc'  :   [], # message on general chat
            'pc'  :   [], # message on private chat
            'rpd' : None, # response to profil demand
            'sh'  : None, # ship array
            'shst': None, # ship status
            'sc'  : None, # script
            'scst': None, # script status (if it's ready or not)
            'rsca': None, # result of script analyse
            'ign' : None, # notify as in game, contains opp's username, team
            'igsh': None, # opponent's ship grid
            'gis' : None, # opponent info after initalisation
            'ige' : None, # opponent's number of errors in script
        }

    def connect(self):
        '''
        Try to connect to the server.  
        Also launch the run loop.  
        Return True if the connection succeeds.
        '''
        is_connected = super().connect()

        if is_connected:
            # launch run loop
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

        return is_connected

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Store the content in the designated container.
        '''
        try:
            msg = pickle.loads(msg)
        except:
            ErrorTCP.call("Unpickling failed.")
            return

        # look for script line
        if msg.identifier == 'scl':
            self._script_cache.append(msg.content)
            return

        elif msg.identifier == 'sc':
            msg.content = '\n'.join(self._script_cache)
            self._script_cache = []

        container = self.in_data[msg.identifier]

        if type(container) == list:
            container.append(msg.content)
        else:
            self.in_data[msg.identifier] = msg.content
        
        self.display_msg(msg)

    def get_data(self, identifier):
        '''
        To use as a context manager.  
        Return the specified data container(s) (`str` or `list`),   
        will free the container(s) after exit of context.
        '''
        return ContextManager(self, identifier)

    def display_msg(self, msg: Message):
        '''
        Display the Message to the terminal
        in a pretty printing way.
        '''
        if type(msg.content) is str and '\n' in msg.content:
            content = ''
        elif type(msg.content) is np.ndarray:
            content = ''
        
        # player stats
        elif msg.identifier == 'rpd':
            content = msg.content['username']

        else:
            content = str(msg.content)

        Console.print('[TCP] {' + msg.identifier + '} ' + content)

    def _send_script(self, script: str):
        '''
        Send the script by little chunk to the client
        '''
        for line in script.split('\n'):
            self.send(Message('scl', line), pickling=True)

    def connect_udp(self, port):
        '''
        Send the udp port to enable the server to send udp msg to local
        '''
        self.send(Message('udp', port), pickling=True)

    def send_logout(self):
        '''
        Send to the server that client is logging out.
        ID: lo
        '''
        self.send(Message('lo', None), pickling=True)

    def send_login(self, username, password):
        '''
        Send the login information to the server.  
        ID : lg
        '''
        self.send(Message('lg', [username, password]), pickling=True)
    
    def send_sign_up(self, username, password):
        '''
        Send the sign up information to the server.  
        ID : sg
        '''
        self.send(Message('sg', [username, password]), pickling=True)

    def send_general_chat_msg(self, message):
        '''
        Send a message on the general chat.
        ID : gc
        '''
        self.send(Message('gc', message), pickling=True)

    def send_private_chat_msg(self, username, message):
        '''
        Send a message on the general chat.
        ID : pc
        '''
        self.send(Message('pc', [username, message]), pickling=True)

    def send_demand_friend(self, username):
        '''
        Send a friend demand.
        ID: dfr
        '''
        self.send(Message('dfr', username), pickling=True)

    def send_response_dfr(self, username, response):
        '''
        Send if accepted or not a friend demand.
        ID: rdfr
        '''
        self.send(Message('rdfr', [username, response]), pickling=True)

    def send_demand_game(self, username):
        '''
        Send a game demand.
        ID: dg
        '''
        self.send(Message('dg', username), pickling=True)

    def send_response_game_demand(self, username, response):
        '''
        Send if accepted or not a game demand.
        ID: rdg
        '''
        self.send(Message('rdg', [username,response]), pickling=True)

    def send_ship_config(self, arr):
        '''
        Send the new ship of client.
        ID: shcf
        '''
        self.send(Message('shcf', arr), pickling=True)

    def send_script(self, script, analysis=False):
        '''
        Send the script stored on the local file to the server.  
        If analysis=True, send script for analysis -> will receive a response
        ID: sc/sca
        '''
        if analysis:
            identifier = 'sca'
        else:
            identifier = 'sc'

        self._send_script(script)
        self.send(Message(identifier, None), pickling=True)

    def send_script_status(self, status):
        '''
        Send the status of the script
        ID: scst
        '''
        self.send(Message('scst', status), pickling=True)

    def send_wait_game_status(self, status):
        '''
        Send if the user is waiting to enter a game
        ID: wg
        '''
        self.send(Message('wg', status), pickling=True)

    def send_end_game(self, has_win):
        '''
        Send that the game is finished, send if user has win the game.
        ID: egst
        '''
        self.send(Message('egst', has_win), pickling=True)

    def send_profil_demand(self, username):
        '''
        Send a demand for the server to send info about the user
        ID: pd
        '''
        self.send(Message('pd', username), pickling=True)

    def send_game_init_info(self, max_shield_hp):
        '''
        Send some info on the player's state after the
        initalisation.
        ID: gis
        '''
        self.send(Message('gis', max_shield_hp), pickling=True)
    
    def send_in_game_error(self, n_error):
        '''
        Send to the other user the number of error that occured in the script.
        ID: ige
        '''
        self.send(Message('ige', n_error), pickling=True)

class ContextManager:
    '''
    Context manager used to get `in_data` content and free it after use.
    '''

    def __init__(self, client, identifier):
        self.client = client

        self.default_in_data = {
            'rlg' : None,
            'rsg' : None,
            'frs' : None,
            'rdfr': None,
            'rdg' : None,
            'dfr' :   [],
            'dg'  :   [],
            'gc'  :   [],
            'pc'  :   [],
            'rpd' : None,
            'sh'  : None,
            'shst': None,
            'sc'  : None,
            'scst': None,
            'rsca': None,
            'ign' : None,
            'igsh': None,
            'gis' : None,
            'ige' : None,
        }

        # pass identifiers to list
        if type(identifier) != list:
            self.id = [identifier]
        else:
            self.id = identifier
    
    def __enter__(self):
        data = [self.client.in_data[id] for id in self.id]
        
        if len(data) == 1:
            return data[0]
        else:
            return data
    
    def __exit__(self, type, value, tb):
        '''Free every containers'''
        
        for id in self.id:
            # free the container
            self.client.in_data[id] = self.default_in_data[id]