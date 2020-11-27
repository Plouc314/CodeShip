import threading
from lib.udp import ClientUDP
from game.bulletsystem import BulletSystem, Bullet
from spec import Spec
import numpy as np

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class GameClient(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

        self.opponent_state = {
            'pos': None,
            'orien': None,
            'hps': None
        }

        # contains opponent bullets (temporary)
        self.bullets = []

    def start(self):
        '''
        Start a infinite loop in another thread to listen to the server.
        '''
        if self.connected:
            print('[LOCAL] Started UDP thread.')
            self._thread = threading.Thread(target=self.run)
            self._thread.start()

    def on_message(self, msg):
        '''Decode state'''
        parts = msg.split(sep_m)

        # get position, orientation
        pos_x, pos_y, orien = parts[0].split(sep_c)

        self.opponent_state['pos'] = np.array([pos_x, pos_y], dtype=int)
        self.opponent_state['orien'] = float(orien)

        # get blocks' hp
        hps = parts[1].split(sep_c)
        hps = np.array(hps, dtype=int)
        hps = hps.reshape(Spec.SHAPE_GRID_SHIP)
        self.opponent_state['hps'] = hps

        # get bullets
        str_bullets = parts[2].split(sep_c)

        if '' in str_bullets:
            str_bullets.remove('')
    
        for str_bullet in str_bullets:

            x, y, orien, damage = str_bullet.split(sep_c2)

            bullet = Bullet(Spec.OPP_TEAM, [int(x), int(y)], float(orien), damage=int(damage))

            self.bullets.append(bullet)

    def send_state(self, ship):
        '''
        Create the msg send to the server at each frame.
        '''

        msg = ''

        # add position, orientation
        pos = ship.get_pos()
        msg += f'{int(pos[0])}{sep_c}{int(pos[1])}'
        msg += f'{sep_c}{ship.orien:.4f}'

        msg += sep_m

        # add blocks' hp
        for x in range(Spec.SIZE_GRID_SHIP):
            for y in range(Spec.SIZE_GRID_SHIP):
                
                block = ship.get_block_by_coord((x,y))

                if block == None:
                    hp = 0
                else:
                    hp = block.hp
                
                msg += str(hp) + sep_c
        
        # remove last separator
        msg = msg[:-1]

        msg += sep_m

        # send bullets of own ship
        for bullet in BulletSystem.get_bullets_by_team(ship.team):

            # add pos, orien, damage
            x, y = bullet.get_pos()
            msg += f'{int(x)}{sep_c2}{int(y)}{sep_c2}{bullet.orien:.4f}'
            msg += f'{sep_c2}{bullet.damage}'

            msg += sep_c

        self.send(msg)
