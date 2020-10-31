from lib.tcp import ClientTCP
from tcp.interaction import Interaction
from db.db import DataBase
from spec import Spec

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
            'gc': self.general_chat
        }

    def on_disconnect(self):
        
        # remove from Interaction
        Interaction.clients.remove(self)

        self.print("Disconnected.")

    def _log_client(self, username):
        '''
        Internal method.  
        Set attributes to log in. 
        '''
        self.logged = True
        self.username = username

        self.print("Logged.")

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Call the method linked to the identifier.
        '''
        identifier, content = msg.split(Spec.SEP_MAIN)

        self.identifiers[identifier](content)
    
    def login(self, content):
        '''
        Log the user in.  
        Content: username, password
        '''
        username, password = content.split(Spec.SEP_CONTENT)

        # check that the username exists and that the password is correct
        if DataBase.is_username(username):
            if DataBase.get_password(username) == password:
                # log in
                self._log_client(username)

                msg = f'rlg{Spec.SEP_MAIN}1'
                self.send(msg)
        
        else:
            # can't log in
            msg = f'rlg{Spec.SEP_MAIN}0'
            self.send(msg)
    
    def sign_up(self, content):
        '''
        Create a new account.  
        Content: username, password
        '''
        username, password = content.split(Spec.SEP_CONTENT)

        # try to add the new user
        if DataBase.add_user(username, password):
            # sign up
            self._log_client(username)

            msg = f'rsg{Spec.SEP_MAIN}1'
            self.send(msg)
        
        else:
            # can't sign up
            msg = f'rsg{Spec.SEP_MAIN}0'
            self.send(msg)
    
    def general_chat(self, content):
        '''
        Send a message on the general chat.  
        Content: msg
        '''
        Interaction.send_general_chat_msg(self.username, content)

    def print(self, string):
        '''
        Print a string to the terminal.  
        '''

        if self.logged:
            id = self.username
        else:
            id = self.ip

        print(f'[TCP] |{id}| {string}')