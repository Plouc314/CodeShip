import pygame
import time
import numpy as np
from lib.plougame import Page, Form, TextBox, Button, InputText, Font, C
from game.api import API
from spec import Spec

### TOP BAR

Y_TB = 100
Y_TB2 = 200

X_TB = 100

POS_TIME = np.array([Spec.CENTER_X-Spec.DIM_MEDIUM_TEXT[0]//2, Y_TB])
POS_CADRE1 = np.array([50,50])
POS_CADRE2 = np.array([2550,50])
DIM_CADRE = np.array([600, 400])

DIM_USER = np.array([600, 80])

### components ###

text_time = TextBox(Spec.DIM_MEDIUM_TEXT, POS_TIME, marge=True, color=C.XLIGHT_GREY)

cadre_1 = Form(DIM_CADRE, POS_CADRE1, marge=True)

text_username1 = TextBox(DIM_USER, POS_CADRE1, text_color=C.WHITE, font=Font.f(60))

cadre_2 = Form(DIM_CADRE, POS_CADRE2, marge=True)

text_username2 = TextBox(DIM_USER, POS_CADRE2, text_color=C.WHITE, font=Font.f(60))

states = ['base']

components = [
    ('t time', text_time),
    ('cadre 1', cadre_1),
    ('t username1', text_username1),
    ('cadre 2', cadre_2),
    ('t username2', text_username2),
]

class GameInterface(Page):

    def __init__(self, client):

        self.start_time = None
        self.client = client

        super().__init__(states, components, active_states='all')

    def start_clock(self):
        '''
        Set the time of the begining of the game
        '''
        self.start_time = time.time()

    def react_events(self, pressed, events):
        
        # update time
        current_time = time.time() - self.start_time
        string = time.strftime("%M:%S", time.gmtime(current_time))
        self.set_text('t time', string)

        super().react_events(pressed, events)

    def set_users(self, user1, user2):
        '''
        Set the two users,  
        user1 should be the one with the position 1 (`Spec.POS_P1`),  
        user2 should be the one with the position 2 (`Spec.POS_P2`)
        '''
        self.set_text('t username1', user1)
        self.set_text('t username2', user2)

        self.set_color('cadre 1', Spec.LCOLOR_P1)
        self.set_color('cadre 2', Spec.LCOLOR_P2)
        self.set_color('t username1', Spec.LCOLOR_P1)
        self.set_color('t username2', Spec.LCOLOR_P2)