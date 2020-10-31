import threading
from lib.tcp import ClientTCP
from spec import Spec

sep_m, sep_c = Spec.SEP_MAIN, Spec.SEP_CONTENT

class Client(ClientTCP):

    def __init__(self, addr, connect=False):

        super().__init__(addr, connect=connect)
    
        # store the identifiers of the comm as key
        # the values are the msg send by the server
        self.in_data = {
            'rlg': None, # response login
            'rsg': None, # response sign up
            'gc': [] # message on general chat
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
        Call the method linked to the identifier.
        '''
        print('[SERVER]',msg)
        identifier, content = msg.split(Spec.SEP_MAIN)

        # try to pass the content to number
        try:
            content = int(content)
        except:
            pass

        container = self.in_data[identifier]

        if type(container) == list:
            container.append(content)
        else:
            self.in_data[identifier] = content

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