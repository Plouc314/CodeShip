from lib.plougame import Interface, Page, TextBox, ScrollList, InputText, Button, Font, C
from spec import Spec
import numpy as np

### TOP BAR ###

Y_TB = 100
X_TB1 = 100

POS_SCR = (500, 300)
DIM_SCR = (1200, 600)

POS_BACK = np.array([100,100], dtype='int16')

### Components ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                text="Friends", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                text="Back", font=Font.f(30))

button_add_fr = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                text="Add friend", font=Font.f(30))

scroll_frs = ScrollList(DIM_SCR, POS_SCR, [])

states = ['base']

components = [
    ('title', title),
    ('b back', button_back),
    ('b add fr', button_add_fr),
    ('s frs', scroll_frs)
]

class Friends(Page):

    def __init__(self, client):

        self.client = client

        super().__init__(states, components)

        self.set_states_components(None, ['title', 'b back'])
        self.set_states_components('base', ['b add fr', 's frs'])
    
        self.add_button_logic('b add fr', self.add_friend)
        self.add_button_logic('b back', self.back)

    def back(self):
        # go back of one state
        print("BACK")
        self.go_back()
    
    def add_friend(self):
        pass