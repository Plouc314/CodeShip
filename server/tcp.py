import socket, threading
from time import time, sleep
from spec import Spec

class ErrorServer:

    @staticmethod
    def call(traceback):
        print('{TCP} [ERROR]', traceback)

class Spec:
    HEADER = 64
    FORMAT = 'utf-8'
    CONNECT_MSG = "!CONNECT"
    DISCONNECT_MSG = "!DISCONNECT"


class ServerTCP:

    def __init__(self, port, ip=None):

        self.port = port
        self.ip = ip
        self.addr = (ip, port)
        self.running = True

        # create socket with TCP protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind()
        self.socket.listen()

    def bind(self):
        '''
        Bind the server to the given port & potential ip address.  
        In case of error: abort operation.
        '''

        try:
            self.socket.bind(self.addr)
        except:
            ErrorServer.call("Port already used.")
            quit()
        
    def run(self):
        '''
        Loop that wait for connections.  
        Execute on_connection method.  
        To end execution, set running attribute to False.
        '''

        while self.running:

            conn, addr = self.socket.accept()
            
            print('{TCP} [NEW CONNECTION]', addr[0])

            self.on_connection(conn, addr)

    @staticmethod
    def on_connection(conn, addr):
        '''
        Function executed on new connection.  
        Has as arguments, conn & addr of the connection.  
        To be implemented.  
        '''
        raise NotImplementedError("on_connection method must be implemented.")


class ClientTCP:

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.connected = True

    def run(self):
        '''
        Loop that wait for message from client.  
        Execute on_message method.  
        To end execution, set connected attribute to False.  
        '''

        while self.connected:

            msg = self.receive_msg()

            if msg == Spec.DISCONNECT_MSG:
                self.disconnect()
            
            else:
                self.on_message(msg)
    
    def disconnect(self):
        '''
        Disconnect, called when the client has sent a disconnect message.  
        '''
        self.connected = False

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def receive(self):
        '''
        Wait until receiving a message on own connection.  
        Message with header, in case of error: abort operation.
        '''
        msg_length = self.conn.recv(Spec.HEADER).decode(Spec.FORMAT)
        
        if msg_length == None:
            return

        try:
            msg_length = int(msg_length)
            msg = self.conn.recv(msg_length).decode(Spec.FORMAT)
            return msg
        except:
            ErrorServer.call("Failure receiving message.")
        
    def send(self, msg):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        message = msg.encode(Spec.FORMAT)
        
        length = len(message)
        msg_length = str(length).encode(Spec.FORMAT)
        msg_length += b' ' * (Spec.HEADER - len(msg_length))
        
        try:
            self.conn.send(msg_length)
            self.conn.send(message)
        except:
            ErrorServer.call("Failure sending message: " + msg)