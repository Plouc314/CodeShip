from lib.plougame import Interface, Page, TextBox, InputText, Button, Font, C
from data.spec import Spec
import numpy as np

### base ###

X_BUTTON = Spec.CENTER_X - Spec.DIM_BIG_BUTTON[0]//2
POS_LOG = np.array([X_BUTTON,600])
POS_SIGN = np.array([X_BUTTON,800])

### login / signup ###

X_SPACE = 50
X_TEXT = Spec.CENTER_X - Spec.DIM_MEDIUM_TEXT[0] - X_SPACE//2

POS_USER = np.array([X_TEXT,600])
POS_PASS = np.array([X_TEXT,800])
POS_INP_USER = np.array([Spec.CENTER_X + X_SPACE//2, 600])
POS_INP_PASS = np.array([Spec.CENTER_X + X_SPACE//2, 800])

POS_DONE = np.array([2200,1200])
POS_BACK = np.array([100,100])

POS_ERROR = np.array([2120,1140]) 

### Components ###

title = TextBox(Spec.DIM_TITLE, Spec.POS_TITLE, 
                            text="Connection", font=Font.f(80))

button_back = Button(Spec.DIM_MEDIUM_BUTTON, POS_BACK, color=C.LIGHT_BLUE,
                    text="Back", font=Font.f(35))

### base ###

button_login = Button(Spec.DIM_BIG_BUTTON, POS_LOG, color=C.LIGHT_BLUE,
                    text="Login", font=Font.f(45))

button_sign_up = Button((Spec.DIM_BIG_BUTTON), POS_SIGN, color=C.LIGHT_BLUE,
                    text="Sign up", font=Font.f(45))

### login / signup ###

text_username = TextBox(Spec.DIM_MEDIUM_TEXT, POS_USER, 
                    text="Username:",font=Font.f(45))

text_password = TextBox(Spec.DIM_MEDIUM_TEXT, POS_PASS, 
                    text="Password:",font=Font.f(45))

input_username = InputText(Spec.DIM_MEDIUM_TEXT, POS_INP_USER, font=Font.f(45))

input_password = InputText(Spec.DIM_MEDIUM_TEXT, POS_INP_PASS, font=Font.f(45), cache=True)

button_done = Button(Spec.DIM_MEDIUM_BUTTON, POS_DONE, color=C.LIGHT_BLUE,
                    text="Done", font=Font.f(35))

text_error = TextBox(None, POS_ERROR, color=C.DARK_RED,
                font=Font.f(30), text_color=C.WHITE, dynamic_dim=True)

states = ['base', 'login', 'signup']

components = [
    ('title', title),
    ('b back', button_back),
    ('b login', button_login),
    ('b signup', button_sign_up),
    ('t username', text_username),
    ('t password', text_password),
    ('i username', input_username),
    ('i password', input_password),
    ('b done', button_done),
    ('t error', text_error)
]

class Connection(Page):

    def __init__(self, client):

        self.client = client

        # store username for when logged
        self.username = None

        super().__init__(states, components)

        self.set_states_components(None, ['title', 'b back'])
        self.set_states_components('base',['b login', 'b signup'])
        self.set_states_components(['login', 'signup'],[
            't username',
            't password',
            'i username',
            'i password',
            'b done'
        ])

        self.add_button_logic('b login', self.login)
        self.add_button_logic('b signup', self.signup)
        self.add_button_logic('b done', self.done)
        self.add_button_logic('b back', self.go_back)

        self.set_in_state_func('base', self.to_base)

    def to_base(self):
        ''' Executed when state pass to base.'''
        self.set_text('title', 'Connection')
        self.change_display_state('t error', False)

    def login(self):
        # go to the login state
        self.change_state('login')
        self.set_text('title', 'Log in')
    
    def signup(self):
        # go to the sign up state
        self.change_state('signup')
        self.set_text('title', 'Sign up')

    def done(self):
        '''
        Send the login information to the server.
        '''

        username = self.get_text('i username')
        password = self.get_text('i password')

        self.username = username

        if self.get_state() == 'login':
            self.client.send_login(username, password)
        else:
            self.client.send_sign_up(username, password)
    
    def set_negative_response(self):
        '''
        When the server return that the log/sign info are incorrect,  
        set an error message.
        '''
        input_username.reset_text()
        input_password.reset_text()

        self.set_text('t error', "The register informations are incorrects.")
        self.change_display_state('t error', True)