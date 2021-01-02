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
        self.running = False

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(('',0))

    def get_local_port(self):
        '''
        Get the port on which the socket listen for messages
        '''
        return self._socket.getsockname()[1]

    def send(self, msg, addr=None):
        '''
        Send the given message to the client.  
        If `addr` is not specified: take default address.  
        In case of error: abort operation.  
        '''
        msg = msg.encode(Spec.FORMAT)

        msg += b' ' * (Spec.BUFSIZE - len(msg))

        if addr == None:
            addr = self.addr

        self._socket.sendto(msg, addr)
    
    def run(self):
        '''
        Loop that wait for all messages.  
        Execute on_message method.  
        To end execution, call disconnect method.  
        '''

        while self.running:

            time.sleep(0.01)

            # receive msg
            msg, address = self._socket.recvfrom(Spec.BUFSIZE)
            msg = msg.decode(Spec.FORMAT).strip()
            
            if msg != Spec.DISCONNECT_MSG:
                self.on_message(msg)

    @staticmethod
    def on_message(msg):
        '''
        Function executed when receiving a message.  
        Has as argument, the message.  
        To be implemented.  
        '''
        raise NotImplementedError("on_message method must be implemented.")

    def stop(self):
        '''
        Stop run loop if active.  
        Not to be implemented!    
        '''
        self.running = False

        # send msg to own socket to stop inf loop
        self.send(Spec.DISCONNECT_MSG, addr=self._socket.getsockname())