import threading, pickle
from lib.udp import ClientUDP, ErrorUDP
from lib.console import Console
from game.bulletsystem import BulletSystem, Bullet
from data.spec import Spec
import numpy as np
from lib.perfeval import Counter

class GameData:
    def __init__(self, player):

        ship = player.ship
        # basic info
        self.pos = np.array(ship.get_pos(), dtype='int16')
        self.speed = np.array(ship.get_speed(), dtype='float32')
        self.acc = np.array(ship.get_acc(), dtype='float32')
        self.orien = ship.orien

        # blocks
        self.hps = np.zeros(Spec.SHAPE_GRID_SHIP, dtype='int16')
        self.shield_hps = np.zeros(Spec.SHAPE_GRID_SHIP, dtype='int16')
        self.actives = np.zeros(Spec.SHAPE_GRID_SHIP, dtype=bool)

        for block in ship.blocks.values():
            x,y = block.coord
            self.hps[x,y] = block.hp
            self.shield_hps[x,y] = block.hp_shield
            self.actives[x,y] = block.get_activate()

        # bullets
        bullets = BulletSystem.get_bullets_by_team(player.team)
        self.bullets = np.zeros((len(bullets),5), dtype='int32')
        for i, bullet in enumerate(bullets):
            x, y = bullet.get_pos()
            self.bullets[i,:] = bullet.id, x, y, 1e4 * bullet.orien, bullet.damage

        # turrets
        turrets = ship.typed_blocks['Turret']
        self.turrets = np.zeros((len(turrets)), dtype='float32')
        for i, turret in enumerate(turrets):
            self.turrets[i] = turret.orien

        # actions cache
        self.actions = []
        for action in player.get_cache(string_format=True):
            self.actions.append(action)

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
        Console.print("[UDP] Started client's thread.")

    def reset_values(self):
        '''
        Reset all values stored in client.
        '''
        self.data = None
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

        self.opp_team = None

        # contains opponent bullets (temporary)
        self.bullets = []

    def set_opp_team(self, team):
        '''
        Set the team of the opponent to
        set the received opponent's bullets correctly.
        '''
        self.opp_team = team

    def on_message(self, data):
        self.data = pickle.loads(data)
        self.update_bullets()    

    def update_bullets(self):
        for infos in self.data.bullets:
            _id, x, y, orien, damage = infos
            bullet = Bullet(self.opp_team, [x, y], 1e-4 * orien, damage=damage, _id=_id)
            self.bullets.append(bullet)

    @Counter.add_func
    def send_state(self, player):
        '''
        Send the state of the player to the opponent.
        '''
        data = GameData(player)
        self.send(pickle.dumps(data))

    @Counter.add_func
    def set_opp_state(self, player):
        if self.data is None:
            return
        
        ship = player.ship

        ship.set_pos(self.data.pos)
        ship.orien = self.data.orien
        ship.speed[:] = self.data.speed
        ship.acc[:] = self.data.acc

        # get it as a list -> remove value during iteration
        items = list(ship.blocks.items())

        for key, block in items:
            x, y = block.coord

            if self.data.hps[x,y] <= 0:
                ship.remove_block(key)
                continue

            block.hp = self.data.hps[x,y]
            block.hp_shield = self.data.shield_hps[x,y]
            block.set_activate(self.data.actives[x,y])

        # set turrets' orien
        oriens = self.data.turrets

        for turret, orien in zip(ship.typed_blocks['Turret'], oriens):
            turret.orien = orien
            turret.rotate_surf(orien)

        # actions cache
        player.str_cache = self.data.actions