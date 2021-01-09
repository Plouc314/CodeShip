from game.ship import Ship as BaseShip
from game.block import (Block as BaseBlock, 
                Generator as BaseGenerator, 
                Shield as BaseShield, 
                Turret as BaseTurret)
from game.geometry import get_deg, get_rad
from data.spec import Spec
import numpy as np
from lib.counter import Counter
from typing import List, Set, Dict, Tuple, Union

class API:

    _ships = {'own':None, 'opp':None}

    @classmethod
    def set_ship(cls, ship: BaseShip):
        cls._ships['own'] = ship
        Ship._set_blocks()

    @classmethod
    def set_opponent_ship(cls, ship: BaseShip):
        cls._ships['opp'] = ship
        Opponent._set_blocks()

    @classmethod
    @Counter.add_func
    def run(cls):
        '''
        Update API's ships to keep them synchronize to the real ships.
        '''
        Ship._update_blocks()
        Ship._update_rotation()
        Opponent._update_blocks()

class Constants:
    '''
    Contain various constants used in the game.
    '''
    size_block = Spec.SIZE_BLOCK
    power_consumption = Spec.POWER_CONS
    power_generation = Spec.POWER_ENERGIE
    turret_fire_delay = Spec.TURRET_FIRE_DELAY
    turret_rotation_speed = Spec.TURRET_MAX_SPEED
    bullet_damage = Spec.DAMAGE_BULLET
    bullet_speed = Spec.SPEED_BULLET
    shield_blocks_limit = Spec.SHIELD_MAX_PRTC
    shield_max_intensity = Spec.SHIELD_MAX_INTENSITY
    shield_hp_unit = Spec.SHIELD_HP
    shield_regeneration_rate = Spec.SHIELD_REGEN_RATE

class Block:
    '''
    Block `Block`

    Most basic block, parent object of every other blocks.

    Note
    ---
    Do not create a block in the script as each API object is linked
    to an internal object in the game, so creating a new block would have
    no effect on the behaviour of the ship.

    Methods
    ---
    `activate`: Activate the block (Useless for `Block`)  
    `deactivate`: Deactivate the block (Useless for `Block`)  
    `get_hp`: Return the amound of hitpoints of the block  
    `get_power_output`: Return the power output of the block (power consumption or generation)  
    '''
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

        API._ships[self.team].blocks[self.key].set_activate(True)
    
    def deactivate(self):
        '''Deactivate the block.'''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].set_activate(False)

    def get_hp(self) -> int:
        '''Return the amound of hp of the block.'''
        return API._ships[self.team].blocks[self.key].hp

    def get_power_output(self):
        '''Return the power output of the block.'''
        return API._ships[self.team].blocks[self.key].get_power_output()

    def __repr__(self):
        return f'{self.name} API Object key:{self.key}'

class Generator(Block):
    '''
    Block `Generator`, inherit from `Block`

    Supply power to the ship, value stored in `Constants.power_generation`.
    
    Methods
    ---
    All `Block` methods.
    '''

    name = 'Generator'

    def __init__(self, key, team):
        super().__init__(key, team)

class Shield(Block):
    '''
    Block `Shield`, inherit from `Block`

    Not implemented.
    '''
    name = 'Shield'

    def __init__(self, key, team):
        super().__init__(key, team)

    def set_intensity(self, value: int):
        '''
        Set the intensity of the shield.  
        It will define the power consumption of the shield
        (computed as `intensity` * `Constants.power_consumption`) and
        the amound of hitpoints that the shield can provide (computed as
        `intensity` * `Constants.shield_hp_unit`).
        '''
        API._ships[self.team].blocks[self.key].set_intensity(value)

    def add_block(self, block):
        '''
        Add a block to be protected by the shield.  
        The block will only be added if the limit of the maximum
        number of blocks of the shield is not reached (stored in
        `Constants.shield_blocks_limit`)

        Parameters
        ---
        `block`: Block / child object...  
        One of the API block (of your team...)
        '''
        if block.team != self.team:
            raise ValueError("Trying to add an opponent block to a Shield block.")

        other_block = API._ships[self.team].blocks[block.key]
        API._ships[self.team].blocks[self.key].add_prtc_block(other_block)

    def remove_block(self, block):
        '''
        Remove one of the protected block.

        Parameters
        ---
        `block`: Block / child object...  
        One of the API block (of your team...)
        '''
        other_block = API._ships[block.team].blocks[block.key]
        API._ships[self.team].blocks[self.key].remove_prtc_block(other_block)

