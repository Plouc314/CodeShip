import threading
from lib.udp import ClientUDP
from spec import Spec
import numpy as np

class GameClient(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

    def on_message(self, msg):
        self.msg = msg

    