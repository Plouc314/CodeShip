import socket, pickle
from time import sleep

class ErrorTCP:
    '''
    Basic printer for error.  
    Use the `call` static method.
    '''

    @staticmethod
    def call(traceback, warning=False):
        '''
        Display a message in the terminal.  
        In the format: `"[TCP] [call type] traceback"`
        '''
        if warning:
            call_type = "WARNING"
        else:
            call_type = "ERROR"
        
        print(f"[TCP] [{call_type}] {traceback}")


class Spec:
    HEADER = 64
    FORMAT = 'utf-8'
    CONNECT_MSG = b"!CONNECT"
    DISCONNECT_MSG = b"!DISCONNECT"

class Message:
    def __init__(self, identifier, content):
        self.identifier = identifier
        self.content = content

class ClientTCP:
    '''
    ClientTCP manage the sending and receiving of the messages to a server.

    Arguments:
        - addr : the address, (ip, port)
        - connect : if the client try to connect to the server in the __init__ method.
    
    Methods:
        - run : Loop that wait for messages from the server.
        - connect : Try to connect to the server.
        - disconnect : Disconnect from the server.
        - send : Send a message to the server.
        - on_message : Method executed when receiving a message, to be implemented.
    '''

    def __init__(self, addr, connect=False):

        self.addr = tuple(addr)
        self.ip = addr[0]
        self.port = addr[1]
        self.connected = False

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if connect:
            self.connect()

    def __del__(self):
        # safety to be sure to disconnect properly
        if self.connected:
            self.connected = False
            self.disconnect()

    def connect(self):
        '''
        Try to connect to the server.  
        Return True if the connection succeeds.
        '''
        try:
            self._socket.connect(self.addr)
            self.connected = True
            return True
        except:
            return False

    def run(self):
        '''
        Loop that wait for message from client.  
        Execute on_message method.  
        To end execution, set connected attribute to False.  
        '''

        while self.connected:

            msg = self.receive(decode=False)

            if msg != None:
                self.on_message(msg)
    
    def disconnect(self):
        '''
        Send disconnection message to the server.     
        '''
        if self.connected:
            self.send(Spec.DISCONNECT_MSG.decode())
            self.connected = False

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def send(self, msg, pickling=False):
        '''
        Send the given message to the client.  
        If pickling=True, pickle the message.  
        In case of error: abort operation.  
        '''
        if pickling:
            message = pickle.dumps(msg)
        else:
            message = msg.encode(Spec.FORMAT)
        
        # send header
        length = len(message)
        msg_length = str(length).encode(Spec.FORMAT)
        msg_length += b' ' * (Spec.HEADER - len(msg_length))
        
        try:
            self._socket.send(msg_length)
            self._socket.send(message)
        except:
            ErrorTCP.call("Failure sending message: " + msg)

    def receive(self, decode=True):
        '''
        Wait until receiving a message on own connection.  
        If decode=True, decode the received msg (`decode` string method).  
        Message with header, in case of error: abort operation.
        '''
        msg_length = self._socket.recv(Spec.HEADER).decode(Spec.FORMAT)
        
        if msg_length == None or msg_length == '':
            return

        try:
            msg_length = int(msg_length)
            msg = self._socket.recv(msg_length)
        except:
            ErrorTCP.call("Failure receiving message.")
            return
        
        if decode:
            return msg.decode(Spec.FORMAT)
        else:
            return msg