import pandas as pd


class DataBase:

    df = None
    filepath = 'db/data.csv'

    @classmethod
    def load(cls):
        cls.df = pd.read_csv(cls.filepath, index_col='username')
        cls.df['password'] = cls.df['password'].astype(str)

    @classmethod
    def add_user(cls, username, password):
        '''
        Add a new user to the dataframe, if the username is already taken return false.  
        '''
        if username in cls.df.index.values:
            return False
        
        cls.df.loc[username,:] = [password]
        return True
    
    @classmethod
    def get_password(cls, username):
        '''
        Return the password of the given username.
        '''
        return cls.df.loc[username,'password']