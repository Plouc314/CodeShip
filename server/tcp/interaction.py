from db.db import DataBase
from spec import Spec

sep_m = Spec.SEP_MAIN
sep_c = Spec.SEP_CONTENT
sep_c2 = Spec.SEP_CONTENT2

class Interaction:
    '''
    Static object.  

    Manage the interaction between the clients.
    '''

    clients = {}

    @classmethod
    def send(cls, username, msg):
        '''
        Send a message to one of the connected users
        '''
        cls.clients[username].send(msg)

    @classmethod
    def remove(cls, username):
        '''
        Remove a client from the interaction.
        '''
        if cls.is_user(username):
            cls.clients.pop(username)

    @classmethod
    def is_user(cls, username):
        '''
        Return if the specified user is connected.
        '''
        return username in cls.clients.keys()

    @classmethod
    def send_connection_state(cls, username, state):
        '''
        Send to every friend of user his state: if he's connected.
        '''
        # get friends
        friends = DataBase.get_friends(username)

        for friend in friends:
            if cls.is_user(friend):
                cls.send(friend, f'frs{sep_m}{username}{sep_c2}{int(state)}')

    @classmethod
    def send_general_chat_msg(cls, username, msg):
        '''
        Send a message to all connected clients on the general chat.
        '''

        for client in cls.clients.values():

            if client.username == username:
                continue
        
            # send message
            msg = f'gc{sep_m}{username}{sep_c}{msg}'
            client.send(msg)

    @classmethod
    def send_demand_friend(cls, target, sender):
        '''
        Send the friend demand to the requested user.
        '''
        cls.clients[target].send(f'dfr{sep_m}{sender}')
