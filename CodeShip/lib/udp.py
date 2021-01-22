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
    DISCONNECT_MSG = b"!DISCONNECT"


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

    def send(self, msg: bytes, addr=None):
        '''
        Send the given message to the client.  
        If `addr` is not specified: take default address.  
        In case of error: abort operation.  
        '''
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
            
            if Spec.DISCONNECT_MSG in msg:
                break
            
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