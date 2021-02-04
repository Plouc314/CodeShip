import pygame
from lib.plougame import Page, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from ui.script_analyser import ScriptAnalyser
from ui.ship_editor import ShipEditor
from data.spec import Spec
import numpy as np

### Components ###

Y_TB = 100
X_TB1 = 100

POS_SHIP_EDITOR = np.array([300, 400])
POS_SCRIPT = np.array([1920, 400])

### base ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Editor", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, (X_TB1, Y_TB), color=C.LIGHT_BLUE,
                text="Back", font=Font.f(35))

script_analyser = ScriptAnalyser(POS_SCRIPT)
ship_editor = ShipEditor(POS_SHIP_EDITOR)

states = ['base']

components = [
    ('title', title),
    ('b back', button_back),
    ('script analyser', script_analyser),
    ('ship editor', ship_editor)
]

class Editor(Page):
    
    def __init__(self, client):

        self.client = client
        script_analyser.client = client
        ship_editor.client = client

        super().__init__(states, components, active_states='all')

        self.add_button_logic('b back', self.go_back)
        self.set_in_state_func('base', self.in_base)

    
    def in_base(self):
        '''
        Execute components' in_base method.
        '''
        # reset script analyser
        self.get_component('script analyser').in_base()
        self.get_component('ship editor').in_base()
