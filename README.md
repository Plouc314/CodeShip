# CodeShip

## Installation

> 1. **Download the files**  
   Use this [link](https://downgit.github.io/#/home?url=https://github.com/Plouc314/CodeShip/tree/master/CodeShip).

> 2. **Install the necessary python modules**  
    Open a terminal, go to the CodeShip folder and 
    type `$ pip3 install -r requirements.txt`,  
    depending on your python version, you might need to type
    `pip` instead of `pip3`.

> 3. **Launch the game**  
    To launch the game you can either create a shortcut on your desktop or use a terminal, in that case, go to the CodeShip folder and type `$ python3 main.py`, depending on your python version, you might need to type
    `python` instead of `python3`.

## Script
> **Principle**  
The script is a piece of code wrote by each player to run his ship. It is written inside of the script.py file (/CodeShip/script.py). The script is consist of two parts:  
> 1. **Initialisation**  
    The first part is the `init` function, it is here that the player set up all the elements of his script & ship. The function is executed once at the beginning of the game.
> 2. **Main**  
    The second part is the `main` function, it here that the player write is actual script that will decide the behaviour of the ship during the game. The function is executed at each frame.

> **Analyse**  
Once written, the script must be analysed to prevent any errors. To do so, go to the page "Editor", and click on the "Analyse" button, it will tell you if the script contains any error and if so will give you the error traceback. If your script is error-free, click on the "Save" button and a "Ready" icon should appear, you're ready to go! 

> **API**  
The API is composed of two main parts, the ships and the blocks. With them, you should be able to establish a series of orders that would cause the ship to evolve as desired. Each order given will have a little delay before be executed, to avoid having the ship literally changing 30 times a second. 
> 1. **Ship**  
    There are two "ship" object, `Ship`, for your ship, and `Opponent`, for the opponent ship.
    These objects can gives information about their ship, for example: `get_speed`, `get_position`, `get_acceleration`...  
    `Ship` has also a few methods to directly control it, like: `rotate_target`, `rotate_angle` or `set_power_engines`
> 2. **Blocks**  
    There is one block object for every type of block (`Block`, `Generator`, `Engine`, `Shield`, `Turret`). You can obtain the references of theses blocks by calling the `get_blocks` of one of the ship object. You can give orders to the blocks by calling one of their methods, for example: `activate`, `deactivate`, `rotate` (Turret), `set_power_level` (Engine)...  

``` python
'''
Example of script
'''
# Import API
# Note: importing the block objects (Block, Engine, ...) is useless for
# the script but can be very handy to have a look at the documentation
from game.api import Ship, Opponent, Block, Engine, Generator, Shield, Turret, Constants

# Define init function
# It will be executed once at the start of the game
# You can set up any element of your ship here
def init():

    # Get the first shield block
    shield = Ship.get_blocks('Shield')[0]
    # Get the turret blocks
    turrets = Ship.get_blocks('Turret')

    # Add two turret blocks to be protected by the shield
    shield.add_block(turrets[0])
    shield.add_block(turrets[1])

    # Set the intensity of the shield
    # It will define the amound of delivered shield hitpoints
    # and its power consumption.
    shield.set_intensity(2)

    # Order the ship to perform a turn of 45° clockwise
    # This will result in the ship starting to turn at the beginning of the game
    Ship.rotate_angle(45)

# Define main function
def main():

    # Test if the speed of the ship if lower than 20,
    # to do it, use a getter (get_speed) and specify to get
    # a scalar value (else it returns a 2D vector)
    if Ship.get_speed(scalar=True) < 20:

        # Switches the engines to full throttle.
        Ship.set_power_engines(1)

    # Get the reference of one of the Shield blocks of the ship
    shield = Ship.get_blocks("Shield")[0]

    # Get the references of the Engine blocks of the ship
    engines = Ship.get_blocks("Engine")

    # For each engine, test if it has less than 80 hitpoints, 
    # if it's the case, set the engine to be protected by the shield
    for engine in engines:
        if engine.get_hp() < 80:
            shield.add_block(engine)

```
