import numpy as np
from lib.udp import ClientUDP
from spec import Spec

class Client(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

        self.opp_client = None
    
    def on_disconnect(self):
        # avoid not implemented error
        pass

    def on_message(self, msg):
        '''
        Send state to other client.
        '''

        if self.opp_client != None:
            self.opp_client.send(msg)