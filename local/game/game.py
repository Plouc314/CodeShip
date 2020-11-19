from comm.gameclient import GameClient
from game.ship import Ship
from game.bulletsystem import BulletSystem
from game.api import API
from spec import Spec
import importlib, traceback
import numpy as np

class Game:

    def __init__(self, ui_client):

        self.ui_client = ui_client
        self.game_client = GameClient(Spec.ADDR_HOST)

    def create_ships(self, own_grid, opp_grid):
        '''
        Create the ships, given the grids.
        '''
        self.own_ship = Ship.from_grid(1, own_grid)
        self.opp_ship = Ship.from_grid(2, opp_grid)

        BulletSystem.set_ships((self.own_ship, self.opp_ship))

        self.own_ship.compile()
        self.opp_ship.compile()

        # return opponent ship to make them face each other
        self.opp_ship.orien = np.pi

        self.own_ship.set_pos(Spec.POS_OWN)
        self.opp_ship.set_pos(Spec.POS_OPP)


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

    def run_script(self):
        '''
        Run the user's script
        '''
        #try:
        self.script.main()
        #except Exception as e:
        
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

    def run(self):
        '''
        '''

        self.run_script()

        self.own_ship.run()
        self.opp_ship.run()

        # send state to server
        #self.game_client.send_state(self.own_ship)

        self.own_ship.display()
        self.opp_ship.display()

        BulletSystem.display()

        BulletSystem.run()