class Turret(Block):
    '''
    Block `Turret`, inherit from `Block`

    Block used to cause damage ot the opponent ship, 
    can rotate and fire bullets.  
    Specifications on the bullets can be found in `Constants`.

    Methods
    ---
    All `Block` methods.

    `is_rotating`: Return if the turret is currently rotating.  
    `rotate`: Rotate the turret to a certain angle.  
    `get_orientation`: Return the current orientation of the turret.  
    `fire`: Make the turret fire.  
    '''
    name = 'Turret'

    def __init__(self, key, team):
        super().__init__(key, team)
    
    def is_rotating(self) -> bool:
        '''
        Return if the turret is rotating.
        '''
        return API._ships[self.team].blocks[self.key].is_rotating

    def rotate(self, target_angle: int):
        '''
        Rotate the turret until reaching the target angle.
        The rotation is done at a certain speed.
        Can know if the turret is rotating by calling `is_rotating` method.

        Parameters
        ---
        `target_angle`: int (degree)  
        The angle up to which the turret will rotate.
        '''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].rotate(target_angle)

    def get_orientation(self):
        '''Return the orientation of the turret (degree)'''
        return API._ships[self.team].blocks[self.key].orien

    def fire(self):
        '''
        Make the turret fire.  

        The turret fire with a delay, meaning that it can't fire at each frame,
        the delay is stored in `Constants.turret_fire_delay` (unit: fps).  

        Note: To be able to fire, the turret needs to be activated.  
        '''
        if self.team == 'opp': 
            raise ValueError("Try to give order to opponent ship.")

        API._ships[self.team].blocks[self.key].fire()

