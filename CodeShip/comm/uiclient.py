import threading
from lib.tcp import ClientTCP
from data.spec import Spec
import numpy as np

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class UIClient(ClientTCP):

    def __init__(self, addr, connect=False):

        super().__init__(addr, connect=connect)
        self.username = None

        # store the identifiers of the comm as key
        # the values are the msg send by the server
        self.in_data = {
            'rlg' : None, # response login
            'rsg' : None, # response sign up
            'frs' : None, # friends connected
            'rdfr': None, # response on friend demand
            'dfr' :   [], # friend demands (from other users) 
            'gc'  :   [], # message on general chat
            'pc'  :   [], # message on private chat
            'rpd' : None, # response to profil demand
            'sh'  : None, # ship array
            'shst': None, # ship status
            'sc'  : None, # script
            'scst': None, # script status (if it's ready or not)
            'rsca': None, # result of script analyse
            'ign' : None, # notify as in game, contains opp's username, id
            'igsh': None, # opponent's ship grid
        }

        # store the identifiers of the comm as key
        # for each key, a function will process the incoming data
        self.processes = {
            'rlg' : lambda x: int(x),
            'rsg' : lambda x: int(x),
            'frs' : self.on_friends,
            'rdfr': lambda x: int(x),
            'dfr' : lambda x: x,
            'gc'  : self.on_chat_msg,
            'pc'  : self.on_chat_msg,
            'rpd' : self.on_profil_infos,
            'sh'  : self.on_ship,
            'shst': lambda x: int(x),
            'sc'  : lambda x: x,
            'scst': lambda x: int(x),
            'rsca': lambda x: int(x),
            'ign' : lambda x: x.split(sep_c),
            'igsh': self.opponent_grid,
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
        identifier, content = msg.split(sep_m)

        if identifier != "sc":
            print('[TCP]', msg)

        content = self.processes[identifier](content)

        container = self.in_data[identifier]

        if type(container) == list:
            container.append(content)
        else:
            self.in_data[identifier] = content

    def get_data(self, identifier):
        '''
        To use as a context manager.  
        Return the specified data container(s) (`str` or `list`),   
        will free the container(s) after exit of context.
        '''
        return ContextManager(self, identifier)

    def on_chat_msg(self, content):
        '''
        Return chat msg in format: `[username, message]`
        '''
        return content.split(sep_c)

    def on_friends(self, content):
        '''
        Return friends in format: `list` `[username, is_connected]`
        '''
        content = content.split(sep_c)
        content = [data.split(sep_c2) for data in content]
        return [[username, int(conn)] for username, conn in content]

    def on_profil_infos(self, content):
        '''
        Return the infos in format: `{username, wins, loss, friends, grid}`
        '''
        username, wins, loss, friends, grid = content.split(sep_c)

        wins = int(wins)
        loss = int(loss)

        friends = friends.split(sep_c2)

        grid = np.array(grid.split(sep_c2), dtype=int)
        grid = grid.reshape(Spec.SHAPE_GRID_SHIP)

        return {'username':username, 'wins':wins, 'loss':loss, 'friends':friends, 'grid':grid}

    def on_ship(self, content):
        '''
        Return the ship as a np.ndarray.
        '''
        arr = content.split(sep_c2)
        arr = np.array(arr, dtype=int)
        return arr.reshape(Spec.SHAPE_GRID_SHIP)

    def opponent_grid(self, content):
        '''
        Set the opponent's ship grid
        '''
        arr = content.split(sep_c2)
        arr = np.array(arr, dtype=int)
        return arr.reshape(Spec.SHAPE_GRID_SHIP)

    def send_logout(self):
        '''
        Send to the server that client is logging out.
        ID: lo
        '''
        self.send(f'lo{sep_m}')

    def send_login(self, username, password):
        '''
        Send the login information to the server.  
        ID : lg
        '''
        msg = f'lg{sep_m}{username}{sep_c}{password}'

        self.send(msg)
    
    def send_sign_up(self, username, password):
        '''
        Send the sign up information to the server.  
        ID : sg
        '''
        msg = f'sg{sep_m}{username}{sep_c}{password}'

        self.send(msg)

    def send_general_chat_msg(self, message):
        '''
        Send a message on the general chat.
        ID : gc
        '''
        msg = f'gc{sep_m}{message}'

        self.send(msg)

    def send_private_chat_msg(self, username, message):
        '''
        Send a message on the general chat.
        ID : pc
        '''
        msg = f'pc{sep_m}{username}{sep_c}{message}'

        self.send(msg)

    def send_demand_friend(self, username):
        '''
        Send a friend demand.
        ID: dfr
        '''
        msg = f'dfr{sep_m}{username}'

        self.send(msg)

    def send_response_dfr(self, username, response):
        '''
        Send if accepted or not a friend demand.
        ID: rdfr
        '''
        self.send(f'rdfr{sep_m}{username}{sep_c}{int(response)}')

    def send_ship_config(self, arr):
        '''
        Send the new ship of client.
        ID: shcf
        '''
        msg = f'shcf{sep_m}'

        for x in range(Spec.SIZE_GRID_SHIP):
            for y in range(Spec.SIZE_GRID_SHIP):
                msg += f'{arr[x,y]}{sep_c}'

        # remove last sep
        msg = msg[:-1]

        self.send(msg)

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

        self.send(f'{identifier}{sep_m}{script}')

    def send_script_status(self, status):
        '''
        Send the status of the script
        ID: scst
        '''
        self.send(f'scst{sep_m}{int(status)}')

    def send_wait_game_status(self, status):
        '''
        Send if the user is waiting to enter a game
        ID: wg
        '''
        self.send(f'wg{sep_m}{int(status)}')

    def send_end_game(self, has_win):
        '''
        Send that the game is finished, send if user has win the game.
        ID: egst
        '''
        self.send(f'egst{sep_m}{int(has_win)}')

    def send_profil_demand(self, username):
        '''
        Send a demand for the server to send info about the user
        ID: pd
        '''
        self.send(f'pd{sep_m}{username}')

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
            'dfr' :   [],
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