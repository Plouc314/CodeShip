from lib.udp import ServerUDP
from udp.client import Client
from spec import Spec
import threading


class Server(ServerUDP):

    def __init__(self):

        super().__init__(Spec.PORT)

        self.clients = {} # key: ip
        self.threads = {} # key: ip
    
    def on_connection(self, addr):
        '''
        '''
        client = Client(addr)
        self.clients[client.ip] = client

        thread = threading.Thread(target=client.run)
        self.threads[client.ip] = thread

        thread.start()
    
    def run(self, queue):
        '''
        Run the server's run method in a separated thread,  
        start a inf loop that wait for comm through the queue
        '''

        self.main_thread = threading.Thread(target=super().run)

        self.main_thread.start()

        while True:

            msg = queue.get()

            if msg == "stop":
                self.running = False
                break