class Engine(Block):
    '''
    Block `Engine`, inherit from `Block`

    Block `Engine` provides motor force to the ship,
    making it go forward. It has an intensity of activation
    which affect the power output and the efficiency of the engine.

    Methods
    ---
    All `Block` methods.

    `set_power_engines`: Set the intensity at which the engines is running
    '''
    name = 'Engine'

    def __init__(self, key, team):
        super().__init__(key, team)
    
    def set_power_level(self, value: float):
        '''
        Set the power level of the engine,
        the intensity at which the engine is running.

        Parameters
        ---
        `value`: float  
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
    '''
    `Ship` object.

    The `Ship` object stored all the blocks reference,
    it has methods to give orders to the whole ship and
    various getters that can gives informations about the 
    current ship situation.

    Methods
    ---
    `get_blocks`: Return the blocks of the ships.  
    `set_power_engines`: Set the intensity at which the engines are running
    (same as `Engine.set_power_level` but for the whole ship)  
    `rotate_target`: Rotate the ship until reaching an angle.  
    `rotate_angle`: Rotate the ship of a given angle.  

    Getters: `get_speed`, `get_acceleration`, `get_orientation`, 
    `get_position`, `get_power_level`
    '''
    
    # rotation
    _target_angle = None
    _path_length = None
    _path_f = None
    _inversed = False

    @classmethod
    def _set_blocks(cls):
        '''
        Internal method.  
        Create a API block for each block of the ship.
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
    def _update_blocks(cls):
        '''
        Internal method.  
        Loop through each block of the ship and remove the dead ones.
        '''
        for block in cls.blocks:
            if not block.key in API._ships['own'].blocks.keys():
                # remove block
                cls.blocks.remove(block)
                cls.typed_blocks[block.name].remove(block)

    @classmethod
    def get_blocks(cls, _type : str = None) -> List[Union[Block, Generator, Shield, Turret, Engine]]:
        ''' 
        Return the blocks of the ship.

        Parameters
        ---
        `_type`: str  
        Can specify a type, can be one of those: `Block`, `Generator`, `Engine`, `Shield`, `Turret`.  
        In that case, return all the blocks of the specified type.
        '''
        if _type == None:
            return cls.blocks
        else:
            return cls.typed_blocks[_type]
    
    @classmethod
    def get_block_by_coord(cls, coord: tuple) -> Union[Block, Generator, Shield, Turret, Engine]:
        '''
        Return the block at the given coordinate.

        The system of coordinates is organised as follows:
        (0, 0) corresponds to the top left corner,
        (5, 5) corresponds to the bottom right corner.

        Return `None` if no block is found at the given coordinates.

        Parameters
        ---

        `coord`: tuple[int, int]  
        The coordinate at which the block is placed.
        '''
        return API._ships['own'].get_block_by_coord(coord)

    @classmethod
    def get_speed(cls, scalar=False):
        '''
        Return the speed of the ship.
        
        Parameters
        ------
        `scalar`: bool  
        If False return the vector speed, else return the norm of the vector.
        '''
        return API._ships['own'].get_speed(scalar=scalar)
    
    @classmethod
    def get_acceleration(cls, scalar=False):
        '''
        Return the acceleration of the ship.
        
        Parameters
        ------
        `scalar`: bool  
        If False return the vector acceleration, else return the norm of the vector.
        '''
        return API._ships['own'].get_acc(scalar=scalar)

    @classmethod
    def get_orientation(cls):
        '''
        Return the orientation of the ship (degree).  
        The orientation is an angle, with:
        0° : East  
        90° : South  
        180° : West  
        270° : North
        '''
        return get_deg(API._ship['own'].orien)

    @classmethod
    def get_position(cls):
        '''
        Return the position of the center of the ship.  
        The position coordinates will fall between `[0,0]` (upper left)
        and `[3200,1800]` (bottom right).
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
    def set_power_engines(cls, value: Union[float, list]):
        '''
        Set the power level of the engines,
        the intensity at which the engines are running.
        
        Parameters
        ------
        `value`: float / list  
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

    @classmethod
    def _choose_rotation_path(cls, current_angle):
        '''
        Given the current orientation (deg),
        Choose the shortest path,
        set the lambda to compute it,
        return the circular acceleration.
        '''
        # a is previous angle, b is target angle
        a = current_angle
        b = cls._target_angle

        if a > b:
            b = b + 360 - a
            a = 0

        # counter clockwise
        path1 = b - a
        # clockwise
        path2 = a + (360 - b)

        cls._path_length = max(path1, path2)

        if path1 < path2:
            acc_circular = Spec.MAX_CIRCULAR_ACC
            cls._path_f = lambda x: b - x + (360 - a)
        else:
            acc_circular = -Spec.MAX_CIRCULAR_ACC
            cls._path_f = lambda x: x + (360 - a) + (360 - b)

        return acc_circular

    @classmethod
    def rotate_target(cls, angle: int):
        '''
        Rotate the ship to a target angle.
        The ship will rotate all the way until reaching the target angle.  
        For example, if the orientation of the ship is 277° and the target
        angle 233°, the ship will rotate of 44° counter-clockwise.

        Parameters
        ---
        `angle`: int  
        The target angle in degrees.
        '''

        if cls._target_angle == angle:
            # given angle is already target angle
            return
        
        cls._target_angle = angle
        cls._inversed = False

        # select the smallest path to the angle
        orien = get_deg(API._ships['own'].orien)
        
        acc_circular = cls._choose_rotation_path(orien)
        
        API._ships['own'].circular_acc = acc_circular

    @classmethod
    def rotate_angle(cls, angle: int):
        '''
        Rotate the ship of a given angle.  
        The ship will rotate of the given angle, so if the orientation
        of the ship is 130° and the given angle -21°, the ship will rotate
        of 21° counter-clockwise to reach 119°.

        Parameters
        ---
        `angle`: int  
        The angle of rotation in degrees, positive is clockwise,
        negative is counter-clockwise.
        '''
        orien = get_deg(API._ships['own'].orien)

        target_angle = (orien + angle) % 360

        if cls._target_angle == target_angle:
            # given angle is already target angle
            return
        
        cls.rotate_target(target_angle)

    @classmethod
    def _update_rotation(cls):
        '''
        Internal method.  
        Update rotation, inverse acc in the middle,
        stop rotation on target angle.
        '''
        if cls._target_angle == None:
            return
        
        ship = API._ships['own']
        orien = get_deg(ship.orien)

        # check halfway through -> inv acc
        path_length = cls._path_f(orien)

        if not cls._inversed == False and path_length <= cls._path_length/2:
            # inverse acc
            ship.circular_acc = -ship.circular_acc
            cls._inversed = True

        # check target angle
        if abs(orien - cls._target_angle) <= 1:
            ship.orien = get_rad(cls._target_angle)

            # finish rotation
            ship.circular_acc = 0
            ship.circular_speed = 0
            cls._target_angle = None

