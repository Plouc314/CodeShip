import socket

class ErrorClient:

    @staticmethod
    def call(traceback):
        print('{TCP} [ERROR]', traceback)


class Spec:
    BUFSIZE = 4096
    FORMAT = 'utf-8'
    CONNECT_MSG = "!CONNECT"
    DISCONNECT_MSG = "!DISCONNECT"


class ClientUDP:

    def __init__(self, addr):

        self.addr = tuple(addr)
        self.ip = addr[0]
        self.port = addr[1]
        self.connected = True

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, msg):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        msg = msg.encode(Spec.FORMAT)

        self._socket.sendto(msg, self.addr)
    
    def run(self):
        '''
        Loop that wait for all messages.  
        Execute on_message method.  
        To end execution, call disconnect method.  
        '''

        while self.connected:

            # receive msg
            msg, address = self.socket.recvfrom(Spec.BUFSIZE)
            msg = msg.decode(Spec.FORMAT)

            self.on_message(msg)

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def disconnect(self):
        '''
        Send disconnection message to the server.  
        Not to be implemented!    
        '''
        self.send(Spec.DISCONNECT_MSG)
        self.connected = False