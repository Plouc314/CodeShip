from ship import Ship as BaseShip
from block import Block as BaseBlock, Energie as BaseEnergie, Shield as BaseShield, Turret as BaseTurret

class API:

    @classmethod
    def set_color(cls, color):
        cls.color = color

    @classmethod
    def set_ship(cls, filename):
        cls.ship = BaseShip.from_file(filename, cls.color)

class Block:

    def __init__(self, key):
        self.key

    def activate(self):
        '''Activate the block.'''
        API.ship.blocks[self.key].is_active = True
    
    def deactivate(self):
        '''Deactivate the block.'''
        API.ship.blocks[self.key].is_active = False

    def get_hp(self):
        '''Return the amound of hp of the block.'''
        return API.ship.blocks[self.key].hp

    def get_power_output(self):
        '''Return the power output of the block.'''
        return API.ship.blocks[self.key].get_power_output()

class Energie(Block):

    def __init__(self, key):
        super().__init__(key)

class Shield(Block):

    def __init__(self, key):
        super().__init__(key)

class Turret(Block):

    def __init__(self, key):
        super().__init__(key)

block_map = {'Block':Block, 'Energie':Energie, 'Shield':Shield, 'Turret':Turret}

class Ship:

    @classmethod
    def _set_blocks(cls):
        '''
        Create a API block for each block of the ship
        '''
        cls.blocks = []

        for key, block in API.ship.blocks.items():
            api_block = map_block[block.name](key)
            
            cls.blocks.append(api_block)

    @classmethod
    def get_blocks(cls):
        ''' Return all the blocks of the ship.'''
        return cls.blocks
    
    @classmethod
    def get_speed(cls):
        ''' Return the speed of the ship. '''
        return API.ship.speed
    
