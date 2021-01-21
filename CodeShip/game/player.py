import numpy as np
from comm.uiclient import UIClient
from game.ship import Ship
from data.spec import Spec
from lib.counter import Counter
import importlib, traceback

def get_traceback(error) -> list:
    '''
    Return a formated traceback of the given error.
    '''
    tb = error.__traceback__
    tb = traceback.extract_tb(tb).format()

    error_type = error.__class__.__name__
    error_msg = str(error)

    tb.append(f'{error_type}: {error_msg}')
    return tb

class Player:
    
    client: UIClient = None

    def __init__(self, username, team, grid, with_script=False):
        
        self.username = username
        self.team = team
        self.n_script_error = 0
        self.total_shield_hp = 0

        # store weak ref of every actions
        self._actions_cache = []

        self.create_ship(grid)

        if with_script:
            self.script = importlib.import_module('script')

    def create_ship(self, grid):
        '''
        Create the Ship object given its grid.  
        Set its starting position & color according to its team.
        '''
        self.ship = Ship.from_grid(grid, self.team)
        self.ship.compile()

        # set starting position & color
        if self.team == 1:
            self.ship.set_pos(Spec.POS_P1)
            self.ship.set_color(Spec.COLOR_P1)
        else:
            self.ship.set_pos(Spec.POS_P2)
            self.ship.set_color(Spec.COLOR_P2)
            self.ship.orien = np.pi

    def setup_shields(self) -> int:
        '''
        Call the setup method of all Shield blocks of the ship.  
        Set the total amound of shield hp.
        '''
        tot_intensity = 0
        for shield in self.ship.typed_blocks['Shield']:
            shield.setup()
            tot_intensity += shield.intensity
        
        # set total shield hp
        self.total_shield_hp = Spec.SHIELD_HP * tot_intensity

    def call_script_init(self, send_data=True):
        '''
        Call the `init` function of the script,
        Handeln potential script's errors.  
        In case of error, returns a formated traceback (from `get_traceback`),
        else returns None.  
        If send_data=True and an error occured, 
        send message to the server (in game purposes)
        '''
        tb = None
        # run init function
        try:
            self.script.init()
        except Exception as e:
            self.n_script_error += 1

            if send_data:
                self.client.send_in_game_error(self.n_script_error)
            
            tb = get_traceback(e)

            print("[WARNING] Error occured in script initiation.")

        return tb

    def finalize_initiation(self, send_data=True):
        '''
        Set up blocks that need to be set up (Shield).  
        If send_data=True,
        send the after-initiation state to the opponent.  
        '''
        self.setup_shields()
        if send_data:
            self.client.send_game_init_info(self.total_shield_hp)
    
    @Counter.add_func
    def call_script_main(self, send_data=True):
        '''
        Execute the `main` function of the script.  
        Handeln potential errors.   
        In case of error, returns a formated traceback (from `get_traceback`),
        else returns None.  
        If send_data=True and an error occured, 
        send message to the server (in game purposes)
        '''
        is_error = False
        tb = None

        try:
            self.script.main()
        except Exception as e:
            is_error = True
            tb = get_traceback(e)
        
        if is_error:
            self.n_script_error += 1

            if send_data:
                self.client.send_in_game_error(self.n_script_error)

        return tb

    def run(self, remote_control=False):
        '''
        Call Ship's run method
        '''
        self.ship.run(remote_control=remote_control)

    def display(self):
        '''
        Call Ship's display method
        '''
        self.ship.display()

    def handeln_out_ship(self):
        '''
        Check if the ship is in the perimeter (window)
        '''
        pos = self.ship.get_pos()
        dim_ship = Spec.DIM_BLOCK * Spec.SIZE_GRID_SHIP
        
        # right
        if pos[0] > Spec.DIM_WINDOW[0]:
            self.ship.set_pos( (-dim_ship[0], pos[1]) )
        
        # left
        if pos[0] + dim_ship[0] < 0:
            self.ship.set_pos( (Spec.DIM_WINDOW[0], pos[1]) )

        # down
        if pos[1] > Spec.DIM_WINDOW[1]:
            self.ship.set_pos( (pos[0], -dim_ship[1]) )

        # up
        if pos[1] + dim_ship[1] < 0:
            self.ship.set_pos( (pos[0], Spec.DIM_WINDOW[1]) )
    
    def add_action_to_cache(self, action):
        '''
        Add an action to the cache (weakref.ref)
        '''
        self._actions_cache.append(action)
    
    def get_cache(self):
        '''
        Access actions cache.  
        Return a generator of the cache, filter dead references.
        '''
        for action in self._actions_cache:
            if not action() is None:
                yield action()
            