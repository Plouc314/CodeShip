from lib.udp import ServerUDP
from udp.client import Client
from spec import Spec
import threading


class Server(ServerUDP):

    def __init__(self):

        super().__init__(Spec.PORT)

        self.clients = {}
    
    def on_connection(self, addr):
        '''
        '''
        client = Client(addr)
        self.clients[client.ip] = client

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

            # connect to user to each other
            ip1, ip2 = msg

            self.clients[ip1].opp_client = self.clients[ip2]
            self.clients[ip2].opp_client = self.clients[ip1]