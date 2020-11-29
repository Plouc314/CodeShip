import pandas as pd
import numpy as np

class DataBase:

    df = None
    filepath = 'db/data/data.csv'

    @classmethod
    def load(cls):
        cls.df = pd.read_csv(cls.filepath, index_col='username')
        cls.df.loc[:,['password','friend','dfr']] = cls.df.loc[:,['password','friend','dfr']].astype(str)

        cls.df['friend'].replace('nan', '', inplace=True)
        cls.df['dfr'].replace('nan', '', inplace=True)

        cls.df['friend'] = cls.df['friend'].str.split('|')
        cls.df['dfr'] = cls.df['dfr'].str.split('|')
        
        def mapper(x):
            if '' in x:
                x.remove('')
            return x

        cls.df['friend'].apply(mapper)
        cls.df['dfr'].apply(mapper)

        cls.load_ships()
        cls.load_scripts()

    @classmethod
    def load_ships(cls):
        cls.ships = {}

        for user in cls.df.index:
            # load ship of every user
            arr = np.load(f"db/data/ships/{user}.npy")

            cls.ships[user] = arr

        cls.grid_shape = cls.ships[cls.df.index[0]].shape

    @classmethod
    def load_scripts(cls):
        cls.scripts = {}

        for user in cls.df.index:
            # load script of every user
            with open(f"db/data/scripts/{user}.txt", 'r') as file:
                script = file.read()
            
            cls.scripts[user] = script

    @classmethod
    def store(cls):
        
        def mapper(x):
            if len(x) == 1:
                return x[0]
            else:
                return '|'.join(x)

        cls.df['friend'] = cls.df['friend'].apply(mapper)
        cls.df['dfr'] = cls.df['dfr'].apply(mapper)

        cls.df.to_csv('db/data.csv')

        cls.store_ships()
        cls.store_scripts()

    @classmethod
    def store_ships(cls):
        for user, arr in cls.ships.items():
            np.save(f"db/data/ships/{user}.npy", arr)

    @classmethod
    def store_scripts(cls):
        for user, script in cls.scripts.items():
            with open(f"db/data/scripts/{user}.txt", 'w') as file:
                file.write(script)

    @classmethod
    def get_ship(cls, username):
        '''
        Return the ship array of a user
        '''
        return cls.ships[username]

    @classmethod
    def set_ship(cls, username, grid):
        '''
        Set the ship grid of a user
        '''
        cls.ships[username] = grid

    @classmethod
    def set_script(cls, username, script):
        '''
        Set the script of a user
        '''
        cls.scripts[username] = script

    @classmethod
    def get_script(cls, username):
        '''
        Return the script of a user
        '''
        return cls.scripts[username]

    @classmethod
    def set_script_status(cls, username, script_status):
        '''
        Set the script status of a user
        '''
        cls.df.loc[username, 'scriptstatus'] = int(script_status)

    @classmethod
    def get_script_status(cls, username):
        '''
        Return the script status of a user
        '''
        return cls.df.loc[username, 'scriptstatus']

    @classmethod
    def set_ship_status(cls, username, ship_status):
        '''
        Set the ship status of a user
        '''
        cls.df.loc[username, 'shipstatus'] = int(ship_status)

    @classmethod
    def get_ship_status(cls, username):
        '''
        Return the ship status of a user
        '''
        return cls.df.loc[username, 'shipstatus']

    @classmethod
    def add_user(cls, username, password):
        '''
        Try to add a new user to the dataframe.  
        Return if the username could be added.
        '''
        if cls.is_username(username):
            return False
        
        cls.df.loc[username,:] = [password,[],[],0]
        
        cls.ships[username] = np.zeros(cls.grid_shape)
        cls.scripts[username] = ''

        return True
    
    @classmethod
    def is_user(cls, username):
        '''
        Return if the given username exist in the database.
        '''
        return username in cls.df.index.values

    @classmethod
    def get_password(cls, username):
        '''
        Return the password of the given username.
        '''
        return cls.df.loc[username,'password']
    
    @classmethod
    def get_friends(cls, username):
        '''
        Return the friends of the given username.
        '''
        return cls.df.loc[username,'friend']
    
    @classmethod
    def set_as_friends(cls, user1, user2):
        '''
        Set two users to be friends.
        '''
        cls.df.loc[user1, 'friend'].append(user2)
        cls.df.loc[user2, 'friend'].append(user1)

    @classmethod
    def get_friend_demands(cls, username):
        '''
        Return the friend demands of the given username.
        '''
        return cls.df.loc[username,'dfr']

    @classmethod
    def add_friend_demand(cls, target, sender):
        '''
        Store the friend demand, for in the case the user isn't connected yet.
        '''
        if not sender in cls.df.loc[target, 'dfr']:
            cls.df.loc[target, 'dfr'].append(sender)
    
    @classmethod
    def remove_friend_demand(cls, target, sender):
        '''
        Remove a friend demand.
        '''
        if sender in cls.df.loc[target, 'dfr']:
            cls.df.loc[target, 'dfr'].remove(sender)