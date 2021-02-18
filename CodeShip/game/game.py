from comm.gameclient import GameClient
from game.ship import Ship
from game.bulletsystem import BulletSystem
from game.collisions import CollisionSystem
from game.api import API
from game.interface import GameInterface
from game.player import Player
from game.bot import BotPlayer
from lib.plougame import Dimension
from lib.perfeval import Counter
from data.spec import Spec
import importlib, traceback, time
import numpy as np

class Game:

    def __init__(self, ui_client, connected=True):

        self.ui_client = ui_client
        Player.client = ui_client

        self.interface = GameInterface(ui_client)
        self.interface.add_button_logic('b quit', self.quit_logic)

        # if the game is running in main.py (meaning not the ui)
        self._is_running = False

        # if the game is active -> if the ship are moving...
        self._is_game_active = False

        # if one of the player is a bot
        self._is_bot = False

        self.game_client = None
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

    def setup(self, team, own_grid, opp_grid, own_username, opp_username, 
            initiate_api=True):
        '''
        Set up `Game` instance for the game,
        given:  
        `team` : Set the team used to set the position, color of the ships.  
        `own/opp grid` : the grids used to create the ships.  
        `own/opp username` : the usernames used to set up the game's interface.  
        `initate_api`: if True, the `setup_api` method and `init_script` method will be executed
        '''
        self.reset_values()
        self.running = True
        self._is_bot = False

        self.players = {
            'own': Player(own_username, team, own_grid, with_script=True),
            'opp': Player(opp_username, (-team + 3), opp_grid),
        }

        if not self.game_client is None:
            self.game_client.set_opp_team(self.players['opp'].team)

        self.setup_interface()
        API.set_players(self.players['own'], self.players['opp'])
        BulletSystem.set_players(self.players['own'], self.players['opp'])
        CollisionSystem.set_ships(self.players['own'].ship, self.players['opp'].ship)

        if initiate_api:
            self.init_script()

    def setup_with_bot(self, team, own_grid, own_username):
        '''
        Set up `Game` instance for the game,
        with one of the player being a bot,
        given:  
        `team` : Set the team used to set the position, color of the ships.  
        `own_grid` : the grid used to create the ship.  
        `own_username` : the username used to set up the game's interface.  
        '''
        self.reset_values()
        self.running = True
        self._is_bot = True

        self.players = {
            'own': Player(own_username, team, own_grid, with_script=True),
            'opp': BotPlayer(-team + 3, 'bot1'),
        }

        self.setup_interface()
        self.interface.has_opp_max_shield = True

        API.set_players(self.players['own'], self.players['opp'])
        BulletSystem.set_players(self.players['own'], self.players['opp'])
        CollisionSystem.set_ships(self.players['own'].ship, self.players['opp'].ship)

        self.init_script(send_data=False)
        self.players['opp'].initiate(self.players['own'])

    def setup_interface(self):
        '''
        set up the game interface,  
        start the clock.
        '''
        self.interface.set_players(self.players['own'], self.players['opp'])
        self.interface.start_clock()

    def reset_values(self):
        '''
        Reset values of third party components.
        '''
        if self.game_client != None:
            self.game_client.reset_values()
        
        API.reset()
        BulletSystem.reset()
        CollisionSystem.reset()

    def check_end_game(self, send_data=True):
        '''
        Check if the game is ended.  
        If send_data=True, send the game result to the server.
        '''
        ended = False

        with self.ui_client.get_data('olg') as has_left:
            if has_left:
                ended = True
                has_win = True
                cause = "Your opponent has disconnected." 

        if self.players['own'].n_script_error > Spec.MAX_SCRIPT_ERROR:
            ended = True
            has_win = False
            cause = "There was too many script errors."
        
        if self.players['opp'].n_script_error > Spec.MAX_SCRIPT_ERROR:
            ended = True
            has_win = True
            cause = "There was too many script errors."

        if len(self.players['own'].ship.typed_blocks['Turret']) == 0:
            ended = True
            has_win = False
            cause = "You don't have any turrets left."

        if len(self.players['own'].ship.typed_blocks['Generator']) == 0:
            ended = True
            has_win = False
            cause = "You don't have any generators left."

        if len(self.players['opp'].ship.typed_blocks['Turret']) == 0:
            ended = True
            has_win = True
            cause = "Your opponent doesn't have any turrets left."
        
        if len(self.players['opp'].ship.typed_blocks['Generator']) == 0:
            ended = True
            has_win = True
            cause = "Your opponent doesn't have any generators left."

        if ended:
            self._is_game_active = False
            self.has_init_info = False
            self.interface.set_end_game(has_win, cause)

            if send_data:
                self.ui_client.send_end_game(has_win)

    def quit_logic(self):
        '''
        Logic of the button quit of the interface.  
        Quit the game, return to the ui.  
        '''
        self._is_running = False
        # reset game interface
        self.interface.change_state('base')

    def _get_init_info(self):
        '''
        Look if the opponent has send the after initialisation info
        '''
        shield_hp = self.ui_client.in_data['gis']
        if not shield_hp is None:
            self.has_init_info = True
            self.players['opp'].total_shield_hp = shield_hp

    def init_script(self, send_data=True):
        '''
        Run "init" function of user's script.  
        Set up blocks that need to be set up (Shield).  
        Send after init state to opponent.  
        Initiate the API
        '''
        self.players['own'].call_script_init(send_data=send_data)
        API.init()
        self.players['own'].finalize_initiation(send_data=send_data)

    def test_script(self, grid):
        '''
        Test the user sript at runtime.  
        Run one frame, with the user ship on both side.  
        Argument: the user's grid ship 
        Return: 
            - bool, If there is an error  
            - list, In case of error (else None): the traceback formated as a list
        '''
        self.setup(1, grid, grid, '', '', initiate_api=False)

        # execute init
        tb = self.players['own'].call_script_init(send_data=False)
        
        if tb != None:
            return 'init', tb
        
        # finalize initiation
        API.init()
        self.players['own'].finalize_initiation(send_data=False)

        # execute main
        st = time.time()
        tb = self.players['own'].call_script_main(send_data=False)
        duration = time.time() - st

        if tb != None:
            return 'runtime', tb

        # check execution time
        if duration > Spec.SCRIPT_EXEC_TIME:
            return 'execution time', None

        return None, None

    def _update_opp_script_error(self):
        '''
        Check if the opponent's script has made an error,  
        if so, store it in player object
        '''
        with self.ui_client.get_data('ige') as n:
            if n == None:
                return
            
            self.players['opp'].n_script_error = n

    @Counter.add_func
    def run(self, pressed, events):
        '''
        Run the game.
        '''
        if self._is_bot:
            self._run_with_bot(pressed, events)
        else:
            self._run_normal(pressed, events)

    def _run_normal(self, pressed, events):
        '''
        Run the game.  
        With one player in local and one player remotely controlled
        '''
        if not self.has_init_info:
            self._get_init_info()

        self._update_opp_script_error()

        if self._is_game_active:
            CollisionSystem.run()
            BulletSystem.run()
            BulletSystem.update_opp_bullets()
            API.run()

            self.game_client.set_opp_state(self.players['opp'])

            self.players['opp'].run(remote_control=True)
            self.players['own'].run()

            # send state to server
            self.game_client.send_state(self.players['own'])

            self.check_end_game()

        self.players['own'].display()
        self.players['opp'].display()

        BulletSystem.display()

        self.interface.react_events(pressed, events)
        self.interface.update()
        self.interface.display()

    def _run_with_bot(self, pressed, events):
        '''
        Run the game with a bot.
        '''
        if self._is_game_active:
            CollisionSystem.run(remote_control=False)
            BulletSystem.run(remote_control=False)
            API.run()

            self.players['opp'].run(send_data=False)
            self.players['own'].run(send_data=False)

            self.check_end_game(send_data=False)

        self.players['own'].display()
        self.players['opp'].display()

        BulletSystem.display()

        self.interface.react_events(pressed, events)
        self.interface.update()
        self.interface.display()
