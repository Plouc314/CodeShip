import numpy as np
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
    # queue used to communicate with the udp server
    queue = None

    clients = {}
    waiting_game = []

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
        Also remove client from udp server.
        '''
        if cls.is_user(username):

            cls.queue.put(['rm', cls.clients[username].ip])

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

    @classmethod
    def set_user_waiting_game(cls, username, state):
        '''
        Set if the user is waiting to enter a game
        '''
        if state:
            if not username in cls.waiting_game:
                cls.waiting_game.append(username)
            
                cls.pair_user()

        else:
            if username in cls.waiting_game:
                cls.waiting_game.remove(username)
    
    @classmethod
    def pair_user(cls):
        '''
        Check if two users a waiting,  
        If yes: pair the two users, active the udp connection
        '''
        # check if enough clients to create a game
        if len(cls.waiting_game) < 2:
            return
        
        # remove clients from waiting list
        user1 = cls.waiting_game[-1]
        user2 = cls.waiting_game[-2]

        cls.waiting_game = cls.waiting_game[:-2]

        # connect client on udp server
        addr1 = cls.clients[user1].addr
        addr2 = cls.clients[user2].addr

        cls.queue.put(['conn', addr1, addr2])

        # notify clients on local

        # get random pos id
        id1 = bool(np.random.randint(0,2))
        id2 = not id1

        cls.clients[user1].send_enter_game(cls.clients[user2], id1)
        cls.clients[user2].send_enter_game(cls.clients[user1], id2)

