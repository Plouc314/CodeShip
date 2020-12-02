from comm.gameclient import GameClient
from game.ship import Ship
from game.bulletsystem import BulletSystem
from game.api import API
from game.interface import GameInterface
from spec import Spec
import importlib, traceback
import numpy as np

class Game:

    def __init__(self, ui_client, connected=True):

        self.ui_client = ui_client
        self.own_id = None

        self.interface = GameInterface(ui_client)
        self.interface.add_button_logic('b quit', self.quit_logic)

        # if the game is running in main.py (meaning not the ui)
        self._is_running = False

        # if the game is active -> if the ship are moving...
        self._is_game_active = False

        if connected:
            self.game_client = GameClient((ui_client.ip, Spec.PORT))
            BulletSystem.game_client = self.game_client

    @property
    def running(self):
        return self._is_running
    
    @running.setter
    def running(self, value):
        if value:
            self._is_running = True
            self._is_game_active = True
        else:
            raise ValueError("Can't set running to False.")

    def create_ships(self, own_grid, opp_grid):
        '''
        Create the ships, given the grids.
        '''
        self.own_ship = Ship.from_grid(Spec.OWN_TEAM, own_grid)
        self.opp_ship = Ship.from_grid(Spec.OPP_TEAM, opp_grid)

        BulletSystem.set_ships((self.own_ship, self.opp_ship))

        self.own_ship.compile()
        self.opp_ship.compile()

        self.set_ships_start_pos()

    def setup_api(self, script=None):
        '''
        Setup the api ships,  
        if `script=None`, load the user script.
        '''
        API.set_ship(self.own_ship)
        API.set_opponent_ship(self.opp_ship)

        if script == None:
            self.script = importlib.import_module('script')
        else:
            self.script = script

    def set_own_id(self, own_id):
        '''
        Set the id use to set the position, color of the ships.
        '''
        self.own_id = bool(own_id)

    def setup_interface(self, own_username, opp_username):
        '''
        set up the game interface, start the clock.
        '''
        if self.own_id:
            self.interface.set_users(own_username, opp_username)
        else:
            self.interface.set_users(opp_username, own_username)

        self.interface.start_clock()

    def set_ships_start_pos(self):
        '''
        Set the position of the ships at the begining of the game.  
        Set their color according to their position.  
        '''
        if self.own_id:
            ship1 = self.own_ship
            ship2 = self.opp_ship
        else:
            ship1 = self.opp_ship
            ship2 = self.own_ship

        # return opponent ship to make them face each other
        ship2.orien = np.pi

        ship1.set_pos(Spec.POS_P1)
        ship2.set_pos(Spec.POS_P2)

        ship1.set_color(Spec.COLOR_P1)
        ship2.set_color(Spec.COLOR_P2)

    def check_end_game(self):
        '''
        Check if the game is ended.
        '''
        if len(self.own_ship.blocks) == 0:
            self._is_game_active = False
            self.interface.change_state('end')
            self.game_client.reset_values()
            self.ui_client.send_end_game(0)
            
        if len(self.opp_ship.blocks) == 0:
            self._is_game_active = False
            self.interface.change_state('end')
            self.game_client.reset_values()
            self.ui_client.send_end_game(1)

    def quit_logic(self):
        '''
        Logic of the button quit of the interface.  
        Quit the game, return to the ui.  
        '''
        self._is_running = False

    def run_script(self):
        '''
        Run the user's script
        '''
        try:
            self.script.main()
        except Exception as e:
            print("[WARNING] Error occured in script.")
        
    def test_script(self, grid, script_module):
        '''
        Test the user sript at runtime.  
        Run one frame, with the user ship on both side.  
        Argument: the script module  
        Return: 
            - bool, If there is an error  
            - tuple, In case of error (else None): the error type, message & traceback
        '''
        # set ships
        self.set_own_id(np.random.choice([0, 1]))
        self.create_ships(grid, grid)
        self.setup_api(script=script_module)

        is_error = False

        try:
            self.script.main()
        
        except Exception as e:

            is_error = True

            tb = e.__traceback__
            tb = traceback.extract_tb(tb).format()

            error_type = e.__class__.__name__
            error_msg = str(e)
        
        if is_error:
            return True, (error_type, error_msg, tb)
        else:
            return False, None

    def set_opp_state(self):
        '''
        Set opponent state according to comm from server
        '''
        pos = self.game_client.opponent_state['pos']
        if pos is not None:
            self.opp_ship.set_pos(pos, scaled=True)
        
        orien = self.game_client.opponent_state['orien']
        if orien:
            self.opp_ship.orien = orien

        # set hp
        hps = self.game_client.opponent_state['hps']

        if not hps is None:

            for x in range(Spec.SIZE_GRID_SHIP):
                for y in range(Spec.SIZE_GRID_SHIP):
                    
                    block = self.opp_ship.get_block_by_coord((x,y))

                    if not block:
                        continue

                    block.hp = hps[x,y]

                    if block.hp <= 0:
                        self.opp_ship.remove_block(block=block)

        # set turrets' orien
        oriens = self.game_client.opponent_state['turrets']

        if len(oriens) != 0:
            
            for turret, orien in zip(self.opp_ship.typed_blocks['Turret'], oriens):
                turret.orien = orien
                turret.rotate_surf(orien)

    def run(self, pressed, events):
        '''
        '''
        if self._is_game_active:
            BulletSystem.run()
            BulletSystem.update_opp_bullets()
            API.run()

            self.set_opp_state()

            self.run_script()

            self.own_ship.run()
            self.opp_ship.run(remote_control=True)

            # send state to server
            self.game_client.send_state(self.own_ship)

            self.own_ship.display()
            self.opp_ship.display()

            BulletSystem.display()

            self.check_end_game()

        self.interface.react_events(pressed, events)
        self.interface.display()

        
