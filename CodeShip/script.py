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

