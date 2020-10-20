import socket, threading
from time import time, sleep
from spec import Spec

class ErrorServer:

    @classmethod
    def call(traceback, id=None, warning=False):
        
        if warning:
            call_type = "WARNING"
        else:
            call_type = "ERROR"

        if id == None:
            call_info = "|TCP|"
        else:
            call_info = f"|TCP {id}|"
        
        print(f"{call_type} {call_info} {traceback}")


class Spec:
    HEADER = 64
    FORMAT = 'utf-8'
    CONNECT_MSG = "!CONNECT"
    DISCONNECT_MSG = "!DISCONNECT"


class ServerTCP:
    '''
    ServerTCP wrap the socket.socket object. It works with the ClientTCP object.  
    
    Arguments:
        - port : port from wich the connections will reach the server.
        - ip : if specified, the ip address that the server will listen to.
    
    Methods: 
        - run : Loop that wait for connections.
        - on_connection : method that is executed for each new connection, must be implemented.
    '''

    def __init__(self, port, ip=None):

        if ip == None:
            self._ip = ''
        else:
            self._ip = ip

        self._port = port
        self._addr = (self._ip, self._port)
        self._running = True

        # create socket with TCP protocol
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind()
        self._socket.listen()

    def bind(self):
        '''
        Bind the server to the given port & potential ip address.  
        In case of error: abort operation.
        '''

        try:
            self._socket.bind(self._addr)
        except:
            ErrorServer.call("Port already used.")
            quit()
        
    def run(self):
        '''
        Loop that wait for connections.  
        Execute on_connection method.  
        To end execution, set running attribute to False.
        '''

        while self._running:

            conn, addr = self._socket.accept()

            print(f'[TCP] Connected: {addr[0]}')

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
    '''
    ClientTCP manage the sending and receiving of the message of a client. It works with the ServerTCP object.  

    Arguments:
        - conn : the Connection object
        - addr : the address, (ip, port)
    
    Methods:
        - run : Loop that wait for messages from the client.
        - send : Send a message to the client.
        - on_message : Method executed when receiving a message, to be implemented.
        - on_disconnect : Method executed when the client disconnect from the server, to be implemented.
    '''

    def __init__(self, conn, addr):
        
        self.conn = conn
        
        self.addr = tuple(addr)
        self.ip = addr[0]
        self.port = addr[1]
        
        self.connected = True
        self.call_id = self.ip # used for error/warning

        # number of msg with blank string received,
        # after 5 of them, close connection with client
        self._blank_threshold = 5
        self._n_blank = 0

    def run(self):
        '''
        Loop that wait for message from client.  
        Execute on_message method.  
        To end execution, set connected attribute to False.  
        '''

        while self.connected:

            msg = self.receive()

            if msg == None: # there was an error in .receive
                continue

            if msg == Spec.DISCONNECT_MSG:
                self._disconnect()
                self.on_disconnect()
                
            else:
                self.on_message(msg)
    
    def _disconnect(self):
        '''
        Internal disconnect method.  
        Close connection and update connected attr
        '''
        self.conn.close()
        self.connected = False

    @staticmethod
    def on_disconnect():
        '''
        Disconnect, called when the client has sent a disconnect message.  
        To be implemented.    
        '''
        raise NotImplementedError("on_disconnect method must be implemented.")

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
        
        try:
            msg_length = self.conn.recv(Spec.HEADER).decode(Spec.FORMAT)
        except:
            ErrorServer.call("Failure receiving header.", self.call_id)
            return
        
        if msg_length == '':
            # safety test -> close connection when client left without disconn msg
            self._n_blank += 1
            if self._n_blank == self._blank_threshold:
                self._disconnect()
                self.on_disconnect()
                ErrorServer.warn("Connection closed.", self.call_id, warning=True)
            return

        try:
            msg_length = int(msg_length)
            msg = self.conn.recv(msg_length).decode(Spec.FORMAT)
            return msg
        except:
            ErrorServer.call("Failure receiving message.", self.call_id)
        
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
            ErrorServer.call("Failure sending message: " + msg, self.call_id)