import socket, threading
from time import time, sleep
from spec import Spec

class ErrorServer:

    @staticmethod
    def call(traceback, warning=False):
        
        if warning:
            call_type = '[WARNING]'
        else:
            call_type = '[ERROR]'
        
        print('[UDP]', call_type, traceback)

class Spec:
    BUFSIZE = 4096

class ServerUDP:

    def __init__(self, port, ip=None):

        # create socket with UDP protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(port, ip)

        self.port = port
        self.ip = ip
        self.running = True

        # list all unknown ip
        self._unknown_ips = []

        # dict of the clients, key : ip address
        self._clients = {}

    def bind(self, port, ip=None):
        '''
        Bind the server to the given port & potential ip address.  
        In case of error: abort operation.
        '''

        if ip == None:
            ip = ''

        addr = (ip, port)

        try:
            self.socket.bind(addr)
        except:
            ErrorServer.call("Port already used.")
            quit()
    
    def add_client(self, client):
        '''
        Add a client to the server.  
        '''
        client.server = self
        self._clients[client.ip] = client

        # check if client in unknown ips -> remove it
        if client.ip in self._unknown_ips:
            self._unknown_ips.remove(client.ip)

    def get_client(self, ip):
        '''
        Return the client with the specified ip address.  
        If no client found: return None
        '''
        if ip in self._clients.keys():
            return self._clients[ip]
        
        return None

    def remove_client(self, ip):
        '''
        Remove the client with the specified ip.
        '''
        if ip in self._clients.keys():
            self._clients.pop(ip)

    def run(self):
        '''
        Loop that wait for all messages.  
        Execute on_connection, clients' on_message method.  
        To end execution, set running attribute to False.
        '''

        while self.running:

            # receive msg
            msg, address = self.socket.recvfrom(Spec.BUFSIZE)

            ip = address[0]
            
            if ip in self._clients.keys():
                client = self._clients[ip]
                client.on_message(msg)

            else:
                if not ip in self._unknown_ips:
                    self._unknown_ips.append(ip)
                    ErrorServer.call("Unknown IP address: " + ip, warning=True)


class ClientUDP:

    server = None

    def __init__(self, addr):
        
        self.ip = addr[0]
        self.port = addr[1]
        self.addr = tuple(addr)

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def send(self, msg: bytes):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        msg += b' ' * (Spec.BUFSIZE - len(msg))

        self.server.socket.sendto(msg, self.addr)
