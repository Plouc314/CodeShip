import pandas as pd
import numpy as np

class DataBase:

    df = None
    filepath = 'db/data.csv'

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

    @classmethod
    def add_user(cls, username, password):
        '''
        Try to add a new user to the dataframe.  
        Return if the username could be added.
        '''
        if cls.is_username(username):
            return False
        
        cls.df.loc[username,:] = [password]
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