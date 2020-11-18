from game.ship import Ship as BaseShip
from game.block import (Block as BaseBlock, 
                Generator as BaseGenerator, 
                Shield as BaseShield, 
                Turret as BaseTurret)
from spec import Spec

class API:

    _ships = {'own':None, 'opp':None}

    @classmethod
    def set_ship(cls, ship):
        cls._ships['own'] = ship
        Ship._set_blocks()

    @classmethod
    def set_opponent_ship(cls, ship):
        cls._ships['opp'] = ship
        Opponent._set_blocks()

class Block:

    name = 'Block'

    def __init__(self, key, team):
        self.key = key

        if team in API._ships.keys():
            self.team = team
        else:
            raise KeyError

    def activate(self):
        '''Activate the block.'''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].is_active = True
    
    def deactivate(self):
        '''Deactivate the block.'''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].is_active = False

    def get_hp(self):
        '''Return the amound of hp of the block.'''
        return API._ships[self.team].blocks[self.key].hp

    def get_power_output(self):
        '''Return the power output of the block.'''
        return API._ships[self.team].blocks[self.key].get_power_output()

    def __repr__(self):
        return f'{self.name} API Object key:{self.key}'

class Generator(Block):

    name = 'Generator'

    def __init__(self, key, team):
        super().__init__(key, team)

class Shield(Block):

    name = 'Shield'

    def __init__(self, key, team):
        super().__init__(key, team)

class Turret(Block):

    name = 'Turret'

    def __init__(self, key, team):
        super().__init__(key, team)
    
    def is_rotating(self):
        '''
        Return if the turret is rotating.
        '''
        return API._ships[self.team].blocks[self.key].is_rotating

    def rotate(self, target_angle: int):
        '''
        Rotate the turret until reaching the target angle.
        The rotation is done at a certain speed.
        Can know if the turret is rotating calling `is_rotating` method.

        Parameters
        ------
        `target_angle: int (degree)`  
        The angle up to which the turret will rotate.
        '''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].rotate(target_angle)

class Engine(Block):

    name = 'Engine'

    def __init__(self, key, team):
        super().__init__(key, team)
    
    def set_power_level(self, value: float):
        '''
        Set the power level of the engine.

        Parameters
        ------
        `value: float`  
        The intensity of the engine, between 0 and 1.
        '''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")
        
        API._ships[self.team].blocks[self.key].activation_per = value

map_block = {
    'Block':Block, 
    'Generator':Generator, 
    'Shield':Shield, 
    'Turret':Turret, 
    'Engine': Engine
}

class Ship:

    @classmethod
    def _set_blocks(cls):
        '''
        Create a API block for each block of the ship
        '''
        cls.blocks = []
        cls.typed_blocks = {
            'Block':[], 
            'Generator':[], 
            'Engine':[], 
            'Shield':[], 
            'Turret':[]
        }

        for key, block in API._ships['own'].blocks.items():
            api_block = map_block[block.name](key, 'own')
            
            cls.blocks.append(api_block)
            cls.typed_blocks[block.name].append(api_block)

    @classmethod
    def get_blocks(cls, type:str=None):
        ''' 
        Return the blocks of the ship.

        Parameters
        ------
        `type: str`    
        Can specify a type, can be one of those: `Block`, `Generator`, `Engine`, `Shield`, `Turret`.  
        In that case, return all the blocks of the specified type.
        '''
        if type == None:
            return cls.blocks
        else:
            return cls.typed_blocks[type]
    
    @classmethod
    def get_speed(cls):
        ''' Return the speed of the ship. '''
        return API._ships['own'].speed
    
    @classmethod
    def get_position(cls):
        '''
        Return the position of the center of the ship.  
        The position coordinates will fall between `[0,0]` and `[3200,1600]`.
        '''
        return API._ships['own'].form.get_center()

    @classmethod
    def get_power_level(cls):
        '''
        Return the power level of the ship.  
        The power level is the sum of the power output of all the blocks,
        if the power level drops bellow 0, some blocks will randomly be deactivate.  
        To change the power level of a block, call the `activate` or `deactivate` methods of the block.
        '''
        return API._ships['own'].get_power_level()

    @classmethod
    def set_power_engines(cls, value):
        '''
        Set the power level of the engines,  
        
        Parameters
        ------
        `value: float / list`  
        The intensity of the engine, between 0 and 1,
        can be either one value for all engines or one value per engine
        '''
        engines = cls.typed_blocks['Engine']

        if type(value) == float or type(value) == int:
            for engine in engines:
                engine.set_power_level(value)
        
        else:
            if len(value) == len(engines):
                for val, engine in zip(value, engines):
                    engine.set_power_level(val)

class Opponent:

    @classmethod
    def _set_blocks(cls):
        '''
        Create a API block for each block of the ship
        '''
        cls.blocks = []

        for key, block in API._ships['opp'].blocks.items():
            api_block = map_block[block.name](key, 'opp')
            
            cls.blocks.append(api_block)

    @classmethod
    def get_blocks(cls, type:str=None):
        ''' 
        Return the blocks of the ship.

        Parameters
        ------
        `type: str`    
        Can specify a type, can be one of those: `Block`, `Generator`, `Engine`, `Shield`, `Turret`.  
        In that case, return all the blocks of the specified type.
        '''
        if type == None:
            return cls.blocks
        else:
            return cls.typed_blocks[type]
    
    @classmethod
    def get_speed(cls):
        ''' Return the speed of the ship. '''
        return API._ships['opp'].speed
    
    @classmethod
    def get_position(cls):
        '''
        Return the position of the center of the ship.  
        The position coordinates will fall between `[0,0]` and `[3200,1600]`.
        '''
        return API._ships['opp'].form.get_center()