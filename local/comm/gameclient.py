import threading
from lib.udp import ClientUDP, ErrorUDP
from game.bulletsystem import BulletSystem, Bullet
from lib.spec import Spec
import numpy as np

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class GameClient(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

        self.reset_values()

    def start(self):
        '''
        Start a infinite loop in another thread to listen to the server.
        '''

        if not self.connected:
            self.connect()

        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        print("[UDP] Started client's thread.")

    def reset_values(self):
        '''
        Reset all values stored in client.
        '''
        self.opponent_state = {
            'pos': None,
            'orien': None,
            'speed':None,
            'acc':None,
            'hps': None,
            'actives': None,
            'turrets': []
        }

        # contains opponent bullets (temporary)
        self.bullets = []

    def on_message(self, msg):
        '''
        Decode state
        '''
        # get position, orientation
        try:
            self.extract_basic_ship_info(msg)
        except:
            ErrorUDP.call("Extraction of ship's information failed.", warning=True)

        # get blocks' info
        try:
            self.extract_blocks_info(msg)
        except:
            ErrorUDP.call("Extraction of blocks' information failed.", warning=True)

        # get bullets
        try:
            self.extract_bullets(msg)
        except:
            ErrorUDP.call("Extraction of bullets' information failed.", warning=True)

        # get turrets' orien
        try:
            self.extract_turrets(msg)
        except:
            ErrorUDP.call("Extraction of turrets' information failed.", warning=True)

    def extract_basic_ship_info(self, string):
        '''
        Extract the (opponent) ship's position and orientation.
        '''
        # get part of string that corresponds to the extracted info
        string = string.split(sep_m)[0]
        pos, orien, speed, acc = string.split(sep_c)

        pos = np.array(pos.split(sep_c2), dtype=int)
        speed = np.array(speed.split(sep_c2), dtype=float)
        acc = np.array(acc.split(sep_c2), dtype=float)

        self.opponent_state['pos'] = pos
        self.opponent_state['orien'] = float(orien)
        self.opponent_state['speed'] = speed
        self.opponent_state['acc'] = acc

    def extract_blocks_info(self, string):
        '''
        Extract the info of the blocks.  
        Hps and activation
        '''
        # get part of string that corresponds to the extracted info
        string = string.split(sep_m)[1]

        infos = string.split(sep_c)
        hps, actives = [], []

        for info in infos:
            hp, active = info.split(sep_c2)
            hps.append(hp)
            actives.append(active)

        hps = np.array(hps, dtype=int)
        hps = hps.reshape(Spec.SHAPE_GRID_SHIP)
        self.opponent_state['hps'] = hps

        actives = np.array(actives, dtype=int)
        actives = actives.reshape(Spec.SHAPE_GRID_SHIP)
        self.opponent_state['actives'] = actives

    def extract_bullets(self, string):
        '''
        Extract the position of the bullets of the (opponent) ship.
        '''
        # get part of string that corresponds to the extracted info
        string = string.split(sep_m)[2]

        str_bullets = string.split(sep_c)

        if '' in str_bullets:
            str_bullets.remove('')
    
        for str_bullet in str_bullets:

            x, y, orien, damage = str_bullet.split(sep_c2)

            bullet = Bullet(Spec.OPP_TEAM, [int(x), int(y)], float(orien), damage=int(damage))

            self.bullets.append(bullet)

    def extract_turrets(self, string):
        '''
        Extract the orientations of the (opponent) turrets.
        '''
        # get part of string that corresponds to the extracted info
        string = string.split(sep_m)[3]

        oriens = string.split(sep_c)

        if '' in oriens:
            oriens.remove('')
        
        self.opponent_state['turrets'] = [float(orien) for orien in oriens]

    def send_state(self, ship):
        '''
        Create the msg send to the server at each frame.
        '''
        msg = ''

        # add position, orientation, speed, acc
        pos = ship.get_pos()
        msg += f'{int(pos[0])}{sep_c2}{int(pos[1])}'
        msg += f'{sep_c}{ship.orien:.4f}'
        speed = ship.get_speed()
        msg += f'{sep_c}{speed[0]:.2f}{sep_c2}{speed[1]:.2f}'
        acc = ship.get_acc()
        msg += f'{sep_c}{acc[0]:.2f}{sep_c2}{acc[1]:.2f}'

        msg += sep_m

        # add blocks' info
        for x in range(Spec.SIZE_GRID_SHIP):
            for y in range(Spec.SIZE_GRID_SHIP):
                
                block = ship.get_block_by_coord((x,y))

                # add hp and if block is activated
                if block == None:
                    hp = 0
                    activate = 0
                else:
                    hp = block.hp
                    activate = int(block.is_active)
                
                msg += f'{hp}{sep_c2}{activate}{sep_c}'
        
        # remove last separator
        msg = msg[:-1]

        msg += sep_m

        # send bullets of own ship
        bullets = BulletSystem.get_bullets_by_team(ship.team)

        for bullet in bullets:

            # add pos, orien, damage
            x, y = bullet.get_pos()
            msg += f'{int(x)}{sep_c2}{int(y)}{sep_c2}{bullet.orien:.4f}'
            msg += f'{sep_c2}{bullet.damage}'

            msg += sep_c

        # remove last separator
        if len(bullets) != 0:
            msg = msg[:-1]

        msg += sep_m

        # send turrets orien
        turrets = ship.typed_blocks['Turret']

        for turret in turrets:
            msg += f'{turret.orien:.4f}'
            msg += sep_c

        # remove last separator
        if len(turrets) != 0:
            msg = msg[:-1]

        self.send(msg)
