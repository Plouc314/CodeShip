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
        self.opponent = None # current opponent username

        # unique tag to identify the game in Interaction
        self.game_tag = None

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
        
        if self.username != None:
            Interaction.send_connection_state(self.username, False)

            # remove from Interaction
            Interaction.remove(self.username)

            self.username = None

        self.print("Disconnected.")

    def connect_udp(self, content):
        '''
        Set udp client in udp socket
        '''
        address = (self.ip, int(content))
        Interaction.connect_udp(address)

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

        # script status
        script_status = DataBase.get_script_status(self.username)
        self.send(f'scst{sep_m}{script_status}')

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

    def format_ship_grid(self, username=None):
        '''
        Return the ship grid formated as a string,  
        if not username is given, send client's ship,  
        separated by `SEP_CONTENT2`.
        '''
        if username == None:
            username = self.username

        arr = DataBase.get_ship(username)
        string = ''

        for x in range(arr.shape[0]):
            for y in range(arr.shape[1]):
                string += f'{arr[x,y]}{sep_c2}'

        # remove last sep
        string = string[:-1]

        return string

    def _send_ship(self):
        '''
        Send the ship grid and ship status
        '''

        # ship grid
        msg = f'sh{sep_m}'
        msg += self.format_ship_grid()

        self.send(msg)

        # ship status
        status = DataBase.get_ship_status(self.username)
        self.send(f'shst{sep_m}{status}')

    def send_enter_game(self, opp_client, pos_id):
        '''
        Send to client that he's entering in a game.  
        pos_id specify the starting position of the ship.
        '''
        # send script
        script = DataBase.get_script(self.username)
        self.send(f'sc{sep_m}{script}')

        # send opp ship grid
        self.send(f'igsh{sep_m}{opp_client.format_ship_grid()}')

        # send own ship grid
        self.send(f'sh{sep_m}{self.format_ship_grid()}')

        # notify in game | opponent username, the position id of the ship
        self.send(f'ign{sep_m}{opp_client.username}{sep_c}{int(pos_id)}')

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Call the method linked to the identifier.
        '''
        try:
            identifier, content = msg.split(sep_m)
        except:
            self.print("Error occured in splitting opperation.", warning=True)

        try:
            self.identifiers[identifier](content)
        except:
            self.print(f"Error occured in identifier attribution: {identifier}", warning=True)

        if identifier in ["sc","sca"]:
            return
            
        self.print(msg)

    def login(self, content):
        '''
        Log the user in.  
        Content: username, password
        '''
        username, password = content.split(sep_c)

        # check that the username exists and that the password is correct
        if DataBase.is_user(username):

            if Interaction.is_user(username):
                # can't log in -> already connected
                self.send(f'rlg{sep_m}0')
                return

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

    def private_chat(self, content):
        '''
        Send a message to the other user
        Content: username, msg
        '''
        target, msg = content.split(sep_c)

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

        # add stats
        msg = f'rpd{sep_m}{username}{sep_c}{wins}{sep_c}{loss}{sep_c}'
        
        # add friends
        for friend in friends:
            if friend != self.username:
                msg += friend + sep_c2
        
        if msg[-1] == sep_c2:
            msg = msg[:-1]
        msg += sep_c

        # add ship's grid
        msg += self.format_ship_grid(username=username)

        self.send(msg)

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
            # send error in friend demand
            self.send(f'rdg{sep_m}0')
            return

        Interaction.send_demand_game(content, self.username)

        # send friend demand is ok
        self.send(f'rdg{sep_m}1')

    def response_demand_game(self, content):
        '''
        Manage the response of a game demand.
        Content: username, response
        '''
        username, response = content.split(sep_c)
        response = int(response)

        if response:
            # start a new game
            Interaction.create_game(self.username, username)

    def ship_config(self, content):
        '''
        Store the new ship config of the client,  
        Store the ship status, send it to the client
        '''
        arr = content.split(sep_c)

        # compute shape of the ship
        size = int(np.sqrt(len(arr)))

        arr = np.array(arr, dtype=int).reshape((size, size))

        DataBase.set_ship(self.username, arr)
        DataBase.set_ship_status(self.username, 1)

        self.send(f'shst{sep_m}1')

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

    def end_game(self, content):
        '''
        Set the user to be out (game finished) of his game in Interaction
        '''
        if int(content):
            result = 'win'
        else:
            result = 'loss'

        Interaction.set_game_result(self.game_tag, self.username, result)

    def on_game_init_state(self, content):
        '''
        Send some info to the other user of the game
        '''
        Interaction.send(self.opponent, f'gis{sep_m}{content}')

    def in_game_error(self, content):
        '''
        Send to the other user the number of errors that occured in the script.
        '''
        Interaction.send(self.opponent, f'ige{sep_m}{content}')

    def set_script_status(self, content):
        '''
        Set the status of the user script.
        '''
        DataBase.set_script_status(self.username, int(content))

        # send status back to user
        self.send(f'scst{sep_m}{content}')

    def set_ship_status(self, content):
        '''
        Set the status of the user ship.
        '''
        DataBase.set_ship_status(self.username, int(content))

    def set_waiting_game_state(self, content):
        '''
        Set if the user is waiting to enter a game.
        '''
        Interaction.set_user_waiting_game(self.username, int(content))

    def print(self, string, warning=False):
        '''
        Print a string to the terminal.  
        '''

        if self.logged:
            id = self.username
        else:
            id = self.ip

        if warning:
            warn = '[WARNING] '
        else:
            warn = ''

        print(f'[TCP] {warn}|{id}| {string}')