import socket, threading
from time import time, sleep
from spec import Spec

class ErrorServer:

    @staticmethod
    def call(traceback):
        print('{UDP} [ERROR]', traceback)

class Spec:
    BUFSIZE = 4096
    FORMAT = 'utf-8'
    CONNECT_MSG = "!CONNECT"
    DISCONNECT_MSG = "!DISCONNECT"

class ServerUDP:

    # store all instances -> allow Client object to get ref of server
    instances = []
    # store ip address -> see above
    last_ip = None 

    def __init__(self, port, ip=None):

        # create socket with UDP protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(port, ip)

        self.port = port
        self.ip = ip
        self.running = True

        # dict of the clients, key : ip address
        # send incoming msg to them
        # clients themselves add them to the dict
        self.clients = {}

        ServerUDP.instances.append(self)

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
    
    def run(self):
        '''
        Loop that wait for all messages.  
        Execute on_connection, clients' on_message method.  
        To end execution, set running attribute to False.
        '''

        while self.running:

            # receive msg
            msg, address = self.socket.recvfrom(Spec.BUFSIZE)
            msg = msg.decode(Spec.FORMAT)

            if msg == Spec.CONNECT_MSG:
                self.last_ip = address[0]
                self.on_connection(address)

            else:
                # call transfert msg to client
                ip = address[0]

                if ip in self.clients.keys():
                    client = self.clients[ip]

                    if msg == Spec.DISCONNECT_MSG:
                        client.on_disconnect()
                        # remove client
                        self.clients.pop(ip)
                    else:
                        client.on_message(msg)

                else:
                    ErrorServer.call("Invalid IP address: " + ip)


    @staticmethod
    def on_connection(addr):
        '''
        Function executed on new connection.  
        Has as argument, address of the connection.  
        To be implemented.  
        '''
        raise NotImplementedError("on_connection method must be implemented.")


class ClientUDP:

    server = None

    def __init__(self, addr):
        
        self.ip = addr[0]
        self.port = addr[1]
        self.addr = tuple(addr)

        self.get_server_ref()
    
    def get_server_ref(self):
        '''
        Look for server reference.  
        Add ref of self to the server.  
        '''
        # find server
        for server in ServerUDP.instances:
            if server.last_ip == self.ip:
                self.server = server

        # add own ref
        self.server.clients[self.ip] = self
    
    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    @staticmethod
    def on_disconnect():
        '''
        Disconnect, called when the client has sent a disconnect message.  
        To be implemented.    
        '''
        raise NotImplementedError("on_disconnect method must be implemented.")

    def send(self, msg):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        msg = msg.encode(Spec.FORMAT)

        self.server.socket.sendto(msg, self.addr)
