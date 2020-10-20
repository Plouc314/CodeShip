import socket
from time import sleep

class ErrorClient:

    @classmethod
    def call(traceback, warning=False):
        
        if warning:
            call_type = "WARNING"
        else:
            call_type = "ERROR"
        
        print(f"{call_type} |TCP| {traceback}")


class Spec:
    HEADER = 64
    FORMAT = 'utf-8'
    CONNECT_MSG = "!CONNECT"
    DISCONNECT_MSG = "!DISCONNECT"


class ClientTCP:

    def __init__(self, addr):

        self.addr = tuple(addr)
        self.ip = addr[0]
        self.port = addr[1]
        self.connected = True

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(self.addr)

    def run(self):
        '''
        Loop that wait for message from client.  
        Execute on_message method.  
        To end execution, set connected attribute to False.  
        '''

        while self.connected:

            msg = self.receive_msg()

            self.on_message(msg)
    
    def disconnect(self):
        '''
        Send disconnection message to the server.     
        '''
        self.send(Spec.DISCONNECT_MSG)
        self.connected = False

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def send(self, msg):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        # send header
        length = len(msg)

        msg = msg.encode(Spec.FORMAT)

        msg_length = str(length).encode(Spec.FORMAT)
        msg_length += b' ' * (Spec.HEADER - len(msg_length))
        
        try:
            self._socket.send(msg_length)

            sleep(.1)

            self._socket.send(msg)
        except:
            ErrorClient.call("Failure sending message: " + msg)
    
    def receive(self):
        '''
        Wait until receiving a message on own connection.  
        Message with header, in case of error: abort operation.
        '''
        msg_length = self._socket.recv(Spec.HEADER).decode(Spec.FORMAT)
        
        if msg_length == None:
            return

        try:
            msg_length = int(msg_length)
            msg = self._socket.recv(msg_length).decode(Spec.FORMAT)
            return msg
        except:
            ErrorClient.call("Failure receiving message.")