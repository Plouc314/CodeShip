from lib.tcp import ServerTCP
from tcp.client import Client
from tcp.interaction import Interaction
from spec import Spec
import threading

class Server(ServerTCP):

    def __init__(self):

        super().__init__(Spec.PORT)

        self.clients = {} # key: ip 
        self.threads = {} # key: ip 

    def on_connection(self, conn, addr):
        '''
        Create client object and run client's loop in separate thread.
        '''
        client = Client(conn, addr)
        self.clients[client.ip] = client

        thread = threading.Thread(target=client.run)
        self.threads[client.ip] = thread

        thread.start()
