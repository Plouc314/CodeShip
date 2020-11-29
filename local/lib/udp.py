import socket, time

class ErrorUDP:
    '''
    Basic printer for error.  
    Use the `call` static method.
    '''

    @staticmethod
    def call(traceback, warning=False):
        '''
        Display a message in the terminal.  
        In the format: `"[UDP] [call type] traceback"`
        '''
        if warning:
            call_type = '[WARNING]'
        else:
            call_type = '[ERROR]'
        
        print('[UDP]', call_type, traceback)


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
        self.connected = False

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connect()

    def connect(self):
        '''
        Try to connect to the server.  
        Return True if the connection succeeds.
        '''
        try:
            # send 4 times -> make sure the server receive it
            self.send(Spec.CONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.CONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.CONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.CONNECT_MSG)

            self.connected = True
            return True
        except:
            return False

    def send(self, msg):
        '''
        Send the given message to the client.  
        In case of error: abort operation.  
        '''
        msg = msg.encode(Spec.FORMAT)

        msg += b' ' * (Spec.BUFSIZE - len(msg))

        self._socket.sendto(msg, self.addr)
    
    def run(self):
        '''
        Loop that wait for all messages.  
        Execute on_message method.  
        To end execution, call disconnect method.  
        '''

        while self.connected:

            time.sleep(0.01)

            # receive msg
            msg, address = self._socket.recvfrom(Spec.BUFSIZE)
            msg = msg.decode(Spec.FORMAT).strip()

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
        Stop run loop if active.  
        Not to be implemented!    
        '''
        if self.connected:
            # send 4 times -> make sure the server receive it
            self.send(Spec.DISCONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.DISCONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.DISCONNECT_MSG)
            time.sleep(0.05)
            self.send(Spec.DISCONNECT_MSG)
            
            self.connected = False