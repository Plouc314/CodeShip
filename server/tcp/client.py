import numpy as np
from lib.tcp import ClientTCP
from tcp.interaction import Interaction
from db.db import DataBase
from spec import Spec

sep_m = Spec.SEP_MAIN
sep_c = Spec.SEP_CONTENT
sep_c2 = Spec.SEP_CONTENT2

class Client(ClientTCP):

    def __init__(self, conn, addr):

        super().__init__(conn, addr)

        self.logged = False
        self.username = None

        # store the identifiers of the comm as key
        # the values are the methods called for each of the identifier
        self.identifiers = {
            'lo': self.on_disconnect, # log out
            'lg': self.login,
            'sg': self.sign_up,
            'gc': self.general_chat,
            'dfr': self.demand_friend,
            'rdfr': self.response_demand_friend,
            'shcf': self.ship_config,
            'sc': self.save_script,
            'sca': self.script_analysis
        }

    def on_disconnect(self, content=None):
        '''
        Executed on disconnection, to have a clean disconnection
        '''
        self.logged = False
        
        if self.username != None:
            Interaction.send_connection_state(self.username, False)

            # remove from Interaction
            Interaction.remove(self.username)

            self.username = None

        self.print("Disconnected.")

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
        self.send(f'sc{sep_m}{script}')

        # friend demands
        dfrs = DataBase.get_friend_demands(self.username)

        for sender in dfrs:
            
            if sender == '':
                continue
            
            Interaction.send_demand_friend(self.username, sender)

    def _send_connected_friends(self):
        '''Send the status of each friend of client'''
        # friends
        msg = f'frs{sep_m}'

        # get friends
        friends = DataBase.get_friends(self.username)

        for friend in friends:

            # look if friend is connected
            if Interaction.is_user(friend):
                is_connected = 1
            else:
                is_connected = 0

            msg += f'{friend}{sep_c2}{is_connected}'

            # add separation
            if not friend == friends[-1]:
                msg += sep_c

        # doesn't send message if user doesn't have friends
        if len(friends) != 0:
            self.send(msg)

    def _send_ship(self):
        '''Send the ship array of client to client'''
        arr = DataBase.get_ship(self.username)
        msg = f'sh{sep_m}{self.username}{sep_c}'

        for x in range(arr.shape[0]):
            for y in range(arr.shape[1]):
                msg += f'{arr[x,y]}{sep_c2}'

        # remove last sep
        msg = msg[:-1]

        self.send(msg)

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Call the method linked to the identifier.
        '''
        identifier, content = msg.split(sep_m)

        self.identifiers[identifier](content)
    
    def login(self, content):
        '''
        Log the user in.  
        Content: username, password
        '''
        username, password = content.split(sep_c)

        # check that the username exists and that the password is correct
        if DataBase.is_user(username):
            if DataBase.get_password(username) == password:
                # log in
                self.send(f'rlg{sep_m}1')

                self._log_client(username)
                return
        
        # can't log in
        self.send(f'rlg{sep_m}0')
    
    def sign_up(self, content):
        '''
        Create a new account.  
        Content: username, password
        '''
        username, password = content.split(sep_c)

        # try to add the new user
        if DataBase.add_user(username, password):
            # sign up
            self.send(f'rsg{sep_m}1')
        
            self._log_client(username)
        else:
            # can't sign up
            self.send(f'rsg{sep_m}0')
    
    def general_chat(self, content):
        '''
        Send a message on the general chat.  
        Content: msg
        '''
        Interaction.send_general_chat_msg(self.username, content)

    def demand_friend(self, content):
        '''
        Manage the friend demand
        Content: target username
        '''
        # check requested user exist
        if not DataBase.is_user(content):
            # send error in friend demand
            self.send(f'rdfr{sep_m}0')
            return
        
        DataBase.add_friend_demand(content, self.username)

        # check if requested user is connected
        if Interaction.is_user(content):
            Interaction.send_demand_friend(content, self.username)

        # send friend demand is ok
        self.send(f'rdfr{sep_m}1')

    def response_demand_friend(self, content):
        '''
        Manage the response of a friend demand.
        Content: username, response
        '''
        username, response = content.split(sep_c)
        response = int(response)
        is_connected = False # if sender is connected

        DataBase.remove_friend_demand(self.username, username)

        if response:
            DataBase.set_as_friends(self.username, username)
            
            # send to new friend that we are connected
            if Interaction.is_user(username):
                is_connected = True
                Interaction.send(username, f'frs{sep_m}{self.username}{sep_c2}1')

            # send to client if new friend is connected
            self.send(f'frs{sep_m}{username}{sep_c2}{int(is_connected)}')
            
    def ship_config(self, content):
        '''
        Store the new ship config of the client
        '''
        arr = content.split(sep_c)

        # compute shape of the ship
        size = int(np.sqrt(len(arr)))

        arr = np.array(arr, dtype=int).reshape((size, size))

        DataBase.set_ship(self.username, arr)

    def save_script(self, content):
        '''
        Store the script
        '''
        DataBase.set_script(self.username, content)

    def script_analysis(self, content):
        '''
        Analyse the script, look for cheating attempts.  
        Send response to user.
        '''
        script = content
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

        self.send(f'rsca{sep_m}{int(fine)}')

    def print(self, string):
        '''
        Print a string to the terminal.  
        '''

        if self.logged:
            id = self.username
        else:
            id = self.ip

        print(f'[TCP] |{id}| {string}')