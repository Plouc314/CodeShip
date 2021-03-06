import numpy as np
from lib.tcp import Message
from db.db import DataBase
from spec import Spec

class Interaction:
    '''
    Static object.  

    Manage the interaction between the clients.
    '''
    # queue used to communicate with the udp server
    queue = None

    clients = {}
    waiting_game = []

    # for each game: store a dict with {username: status}
    # by default status=None, then it can equal either 'win' or 'loss'
    games = {}


    @classmethod
    def send(cls, username, msg: Message):
        '''
        Send a message to one of the connected users
        '''
        cls.clients[username].send(msg, pickling=True)

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
    def set_game_result(cls, tag, username, result):
        '''
        Set the result of one of the user in a game.  
        Check if all users of the games have set a result -> end game 

        `int` tag: the unique tag of the game (stored in `.game_tag`)  
        `str` result: either `"win"` or `"loss"`
        '''
        game = cls.games[tag]
        game[username] = result

        # check if both users have finished the game
        if all(game.values()):
            cls.end_game(tag)

    @classmethod
    def connect_udp(cls, address):
        '''
        Add a client on the udp socket
        '''
        cls.queue.put(['conn', address])

    @classmethod
    def end_game(cls, tag):
        '''
        End a game, stop udp clients.  
        '''
        user1, user2 = cls.games[tag].keys()

        # update DataBase
        if cls.games[tag][user1] == 'win':
            DataBase.increment_wins(user1)
        else:
            DataBase.increment_loss(user1)

        if cls.games[tag][user2] == 'win':
            DataBase.increment_wins(user2)
        else:
            DataBase.increment_loss(user2)

        # update udp clients
        ip1 = cls.clients[user1].ip
        ip2 = cls.clients[user2].ip

        cls.queue.put(['unlink', ip1, ip2])

        cls.games.pop(tag)

    @classmethod
    def send_connection_state(cls, username, state):
        '''
        Send to every friend of user his state: if he's connected.
        '''
        # get friends
        friends = DataBase.get_friends(username)

        for friend in friends:
            if cls.is_user(friend):
                cls.send(friend, Message('frs', [[username, state]]))

    @classmethod
    def send_general_chat_msg(cls, username, msg):
        '''
        Send a message to all connected clients on the general chat.
        '''

        for client in cls.clients.values():

            if client.username == username:
                continue
        
            # send message
            client.send(Message('gc', [username, msg]), pickling=True)

    @classmethod
    def send_private_chat_msg(cls, sender, target, msg):
        '''
        Send a message to the user if connected,  
        else abort msg.
        '''
        if cls.is_user(target):
            cls.clients[target].send(Message('pc', [sender, msg]), pickling=True)

    @classmethod
    def send_demand_friend(cls, target, sender):
        '''
        Send the friend demand to the requested user.
        '''
        cls.clients[target].send(Message('dfr', sender), pickling=True)

    @classmethod
    def send_demand_game(cls, target, sender):
        '''
        Send the game demand to the requested user.
        '''
        cls.clients[target].send(Message('dg', sender), pickling=True)

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

        cls.create_game(user1, user2)

    @classmethod
    def create_game(cls, user1, user2):
        '''
        Start a game, setup the udp socket, 
        send start of game to client.
        '''
        # store game
        tag = id(user1)
        cls.games[tag] = {
            user1: None,
            user2: None
        }

        cls.clients[user1].game_tag = tag
        cls.clients[user2].game_tag = tag

        cls.clients[user1].opponent = user2
        cls.clients[user2].opponent = user1

        # link client on udp server
        ip1 = cls.clients[user1].ip
        ip2 = cls.clients[user2].ip

        cls.queue.put(['link', ip1, ip2])

        # notify clients on local

        # get random team
        team1 = np.random.randint(1,3)
        team2 = -team1 + 3

        cls.clients[user1].send_enter_game(cls.clients[user2], team1)
        cls.clients[user2].send_enter_game(cls.clients[user1], team2)