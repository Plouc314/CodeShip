import threading
from lib.udp import ClientUDP, ErrorUDP
from game.bulletsystem import BulletSystem, Bullet
from data.spec import Spec
import numpy as np
from lib.counter import Counter

sep_m, sep_c, sep_c2 = Spec.SEP_MAIN, Spec.SEP_CONTENT, Spec.SEP_CONTENT2

class GameClient(ClientUDP):

    def __init__(self, addr):

        super().__init__(addr)

        self.reset_values()

    def start(self):
        '''
        Start a infinite loop in another thread to listen to the server.
        '''
        self.running = True
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
            'shield hps': None,
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
        Hps, shield hps and activation
        '''
        # get part of string that corresponds to the extracted info
        string = string.split(sep_m)[1]

        infos = string.split(sep_c)
        hps, shield_hps, actives = [], [], []

        for info in infos:
            hp, shield_hp, active = info.split(sep_c2)
            hps.append(hp)
            shield_hps.append(shield_hp)
            actives.append(active)

        hps = np.array(hps, dtype=int)
        hps = hps.reshape(Spec.SHAPE_GRID_SHIP)
        self.opponent_state['hps'] = hps

        shield_hps = np.array(shield_hps, dtype=int)
        shield_hps = shield_hps.reshape(Spec.SHAPE_GRID_SHIP)
        self.opponent_state['shield hps'] = shield_hps

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

            _id, x, y, orien, damage = str_bullet.split(sep_c2)

            bullet = Bullet(Spec.OPP_TEAM, [int(x), int(y)], float(orien),
                        damage=int(damage), _id=int(_id))

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

    @Counter.add_func
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
        blocks = list(ship.blocks.values())

        for x in range(Spec.SIZE_GRID_SHIP):
            for y in range(Spec.SIZE_GRID_SHIP):
                
                block = ship.get_block_by_coord((x,y), blocks=blocks)

                # add hp and if block is activated
                if block == None:
                    hp = 0
                    shield_hp = 0
                    activate = 0
                else:
                    blocks.remove(block)
                    hp = block.hp
                    shield_hp = round(block.hp_shield)
                    activate = int(block.get_activate())
                
                msg += f'{hp}{sep_c2}{shield_hp}{sep_c2}{activate}{sep_c}'
        
        # remove last separator
        msg = msg[:-1]

        msg += sep_m

        # send bullets of own ship
        bullets = BulletSystem.get_bullets_by_team(ship.team)

        for bullet in bullets:

            # send: id, pos x, pos y, orien, damage
            x, y = bullet.get_pos()
            msg += f'{bullet.id}{sep_c2}{int(x)}{sep_c2}{int(y)}'
            msg += f'{sep_c2}{bullet.orien:.4f}{sep_c2}{bullet.damage}'

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

    @Counter.add_func
    def set_opp_state(self, ship):
        '''
        Set opponent state according to comm from server
        '''
        if self.opponent_state['pos'] is None:
            return
        
        pos = self.opponent_state['pos']
        ship.set_pos(pos)
        
        ship.orien = self.opponent_state['orien']
        ship.speed = self.opponent_state['speed']
        ship.acc = self.opponent_state['acc']

        # blocks info
        hps = self.opponent_state['hps']
        shield_hps = self.opponent_state['shield hps']
        actives = self.opponent_state['actives']

        # get it as a list -> remove value during iteration
        items = list(ship.blocks.items())

        for key, block in items:
            x, y = block.coord

            if hps[x,y] <= 0:
                ship.remove_block(key)
                continue

            block.hp = hps[x,y]
            block.hp_shield = shield_hps[x,y]
            block.set_activate(bool(actives[x,y]))

        # set turrets' orien
        oriens = self.opponent_state['turrets']

        for turret, orien in zip(ship.typed_blocks['Turret'], oriens):
            turret.orien = orien
            turret.rotate_surf(orien)
