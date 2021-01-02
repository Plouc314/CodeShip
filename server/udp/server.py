from lib.udp import ServerUDP
from udp.client import Client
from spec import Spec
import threading


class Server(ServerUDP):

    def __init__(self):

        super().__init__(Spec.PORT)

    def create_client(self, addr):
        '''
        Create a client given it's address
        '''
        print(f"[UDP] |{addr[0]}| Connected.")
        client = Client(addr)
        self.add_client(client)

    def link_clients(self, ip1, ip2):
        '''
        Link two clients together.
        '''
        self.get_client(ip1).opp_client = self.get_client(ip2)
        self.get_client(ip2).opp_client = self.get_client(ip1)

    def unlink_clients(self, ip1, ip2):
        '''
        Unlink two clients
        '''
        self.get_client(ip1).opp_client = None
        self.get_client(ip2).opp_client = None

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

            # connect new client
            if msg[0] == 'conn':
                self.create_client(msg[1])

            # link two users to each other -> in game comm
            if msg[0] == 'link':
                ip1, ip2 = msg[1:]

                self.link_clients(ip1, ip2)
            
            # break connection beteween two users
            elif msg[0] == 'unlink':
                ip1, ip2 = msg[1:]

                self.unlink_clients(ip1, ip2)

            # remove a client -> disconnection
            elif msg[0] == 'rm':
                self.remove_client(msg[1])

            