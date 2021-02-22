import numpy as np
import json, os
from lib.plougame.auxiliary import C
from lib.plougame import Formatter

class Spec:
    '''
    Static object

    Store all constants variables used in the whole program (on local).
    Store the "json data", the values stored in "data.json".

    Methods
    ---
    `load`: Load all the data, performed once during import  
    `set_json_variable`: Set the value of a json data variable  
    `set_attribute`: Set the value of a constant variable.
    '''

    formatter: Formatter

    PORT = 5050
    BOT_PORT = 5051
    IP_PUBLIC = "188.62.158.181"
    IP_HOST1 = "127.0.0.1"
    IP_HOST2 = "192.168.1.149"
    IP_HOST3 = "127.0.0.2"

    SIZE_BLOCK = 100
    SIZE_TURRET = 80
    DIM_BLOCK = np.array([100, 100])
    DIM_ITEM = np.array([70, 70])
    DIM_TURRET = np.array([80, 80])
    DIM_BULLET = np.array([20,20])
    DIM_BLOCK_MARGE = 10
    
    DIM_SIGNAL = np.array([15,15])
    POS_SIGNAL = np.array([10,10])
    POS_SIGNAL_SHIELD = np.array([10,30])
    COLOR_SIGNAL_SHIELD = np.array([0,255,255])

    SCRIPT_EXEC_TIME = 0.005

    SIZE_GRID_SHIP = 6
    SHAPE_GRID_SHIP = np.array([6,6])
    DIM_SHIP = np.array([600,600])

    CREDITS_TOTAL = 1000
    PRICE_BLOCK = 40
    PRICE_ENGINE = 70
    PRICE_GENERATOR = 70
    PRICE_SHIELD = 60
    PRICE_TURRET = 90

    MAX_CIRCULAR_ACC = 0.00025
    MAX_CIRCULAR_SPEED = 0.05
    AIR_RESISTANCE = 0.98
    BOUNCE_ACC_FACTOR = 1.5
    BOUNCE_CIRCULAR_SPEED = 0.01
    AUX_TIMER = 30

    HP_BLOCK = 100
    POWER_ENERGIE = 50
    POWER_CONS = 10
    POWER_CONS_MOTOR = 20
    MOTOR_FORCE = 10
    TURRET_FIRE_DELAY = 20
    TURRET_MAX_SPEED = 2
    TURRET_ROTATE_DELAY = 5

    SHIELD_DELAY = 10
    SHIELD_MAX_INTENSITY = 3
    SHIELD_HP = 100
    SHIELD_MAX_PRTC = 3
    SHIELD_REGEN_RATE = 0.2

    DAMAGE_BULLET = 20
    SPEED_BULLET = 40
    HIT_DURATION = 5

    DIM_MAX_EXPL = np.array([60,60])
    DIM_MIN_EXPL = np.array([20,20])
    TIME_EXPL = 3

    COLOR_P1 = C.BLUE
    COLOR_P2 = C.PURPLE
    DCOLOR_P1 = C.DARK_BLUE
    DCOLOR_P2 = C.DARK_PURPLE
    POS_P1 = np.array([400, 500])
    POS_P2 = np.array([2200, 500])
    MAX_SCRIPT_ERROR = 10
    RUNTIME_DELAY = 10

    PAGE_MENU = "menu"
    PAGE_CONN = "conn"
    PAGE_FRIENDS = "friends"
    PAGE_EDITOR = "editor"
    PAGE_PROFIL = "profil"
    PAGE_OFFLINE = "offline"

    CHAT_MAX_MSG = 20

    @classmethod
    def load(cls):
        '''
        Load the variable from the json file
        '''
        cls.formatter = Formatter({'C':C})
        
        cls.formatter.process_variables(os.path.join('data','spec.json'))

        # store the attirutes as a dict -> simpler to store
        cls._data = cls.formatter.get_variables()

        for name, value in cls._data.items():
            setattr(cls, name, value)
        
        # load json data
        with open(os.path.join("data","data.json"), 'r') as file:
            cls.JSON_DATA = json.load(file)

    @classmethod
    def set_json_variable(cls, name: str, value, update_json=True):
        '''
        Set the value of one of the json data's variables,  
        if update_json=True, update the `data.json` file.
        '''
        cls.JSON_DATA[name] = value

        if update_json:
            with open(os.path.join('data','data.json'), 'w') as file:
                json.dump(cls.JSON_DATA, file, indent=4)

    @classmethod
    def set_attribute(cls, name: str, value, update_json=True):
        '''
        Set the value of one of the attribute,  
        if update_json=True, update the `spec.json` file.
        '''
        setattr(cls, name, value)

        cls._data[name] = value

        if update_json:
            with open(os.path.join('data','spec.json'), 'w') as file:
                json.dump(cls._data, file, indent=4)

    @classmethod
    def is_user_data(cls, username):
        '''
        Return if a user has data stored on local.
        '''
        filename = os.path.join('data','accounts',f'{username}.json')

        return os.path.exists(filename)

    @classmethod
    def load_user_data(cls, username):
        '''
        Load & return the data stored in local of a user.
        '''
        filename = os.path.join('data','accounts',f'{username}.json')

        if not os.path.exists(filename):
            return None

        with open(filename, 'r') as file:
            data = json.load(file)
        
        return data

    @classmethod
    def remove_user_data(cls, username):
        '''
        Remove the .json file of a user
        '''
        filename = os.path.join('data','accounts',f'{username}.json')

        if os.path.exists(filename):
            os.remove(filename)

    @classmethod
    def store_local_profil(cls, username, client):
        '''
        Store the data of the user in local .json file.  
        Set it to be the active account (in data.json).
        '''
        filename = os.path.join('data','accounts',f'{username}.json')
        
        with open(filename, 'w') as file:
            json.dump({
                'username': username,
                "updated": False, # if the local data were modified
                'script status': client.in_data['scst'],
                'ship status': client.in_data['shst'],
                'ship': client.in_data['sh'].tolist(),
                'script': client.in_data['sc'].split('\n')
            }, file, indent=4)
        
        cls.JSON_DATA['current account'] = username

    @classmethod
    def update_local_profil(cls, username, key, value):
        '''
        Update the profil of a user, who must have a .json file otherwise
        the operation is aborted. Only update the given key.
        '''
        filename = os.path.join('data','accounts',f'{username}.json')

        if not os.path.exists(filename):
            return
        
        with open(filename, 'r') as file:
            data = json.load(file)
        
        # mark the data as updated
        data['updated'] = True

        data[key] = value

        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

Spec.load()