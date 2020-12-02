from lib.udp import ServerUDP
from udp.client import Client
from spec import Spec
import threading


class Server(ServerUDP):

    def __init__(self):

        super().__init__(Spec.PORT)

    def on_connection(self, addr):

        print(f"[UDP] |{addr[0]}| Connected.")
        client = Client(addr)
        self.add_client(client)

    def connect_clients(self, ip1, ip2):
        '''
        Connect two clients together.
        '''
        self.get_client(ip1).opp_client = self.get_client(ip2)
        self.get_client(ip2).opp_client = self.get_client(ip1)

    def break_conn_clients(self, ip1, ip2):
        '''
        Break the connection between two clients
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

            # connect two users to each other -> in game comm
            if msg[0] == 'conn':
                ip1, ip2 = msg[1:]

                self.connect_clients(ip1, ip2)
            
            # break connection beteween two users
            elif msg[0] == 'disconn':
                ip1, ip2 = msg[1:]

                self.break_conn_clients(ip1, ip2)

            # remove a client -> disconnection
            elif msg[0] == 'rm':
                self.remove_client(msg[1])

            