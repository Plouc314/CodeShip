import pandas as pd


class DataBase:

    df = None
    filepath = 'db/data.csv'

    @classmethod
    def load(cls):
        cls.df = pd.read_csv(cls.filepath, index_col='username')
        cls.df.loc[:,['password','friend','dfr']] = cls.df.loc[:,['password','friend','dfr']].astype(str)

        cls.df['friend'] = cls.df['friend'].str.split('|')
        cls.df['dfr'] = cls.df['dfr'].str.split('|')
        
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
    def is_username(cls, username):
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