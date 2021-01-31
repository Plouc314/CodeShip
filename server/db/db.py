import numpy as np
import json, os
from spec import Spec

class DataBase:

    usernames: list
    data: dict

    @classmethod
    def load(cls):
        '''
        Load data of users.
        '''
        # load usernames
        with open(os.path.join('db','data','users.json'), 'r') as file:
            data = json.load(file)
        
        cls.usernames = data['usernames']
        cls.data = {} # key: username

        # load user's data
        for username in cls.usernames:

            with open(os.path.join('db','data','users',f'{username}.json'), 'r') as file:
                cls.data[username] = json.load(file)

            # convert ship list to array
            cls.data[username]['ship'] = np.array(cls.data[username]['ship'], int)

    @classmethod
    def store(cls):
        '''
        Store the data
        '''
        # store usernames
        with open(os.path.join('db','data','users.json'), 'w') as file:
            json.dump({"usernames": cls.usernames}, file, indent=4)

        # load user's data
        for username in cls.usernames:

            # convert numpy array to a list -> json can't handeln np.ndarray
            cls.data[username]['ship'] = cls.data[username]['ship'].tolist()

            with open(os.path.join('db','data','users',f'{username}.json'), 'w') as file:
                json.dump(cls.data[username], file, indent=4)

    @classmethod
    def is_user(cls, username):
        '''
        Return if the given user exist in the database.
        '''
        return username in cls.usernames

    @classmethod
    def add_user(cls, username, password):
        '''
        Try to add a new user to the dataframe.  
        Return if the username could be added.
        '''
        if cls.is_user(username):
            return False
        
        cls.usernames.append(username)

        cls.data[username] = {
            "password": password,
            "friends": [],
            "dfr": [],
            "script status": 0,
            "ship status": 0,
            "wins": 0,
            "loss": 0,
            "ship": np.zeros(Spec.SHIP_GRID_SHAPE, dtype=int),
            "script": ""
        }

    @classmethod
    def get_ship(cls, username):
        '''
        Return the ship array of a user
        '''
        return cls.data[username]['ship']

    @classmethod
    def set_ship(cls, username, grid):
        '''
        Set the ship grid of a user
        '''
        cls.data[username]['ship'] = grid

    @classmethod
    def set_script(cls, username, script):
        '''
        Set the script of a user
        '''
        cls.data[username]['script'] = script

    @classmethod
    def get_script(cls, username):
        '''
        Return the script of a user
        '''
        return cls.data[username]['script']

    @classmethod
    def set_script_status(cls, username, script_status):
        '''
        Set the script status of a user
        '''
        cls.data[username]['script status'] = int(script_status)

    @classmethod
    def get_script_status(cls, username):
        '''
        Return the script status of a user
        '''
        return cls.data[username]['script status']

    @classmethod
    def set_ship_status(cls, username, ship_status):
        '''
        Set the ship status of a user
        '''
        cls.data[username]['ship status'] = int(ship_status)

    @classmethod
    def get_ship_status(cls, username):
        '''
        Return the ship status of a user
        '''
        return cls.data[username]['ship status']

    @classmethod
    def get_password(cls, username):
        '''
        Return the password of the given username.
        '''
        return cls.data[username]['password']
    
    @classmethod
    def get_friends(cls, username):
        '''
        Return the friends of the given username.
        '''
        return cls.data[username]['friends']
    
    @classmethod
    def set_as_friends(cls, user1, user2):
        '''
        Set two users to be friends.
        '''
        cls.data[user1]['friends'].append(user2)
        cls.data[user2]['friends'].append(user1)

    @classmethod
    def get_friend_demands(cls, username):
        '''
        Return the friend demands of the given username.
        '''
        return cls.data[username]['dfr']

    @classmethod
    def add_friend_demand(cls, target, sender):
        '''
        Store the friend demand, for in the case the user isn't connected yet.
        '''
        if not sender in cls.data[target]['dfr']:
            cls.data[target]['dfr'].append(sender)
    
    @classmethod
    def remove_friend_demand(cls, target, sender):
        '''
        Remove a friend demand.
        '''
        if sender in cls.data[target]['dfr']:
            cls.data[target]['dfr'].remove(sender)
    
    @classmethod
    def set_wins(cls, username, wins):
        '''
        Set the wins of a user
        '''
        cls.data[username]['wins'] = int(wins)

    @classmethod
    def get_wins(cls, username):
        '''
        Return the wins of a user
        '''
        return cls.data[username]['wins']
    
    @classmethod
    def increment_wins(cls, username, step=1):
        '''
        Increment by `step` the number of wins of the user.
        '''
        cls.data[username]['wins'] += step

    @classmethod
    def set_loss(cls, username, loss):
        '''
        Set the loss of a user
        '''
        cls.data[username]['loss'] = int(loss)

    @classmethod
    def get_loss(cls, username):
        '''
        Return the loss of a user
        '''
        return cls.data[username]['loss']
    
    @classmethod
    def increment_loss(cls, username, step=1):
        '''
        Increment by `step` the number of loss of the user.
        '''
        cls.data[username]['loss'] += step
