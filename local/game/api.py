from game.ship import Ship as BaseShip
from game.block import (Block as BaseBlock, 
                Generator as BaseGenerator, 
                Shield as BaseShield, 
                Turret as BaseTurret)
from spec import Spec

class API:

    @classmethod
    def set_ship(cls, ship):
        cls._ship = ship
        Ship._set_blocks()

    @classmethod
    def set_opponent_ship(cls, ship):
        cls._opponent_ship = ship
        Opponent._set_blocks()

class Block:

    name = 'Block'

    def __init__(self, key, team):
        self.key = key

        if team == 'own':
            self._ship = API._ship
        else:
            self._ship = API._opponent_ship

    def activate(self):
        '''Activate the block.'''
        self._ship.blocks[self.key].is_active = True
    
    def deactivate(self):
        '''Deactivate the block.'''
        self._ship.blocks[self.key].is_active = False

    def get_hp(self):
        '''Return the amound of hp of the block.'''
        return self._ship.blocks[self.key].hp

    def get_power_output(self):
        '''Return the power output of the block.'''
        return self._ship.blocks[self.key].get_power_output()

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
        return self._ship.blocks[self.key].is_rotating

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
        self._ship.blocks[self.key].rotate(target_angle)

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
        self._ship.blocks[self.key].activation_per = value

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

        for key, block in API._ship.blocks.items():
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
        return API._ship.speed
    
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

        if type(value) == float:
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

        for key, block in API._opponent_ship.blocks.items():
            api_block = map_block[block.name](key, 'opp')
            
            cls.blocks.append(api_block)

    @classmethod
    def get_blocks(cls):
        ''' Return all the blocks of the ship.'''
        return cls.blocks
    
    @classmethod
    def get_speed(cls):
        ''' Return the speed of the ship. '''
        return API._opponent_ship.speed