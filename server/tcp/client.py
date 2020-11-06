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
            'lg': self.login,
            'sg': self.sign_up,
            'gc': self.general_chat,
            'dfr': self.demand_friend,
            'rdfr': self.response_demand_friend
        }

    def on_disconnect(self):
        '''
        Executed on disconnection, to have a clean disconnection
        '''

        Interaction.send_connection_state(self.username, False)

        # remove from Interaction
        Interaction.remove(self.username)

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
        # friends
        msg = f'frs{sep_m}'

        # get friends
        friends = DataBase.get_friends(self.username)

        # doesn't send message if user doesn't have friends
        if len(friends) == 0:
            return

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

        self.send(msg)

        # friend demands
        dfrs = DataBase.get_friend_demands(self.username)

        for sender in dfrs:
            
            if sender == '':
                continue
            
            Interaction.send_demand_friend(self.username, sender)

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
        else:
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

        DataBase.remove_friend_demand(self.username, username)

        if response:
            DataBase.set_as_friends(self.username, username)
            
            # send to new friend that we are connected
            if Interaction.is_user(username):
                Interaction.send(username, f'frs{sep_m}{self.username}{sep_c2}1')

    def print(self, string):
        '''
        Print a string to the terminal.  
        '''

        if self.logged:
            id = self.username
        else:
            id = self.ip

        print(f'[TCP] |{id}| {string}')