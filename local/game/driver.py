import pygame
import numpy as np
from game.api import API
from spec import Spec

class Driver:

    def __init__(self, own_ship, opp_ship):

        API.set_ship(own_ship)
        API.set_opponent_ship(opp_ship)
 
    def load_script(self):
        '''
        Load the user script
        '''
        try:
            from script import main
            self.main = main
        except:
            return False

        return True

    def run(self):
        self.main()
        