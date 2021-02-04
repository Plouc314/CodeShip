import numpy as np
import pickle
from lib.tcp import ClientTCP, Message
from lib.console import Console
from tcp.interaction import Interaction
from db.db import DataBase
from spec import Spec

class Client(ClientTCP):

    def __init__(self, conn, addr):

        super().__init__(conn, addr)

        self.logged = False
        self.username = None
        self.opponent = None # current opponent username

        # unique tag to identify the game in Interaction
        self.game_tag = None

        # store the script lines temporarely
        self._script_cache = []

        # store the identifiers of the comm as key
        # the values are the methods called for each of the identifier
        self.identifiers = {
            'lo': self.on_disconnect, # log out
            'lg': self.login,
            'sg': self.sign_up,
            'udp': self.connect_udp,
            'gc': self.general_chat,
            'pc': self.private_chat,
            'dfr': self.demand_friend,
            'rdfr': self.response_demand_friend,
            'dg': self.demand_game,
            'rdg': self.response_demand_game,
            'shcf': self.ship_config,
            'scl': self.on_script_line,
            'sc': self.save_script,
            'scst': self.set_script_status,
            'sca': self.script_analysis,
            'wg': self.set_waiting_game_state,
            'egst': self.end_game,
            'gis': self.on_game_init_state,
            'ige': self.in_game_error,
            'pd': self.profil_demand
        }

    def on_disconnect(self, content=None):
        '''
        Executed on disconnection, to have a clean disconnection
        '''
        self.logged = False
        self.print("Disconnected.")

        if self.username is None:
            return
        
        # inform friends
        Interaction.send_connection_state(self.username, False)

        # remove from Interaction
        Interaction.remove(self.username)

        # if in game -> inform opponent that is leaving
        if not self.game_tag is None:
            Interaction.send(self.opponent, Message('olg',True))

            # count game as a loss
            DataBase.increment_loss(self.username)

        self.username = None

    def connect_udp(self, content):
        '''
        Set udp client in udp socket
        '''
        address = (self.ip, content)
        Interaction.connect_udp(address)

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Call the method linked to the identifier.
        '''
        try:
            msg = pickle.loads(msg)
        except:
            self.print("Error occured in unpickling opperation.", warning=True)
            return

        try:
            self.identifiers[msg.identifier](msg.content)
        except:
            self.print(f"Error occured in identifier attribution: {msg.identifier}", warning=True)

        # display message
        self.display_msg(msg)

    def _log_client(self, username):
        '''
        Internal method.  
        Set attributes to log in. 
        '''
        self.logged = True
        self.username = username

        Interaction.clients[username] = self

        Interaction.send_connection_state(self.username, True)

        self._send_basic_infos()

        self.print("Logged.")

    def _send_basic_infos(self):
        '''
        Send the basic informations, friends, ...
        '''
        self._send_connected_friends()
        self._send_ship()

        # script
        script = DataBase.get_script(self.username)
        self._send_script(script)
        self.send(Message('sc', None), pickling=True)

        # script status
        script_status = DataBase.get_script_status(self.username)
        self.send(Message('scst', script_status), pickling=True)

        # friend demands
        dfrs = DataBase.get_friend_demands(self.username)

        for sender in dfrs:
            
            if sender == '':
                continue
            
            Interaction.send_demand_friend(self.username, sender)

    def _send_connected_friends(self):
        '''Send the status of each friend of client'''
        friends = []

        # get friends
        username_friends = DataBase.get_friends(self.username)

        for username in username_friends:

            friends.append([
                username,
                Interaction.is_user(username)
            ])

        self.send(Message('frs', friends), pickling=True)

    def _send_ship(self):
        '''
        Send the ship grid and ship status
        '''
        # ship grid
        arr = DataBase.get_ship(self.username)
        self.send(Message('sh', arr), pickling=True)

        # ship status
        self.send(Message('shst', DataBase.get_ship_status(self.username)), pickling=True)

    def _send_script(self, script: list):
        '''
        Send the script by little chunk to the client
        '''
        for line in script:
            self.send(Message('scl', line), pickling=True)

    def send_enter_game(self, opp_client, team):
        '''
        Send to client that he's entering in a game.  
        team specify the starting position of the ship.
        '''
        # send script
        script = DataBase.get_script(self.username)
        self._send_script(script)
        self.send(Message('sc', None), pickling=True)

        # send opp ship grid
        arr = DataBase.get_ship(opp_client.username)
        self.send(Message('igsh', arr), pickling=True)

        # send own ship grid
        arr = DataBase.get_ship(self.username)
        self.send(Message('sh', arr), pickling=True)

        # notify in game | opponent username, the position id of the ship
        self.send(Message('ign', [opp_client.username, team]), pickling=True)

    def login(self, content):
        '''
        Log the user in.  
        Content: username, password
        '''
        username, password = content

        # check that the username exists and that the password is correct
        if DataBase.is_user(username):

            if Interaction.is_user(username):
                # can't log in -> already connected
                self.send(Message('rlg',False), pickling=True)
                return

            if DataBase.get_password(username) == password:
                # log in
                self.send(Message('rlg',True), pickling=True)
                self._log_client(username)
                return
        
        # can't log in
        self.send(Message('rlg',False), pickling=True)
    
    def sign_up(self, content):
        '''
        Create a new account.  
        Content: username, password
        '''
        username, password = content

        # try to add the new user
        if DataBase.add_user(username, password):
            # sign up
            self.send(Message('rsg',True), pickling=True)
        
            self._log_client(username)
        else:
            # can't sign up
            self.send(Message('rsg',False), pickling=True)
    
    def general_chat(self, content):
        '''
        Send a message on the general chat.  
        Content: msg
        '''
        Interaction.send_general_chat_msg(self.username, content)

    def private_chat(self, content):
        '''
        Send a message to the other user
        Content: username, msg
        '''
        target, msg = content

        Interaction.send_private_chat_msg(self.username, target, msg)        

    def profil_demand(self, username):
        '''
        Get the stats of a user,  
        send stats to user
        '''
        wins = DataBase.get_wins(username)
        loss = DataBase.get_loss(username)
        ship = DataBase.get_ship(username)
        friends = DataBase.get_friends(username)
        grid = DataBase.get_ship(username)

        if self.username in friends:
            friends.remove(self.username)

        msg = Message('rpd',{
            'username': username,
            'wins': wins,
            'loss': loss,
            'friends': friends,
            'grid': grid
        })

        self.send(msg, pickling=True)

    def demand_friend(self, content):
        '''
        Manage the friend demand
        Content: target username
        '''
        is_error = False

        # check target is not user
        if content == self.username:
            is_error = True

        # check requested user exist
        if not DataBase.is_user(content):
            is_error = True
        
        # check not already friends
        if content in DataBase.get_friends(self.username):
            is_error = True

        if is_error:
            # send error in friend demand
            self.send(Message('rdfr', False), pickling=True)
            return

        DataBase.add_friend_demand(content, self.username)

        # check if requested user is connected
        if Interaction.is_user(content):
            Interaction.send_demand_friend(content, self.username)

        # send friend demand is ok
        self.send(Message('rdfr', True), pickling=True)

    def response_demand_friend(self, content):
        '''
        Manage the response of a friend demand.
        Content: username, response
        '''
        username, response = content

        is_connected = False # if sender is connected

        DataBase.remove_friend_demand(self.username, username)

        if response:
            DataBase.set_as_friends(self.username, username)
            
            # send to new friend that we are connected
            if Interaction.is_user(username):
                is_connected = True
                Interaction.send(username, Message('frs', [[self.username, True]]))

            # send to client if new friend is connected
            self.send(Message('frs', [[username, is_connected]]), pickling=True)
    
    def demand_game(self, content):
        '''
        Manage the game demand
        Content: target username
        '''
        is_error = False

        # check target is not user
        if content == self.username:
            is_error = True

        # check if requested user is connected
        if not Interaction.is_user(content):
            is_error = True

        if is_error:
            # send error in game demand
            self.send(Message('rdg', False), pickling=True)
            return

        Interaction.send_demand_game(content, self.username)

        # send game demand is ok
        self.send(Message('rdg', True), pickling=True)

    def response_demand_game(self, content):
        '''
        Manage the response of a game demand.
        Content: username, response
        '''
        username, response = content

        if response:
            # start a new game
            Interaction.create_game(self.username, username)

    def ship_config(self, arr):
        '''
        Store the new ship config of the client,  
        Store the ship status, send it to the client
        '''
        DataBase.set_ship(self.username, arr)
        DataBase.set_ship_status(self.username, 1)

        self.send(Message('shst', 1), pickling=True)

    def save_script(self, status):
        '''
        Store the script
        '''
        script = self._script_cache
        DataBase.set_script(self.username, script)

        # empty cache
        self._script_cache = []

    def script_analysis(self, status):
        '''
        Analyse the script, look for cheating attempts.  
        Send response to user.
        '''
        script = '\n'.join(self._script_cache)
        self._script_cache = []
        
        fine = True        

        script = script.replace('  ', ' ')

        maliscious_lines = [
            'from API import',
            'API._ships',
            'API as',
            'import game',
            'from game.ship',
            'from game.game'
        ]

        for line in maliscious_lines:
            if script.find(line) != -1:
                fine = False
                break

        self.send(Message('rsca', fine), pickling=True)

    def end_game(self, has_win):
        '''
        Set the user to be out (game finished) of his game in Interaction
        '''
        if has_win:
            result = 'win'
        else:
            result = 'loss'

        Interaction.set_game_result(self.game_tag, self.username, result)

        # reset game values
        self.game_tag = None
        self.opponent = None

    def on_game_init_state(self, content):
        '''
        Send some info to the other user of the game
        '''
        Interaction.send(self.opponent, Message('gis', content))

    def in_game_error(self, content):
        '''
        Send to the other user the number of errors that occured in the script.
        '''
        Interaction.send(self.opponent, Message('ige', content))

    def set_script_status(self, content):
        '''
        Set the status of the user script.
        '''
        DataBase.set_script_status(self.username, content)

        # send status back to user
        self.send(Message('scst', content), pickling=True)

    def set_ship_status(self, content):
        '''
        Set the status of the user ship.
        '''
        DataBase.set_ship_status(self.username, content)

    def set_waiting_game_state(self, content):
        '''
        Set if the user is waiting to enter a game.
        '''
        Interaction.set_user_waiting_game(self.username, content)

    def on_script_line(self, line):
        '''
        Store the line in the script cache
        '''
        self._script_cache.append(line)

    def display_msg(self, msg: Message):
        '''
        Display the Message to the terminal
        in a pretty printing way.
        '''
        display_content = True

        if msg.identifier == 'scl':
            return
        elif type(msg.content) is np.ndarray:
            display_content = False
        
        if display_content:
            self.print('{' + msg.identifier + '} ' + str(msg.content))
        else:
            self.print('{' + msg.identifier + '}')

    def print(self, string, *strings, warning=False):
        '''
        Print a string to the terminal.  
        '''

        # compose string
        for _str in strings:
            string += ' ' + _str

        if self.logged:
            id = self.username
        else:
            id = self.ip

        if warning:
            Console.print(f'[TCP] |{id}| [WARNING] {string}')
        else:
            Console.print(f'[TCP] |{id}| {string}')