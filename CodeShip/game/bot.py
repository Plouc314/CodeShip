from game.api import API, Opponent, Ship, Constants
from game.player import Player
from data.spec import Spec
import os, json, importlib, numpy as np

# create copy of API's static objects (copy of classes)
BotAPI = type('BotAPI', API.__bases__, dict(API.__dict__))
BotOpponent = type('BotOpponent', Opponent.__bases__, dict(Opponent.__dict__))
BotShip = type('BotShip', Ship.__bases__, dict(Ship.__dict__))

BotAPI._ship_cls = BotShip
BotAPI._opponent_cls = BotOpponent

class BotPlayer(Player):
    '''
    Bot version of Player

    Manage its own API and script
    '''

    def __init__(self, team, botname):
        
        # load bot specifications
        with open(os.path.join('game', 'bots', f'{botname}.json'), 'r') as file:
            data = json.load(file)
        
        grid = np.array(data['ship'])
        script = '\n'.join(data['script'])

        super().__init__('Bot', team, grid)

        self._set_script(script)
    
    def _set_script(self, script: str):
        '''
        Set the script as a module
        '''
        # https://stackoverflow.com/questions/3614537/python-import-string-of-python-code-as-module
        spec = importlib.util.spec_from_loader('_script', loader=None)
        _script = importlib.util.module_from_spec(spec)

        exec(script, _script.__dict__)

        self.script = _script

    def run(self, **kwargs):
        '''
        Overwrite of Player.run method,  
        Execute bot API run method
        '''
        BotAPI.run()
        super().run(**kwargs)
    
    def initiate(self, player):
        '''
        Initialize the API and script,  
        given the other player
        '''
        BotAPI.set_players(self, player)
        self.call_script_init(send_data=False)
        BotAPI.init()
        self.finalize_initiation(send_data=False)