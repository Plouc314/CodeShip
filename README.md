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
> **Script**  
The script is a piece of code wrote by each player to run his ship. The script is written inside a `main` function inside the script.py file (/CodeShip/script.py). Once written, the script must be analysed to prevent any errors. To do so, go to the page "Editor", and click on the "Analyse" button, it will tell you if the script contains any error and if so will give you the error traceback. If your script is error-free, click on the "Save" button and a "Ready" icon should appear, you're ready to go! 

> **API**  
The API is composed of two main parts, the ships and the blocks. With them, you should be able to establish a series of orders that would cause the ship to evolve as desired.  
> 1. **Ship**  
    There are two "ship" object, `Ship`, for your ship, and `Opponent`, for the opponent ship.
    These objects can gives information about their ship, for example: `get_speed`, `get_position`, `get_acceleration`...  
> 2. **Block**  
    There is one block object for every type of block (`Block`, `Generator`, `Engine`, `Shield`, `Turret`). You can obtain the references of theses blocks by calling the `get_blocks` of one of the ship object. You can give orders to the blocks by calling one of their methods, for example: `activate`, `deactivate`, `rotate` (Turret), `set_power_level` (Engine)...  

``` python
'''
Example of script
'''
# import API
from game.api import Ship, Opponent, Block, Engine, Generator, Shield, Turret

# define main function
def main():

    if Ship.get_speed() < 20:

        # switches the engines to full throttle.
        Ship.set_power_engines(1)

    # get the references of the Turret blocks of the ship
    turrets = Ship.get_blocks("Turret")

    # order every turrets to fire
    for turret in turrets:
        turret.fire()

```
