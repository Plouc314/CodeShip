from comm.gameclient import GameClient
from game.ship import Ship
from game.bulletsystem import BulletSystem
from game.collisions import CollisionSystem
from game.api import API
from game.interface import GameInterface
from lib.plougame import Dimension
from lib.counter import Counter
from data.spec import Spec
import importlib, traceback, time
import numpy as np

class Game:

    def __init__(self, ui_client, connected=True):

        self.ui_client = ui_client
        self.own_id = None

        self.interface = GameInterface(ui_client)
        self.interface.add_button_logic('b quit', self.quit_logic)

        # patch the position where the ship are displayed to always display them centered
        self.position_patch = np.array([0,0], dtype=int) # scaled

        # if the game is running in main.py (meaning not the ui)
        self._is_running = False

        # if the game is active -> if the ship are moving...
        self._is_game_active = False

        self.has_init_info = False

        if connected:
            self._set_game_client()

    def _set_game_client(self):
        '''
        Set the game client, connect to the server.
        '''
        self.game_client = GameClient((self.ui_client.ip, Spec.PORT))
        BulletSystem.game_client = self.game_client

    def start_udp(self):
        '''
        Connect udp to server, 
        start infinite loop.
        '''
        # connect
        self.ui_client.connect_udp(self.game_client.get_local_port())
        self.game_client.start()

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

    def setup(self, own_id, own_grid, opp_grid, own_username, opp_username):
        '''
        Set up `Game` instance for the game,
        given:  
        `own_id` : Set the id use to set the position, color of the ships.  
        `own/opp grid` : the grids used to create the ships.  
        `own/opp username` : the usernames used to set up the game's interface.  
        '''
        self.reset_values()
        self.running = True
        self.own_id = bool(own_id)
        self.create_ships(own_grid, opp_grid)
        self.setup_interface(own_username, opp_username)
        self.setup_api()

        self.init_script()

    def create_ships(self, own_grid, opp_grid):
        '''
        Create the ships, given the grids.  
        Must have set id before (call `set_own_id`)
        '''
        self.own_ship = Ship.from_grid(Spec.OWN_TEAM, own_grid)
        self.opp_ship = Ship.from_grid(Spec.OPP_TEAM, opp_grid)

        BulletSystem.set_ships(self.own_ship, self.opp_ship)
        CollisionSystem.set_ships(self.own_ship, self.opp_ship)

        self.own_ship.compile()
        self.opp_ship.compile()

        self._set_id_ships()
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

    def _set_id_ships(self):
        '''
        Create `.id_ships` that store the ships according to their id.
        '''
        self.id_ships = {}
        if self.own_id:
            self.id_ships[1] = self.own_ship
            self.id_ships[2] = self.opp_ship
        else:
            self.id_ships[1] = self.opp_ship
            self.id_ships[2] = self.own_ship

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
        # return opponent ship to make them face each other
        self.id_ships[2].orien = np.pi

        self.id_ships[1].set_pos(Spec.POS_P1)
        self.id_ships[2].set_pos(Spec.POS_P2)

        self.id_ships[1].set_color(Spec.COLOR_P1)
        self.id_ships[2].set_color(Spec.COLOR_P2)

    def reset_values(self):
        '''
        Reset values of third party components.
        '''
        self.game_client.reset_values()
        BulletSystem.reset()
        CollisionSystem.reset()

    def handeln_out_ship(self):
        '''
        Check if own ship is in the perimeter (window)
        '''
        pos = self.own_ship.get_pos()
        dim_ship = Spec.DIM_BLOCK * Spec.SIZE_GRID_SHIP
        
        # right
        if pos[0] > Spec.DIM_WINDOW[0]:
            self.own_ship.set_pos( (-dim_ship[0], pos[1]) )
        
        # left
        if pos[0] + dim_ship[0] < 0:
            self.own_ship.set_pos( (Spec.DIM_WINDOW[0], pos[1]) )

        # down
        if pos[1] > Spec.DIM_WINDOW[1]:
            self.own_ship.set_pos( (pos[0], -dim_ship[1]) )

        # up
        if pos[1] + dim_ship[1] < 0:
            self.own_ship.set_pos( (pos[0], Spec.DIM_WINDOW[1]) )

    def check_end_game(self):
        '''
        Check if the game is ended.
        '''
        ended = False

        if len(self.own_ship.typed_blocks['Turret']) == 0 or len(self.own_ship.typed_blocks['Generator']) == 0:
            ended = True
            has_win = False
            
        if len(self.opp_ship.typed_blocks['Turret']) == 0 or len(self.opp_ship.typed_blocks['Generator']) == 0:
            ended = True
            has_win = True
        
        if ended:
            self._is_game_active = False
            self.interface.set_end_game(has_win)
            self.ui_client.send_end_game(int(has_win))

    def quit_logic(self):
        '''
        Logic of the button quit of the interface.  
        Quit the game, return to the ui.  
        '''
        self._is_running = False
        # reset game interface
        self.interface.change_state('base')

    def _get_traceback(self, error):
        '''
        Return a formated traceback of the given error.
        '''
        tb = error.__traceback__
        tb = traceback.extract_tb(tb).format()

        error_type = error.__class__.__name__
        error_msg = str(error)

        tb.append(f'{error_type}: {error_msg}')
        return tb

    @Counter.add_func
    def run_script(self):
        '''
        Run the user's script
        '''
        try:
            self.script.main()
        except Exception as e:
            print("[WARNING] Error occured in script.")

    def _get_init_info(self):
        '''
        Look if the opponent has send the after initialisation info
        '''
        shield_hp = self.ui_client.in_data['gis']
        if not shield_hp is None:
            self.has_init_info = True
            self.opp_ship.total_shield_hp = shield_hp

    def init_script(self):
        '''
        Run "init" function of user's script.  
        Set up blocks that need to be set up (Shield).  
        Send after init state to opponent
        '''
        # run init function
        try:
            self.script.init()
        except:
            print("[WARNING] Error occured in script initiation.")
        
        shields = self.own_ship.typed_blocks['Shield']

        for shield in shields:
            shield.setup()

        # get total shield hp
        total_shield_hp = Spec.SHIELD_HP * sum((shield.intensity for shield in shields))

        self.own_ship.total_shield_hp = total_shield_hp
        self.ui_client.send_game_init_info(total_shield_hp)

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
        self.own_id = bool(np.random.choice([0, 1]))
        self.create_ships(grid, grid)
        self.setup_api(script=script_module)

        try:
            self.script.init()
            st = time.time()
            self.script.main()
            duration = time.time() - st
        
        except Exception as e:

            tb = self._get_traceback(e)

            return 'runtime', tb
        
        # check execution time
        if duration > Spec.SCRIPT_EXEC_TIME:
            return 'execution time', None

        return None, None

    @Counter.add_func
    def run(self, pressed, events):
        '''
        Run the game.
        '''
        if not self.has_init_info:
            self._get_init_info()

        if self._is_game_active:
            CollisionSystem.run()
            BulletSystem.run()
            BulletSystem.update_opp_bullets()
            API.run()

            self.game_client.set_opp_state(self.opp_ship)

            self.run_script()

            self.own_ship.run()
            self.opp_ship.run(remote_control=True)
            self.handeln_out_ship()

            # send state to server
            self.game_client.send_state(self.own_ship)

            self.check_end_game()

        self.own_ship.display()
        self.opp_ship.display()

        BulletSystem.display()

        self.interface.react_events(pressed, events)
        self.interface.update(*self.id_ships.values())
        self.interface.display()

        
