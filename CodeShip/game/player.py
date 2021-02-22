import numpy as np
from comm.uiclient import UIClient
from game.ship import Ship
from data.spec import Spec
from lib.perfeval import Counter
import importlib, traceback, os

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

        # store traceback of in game script errors
        self._tbs = []

        # for remotely controlled player
        self.str_cache = None

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
            self._tbs.append(tb)
        
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
        tb = None
        is_error = False

        try:
            self.script.main()
        except Exception as e:
            is_error = True
            tb = get_traceback(e)
            self._tbs.append(tb)
        
        if is_error:
            self.n_script_error += 1

            if send_data:
                self.client.send_in_game_error(self.n_script_error)

        return tb

    def run(self, remote_control=False, send_data=True):
        '''
        Call Ship's run method  
        If remote_control=False:  
        > Call user's script  
        > Handeln out ship 
        '''
        if not remote_control:
            self.call_script_main(send_data=send_data)

        self.ship.run(remote_control=remote_control)

        if not remote_control:
            self.handeln_out_ship()

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
    
    def get_cache(self, string_format=False):
        '''
        Access actions cache.  
        Return a generator of the cache, filter dead references.  
        If string_format=True, return a displayable string of the action (str)
        '''
        if not self.str_cache is None:
            for string in self.str_cache:
                yield string

        else:
            i = 0

            while i != len(self._actions_cache):
                action = self._actions_cache[i]

                if not action() is None:
                    i += 1

                    action = action()

                    if string_format:
                        yield action['block'] + ':   ' + action['desc']
                    else:
                        yield action
                
                else:
                    self._actions_cache.pop(i)
