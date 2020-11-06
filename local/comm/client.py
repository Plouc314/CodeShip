import threading
from lib.tcp import ClientTCP
from spec import Spec

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class Client(ClientTCP):

    def __init__(self, addr, connect=False):

        super().__init__(addr, connect=connect)
    
        # store the identifiers of the comm as key
        # the values are the msg send by the server
        self.in_data = {
            'rlg' : None, # response login
            'rsg' : None, # response sign up
            'frs' : None, # friends connected
            'rdfr': None, # response on friend demand
            'dfr' :   [], # friend demands (from other users) 
            'gc'  :   [], # message on general chat
        }

        # store "empty" datatype of each container -> reset automaticly
        self.default_in_data = self.in_data.copy()

        # store the identifiers of the comm as key
        # for each key, a function will process the incoming data
        self.processes = {
            'rlg' : lambda x: int(x),
            'rsg' : lambda x: int(x),
            'frs' : self.on_friends,
            'rdfr': lambda x: int(x),
            'dfr' : lambda x: x,
            'gc'  : self.on_general_chat
        }

    def connect(self):
        '''
        Try to connect to the server.  
        Also launch the run loop.  
        Return True if the connection succeeds.
        '''
        is_connected = super().connect()

        if is_connected:
            # launch run loop
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

        return is_connected

    def on_message(self, msg):
        '''
        Split the identifier and content of the message.  
        Store the content in the designated container.
        '''
        print('[SERVER]',msg)
        identifier, content = msg.split(sep_m)

        content = self.processes[identifier](content)

        container = self.in_data[identifier]

        if type(container) == list:
            container.append(content)
        else:
            self.in_data[identifier] = content

    def get_data(self, identifier):
        '''
        To use as a context manager.  
        Return the specified data container(s) (`str` or `list`),   
        will free the container(s) after exit of context.
        '''
        return ContextManager(self, identifier)

    def on_general_chat(self, content):
        '''Return chat msg in format: `[username, message]`'''
        return content.split(sep_c)

    def on_friends(self, content):
        '''
        Return friends in format: `list` `[username, is_connected]`
        '''
        content = content.split(sep_c)
        content = [data.split(sep_c2) for data in content]
        return [[username, int(conn)] for username, conn in content]

    def send_login(self, username, password):
        '''
        Send the login information to the server.  
        ID : lg
        '''
        msg = f'lg{sep_m}{username}{sep_c}{password}'

        self.send(msg)
    
    def send_sign_up(self, username, password):
        '''
        Send the sign up information to the server.  
        ID : sg
        '''
        msg = f'sg{sep_m}{username}{sep_c}{password}'

        self.send(msg)

    def send_general_chat_msg(self, message):
        '''
        Send a message on the general chat.
        ID : gc
        '''
        msg = f'gc{sep_m}{message}'

        self.send(msg)

    def send_demand_friend(self, username):
        '''
        Send a friend demand.
        ID: dfr
        '''
        msg = f'dfr{sep_m}{username}'

        self.send(msg)

    def send_response_dfr(self, username, response):
        '''
        Send if accepted or not a friend demand.
        ID: rdfr
        '''
        self.send(f'rdfr{sep_m}{username}{sep_c}{int(response)}')

class ContextManager:
    '''
    Context manager used to get `in_data` content and free it after use.
    '''

    def __init__(self, client, identifier):
        self.client = client

        # pass identifiers to list
        if type(identifier) != list:
            self.id = [identifier]
        else:
            self.id = identifier
    
    def __enter__(self):
        data = [self.client.in_data[id] for id in self.id]
        
        if len(data) == 1:
            return data[0]
        else:
            return data
    
    def __exit__(self, type, value, tb):
        '''Free every containers'''
        
        for id in self.id:
            # free the container
            self.client.in_data[id] = self.client.default_in_data[id]