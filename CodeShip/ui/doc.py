from lib.plougame import SubPage, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from data.spec import Spec
import numpy as np

# number of subjects in documentation
N_PART = 8

DIM_CADRE = np.array([1400, 1260])
DIM_DESC = np.array([1300, 1000])
DIM_TITLE_DESC = np.array([1200, 100])

dx = DIM_CADRE[0] // N_PART

DIM_BUTT = np.array([dx, 60])

X1 = np.array([0, 0])
X2 = np.array([1 * dx, 0])
X3 = np.array([2 * dx, 0])
X4 = np.array([3 * dx, 0])
X5 = np.array([4 * dx, 0])
X6 = np.array([5 * dx, 0])
X7 = np.array([6 * dx, 0])
X8 = np.array([7 * dx, 0])

POS_TITLE = np.array([100,80])
POS_DESC = np.array([50,200])

# components

cadre = Cadre(DIM_CADRE, (0,0))

title_desc = TextBox(DIM_TITLE_DESC, POS_TITLE, text='General', font=Font.f(65))

text_desc = TextBox(DIM_DESC, POS_DESC, text=Spec.JSON_DATA['doc']['general'],
            font=Font.f(35), centered=False, continuous_text=True)

button_general = Button(DIM_BUTT, X1, color=C.XLIGHT_GREY, font=Font.f(35),
            text='General')

button_ship = Button(DIM_BUTT, X2, color=C.XLIGHT_GREY, font=Font.f(35),
            text='Ship')

button_script = Button(DIM_BUTT, X3, color=C.XLIGHT_GREY, font=Font.f(35),
            text='Script')

components = [
    ('cadre', cadre),
    ('title desc', title_desc),
    ('t desc', text_desc),
    ('b general', button_general),
    ('b ship', button_ship),
    ('b script', button_script),
]

states = ['base']

class Doc(SubPage):

    def __init__(self, pos):

        super().__init__(states, components, pos, active_states='all')

        self.add_button_logic('b general', self._get_logic('b general'))
        self.add_button_logic('b ship', self._get_logic('b ship'))
        self.add_button_logic('b script', self._get_logic('b script'))

    def _get_logic(self, name: str):
        '''
        Get logic of doc buttons
        '''
        # get rid of "b " in "b subj"
        subject = name[2:]

        title = subject[0].upper() + subject[1:]

        def logic():

            self.set_text('title desc', title)
            self.set_text('t desc', Spec.JSON_DATA['doc'][subject])
        
        return logic