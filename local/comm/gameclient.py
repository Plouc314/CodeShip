import threading
from lib.udp import ClientUDP
from spec import Spec
import numpy as np

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class GameClient(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

    def on_message(self, msg):
        self.msg = msg

    def send_state(self, ship):
        '''
        Create the msg send to the server at each frame.
        '''
        msg = ''

        # add position, orientation
        pos = ship.get_pos()
        msg += f'{pos[0]}{sep_c}{pos[1]}'
        msg += f'{sep_c}{ship.orien:.4f}'

        msg += sep_m

        # add block's hp
        for x in range(Spec.SIZE_GRID_SHIP):
            for y in range(Spec.SIZE_GRID_SHIP):
                
                block = ship.get_block_by_coord(x,y)

                if block == None:
                    hp = 0
                else:
                    hp = block.hp
                
                msg += str(hp) + sep_c
        
        # remove last separator
        msg = msg[:-1]

        msg += sep_m