class Opponent:
    '''
    `Opponent` object.

    The `Opponent` object is the same as the `Ship` object except
    it doesn't has the methods that give orders.  

    Methods
    ---
    `get_blocks`: Return the blocks of the ships.  
    
    Getters: `get_speed`, `get_acceleration`, `get_orientation`, 
    `get_position`, `get_power_level`
    '''

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
    def _update_blocks(cls):
        '''
        Internal method.  
        Loop through each block of the ship and remove the dead ones.
        '''
        for block in cls.blocks:
            if not block.key in API._ships['opp'].blocks.keys():
                # remove block
                cls.blocks.remove(block)

    @classmethod
    def get_blocks(cls, _type: str = None):
        ''' 
        Return the blocks of the ship.

        Parameters
        ---
        `_type`: str  
        Can specify a type, can be one of those: `Block`, `Generator`, `Engine`, `Shield`, `Turret`.  
        In that case, return all the blocks of the specified type.
        '''
        if _type == None:
            # assign type to blocks -> get doc in script
            values: List[Union[map_block]] = cls.blocks
            return values
        else:
            # assign type to blocks -> get doc in script
            values: List[Union[map_block]] = cls.typed_blocks[_type]
            return values
    
    @classmethod
    def get_block_by_coord(cls, coord: tuple) -> Union[Block, Generator, Shield, Turret, Engine]:
        '''
        Return the block at the given coordinate.

        The system of coordinates is organised as follows:
        (0, 0) corresponds to the top left corner,
        (5, 5) corresponds to the bottom right corner.

        Return `None` if no block is found at the given coordinates.

        Parameters
        ---

        `coord`: tuple[int, int]  
        The coordinate at which the block is placed.
        '''
        return API._ships['opp'].get_block_by_coord(coord)

    @classmethod
    def get_speed(cls, scalar=False):
        '''
        Return the speed of the ship.
        
        Parameters
        ------
        `scalar`: bool  
        If False return the vector speed, else return the norm of the vector.
        '''
        return API._ships['own'].get_speed(scalar=scalar)
    
    @classmethod
    def get_acceleration(cls, scalar=False):
        '''
        Return the acceleration of the ship.
        
        Parameters
        ------
        `scalar`: bool  
        If False return the vector acceleration, else return the norm of the vector.
        '''
        return API._ships['own'].get_acc(scalar=scalar)

    @classmethod
    def get_orientation(cls):
        '''
        Return the orientation of the ship (degree).  
        The orientation is an angle, with:
        0° : East  
        90° : South  
        180° : West  
        270° : North
        '''
        return get_deg(API._ship['opp'].orien)

    @classmethod
    def get_position(cls):
        '''
        Return the position of the center of the ship.  
        The position coordinates will fall between `[0,0]` (upper left)
        and `[3200,1800]` (bottom right).
        '''
        return API._ships['opp'].form.get_center()