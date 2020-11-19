import numpy as np
from lib.udp import ClientUDP
from spec import Spec

class Client(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

        self.opp_client = None