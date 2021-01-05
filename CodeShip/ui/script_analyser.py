import pygame
from lib.plougame import SubPage, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from game.game import Game
from data.spec import Spec
import numpy as np
import importlib, traceback, time, functools

DIM_CADRE = np.array([1100, 900])
POS_TITLE = np.array([350, 30])

Y_BAR = 130
X_BAR1 = 20
X_BAR2 = 280
X_BAR3 = 540
X_BAR4 = 800

POS_ERROR = np.array([30, 210])
POS_T_TB = np.array([30, 250])
POS_TB = np.array([0, 310])
DIM_TB = np.array([1100, 590])
DIM_STATUS = np.array([280, 60])

# components

cadre = Cadre(DIM_CADRE, (0,0))

title = TextBox(Spec.DIM_MEDIUM_TEXT, POS_TITLE, marge=True,
                text="Script", font=Font.f(50))

button_analyse = Button(Spec.DIM_MEDIUM_BUTTON, (X_BAR1, Y_BAR), 
                color=C.LIGHT_BLUE, text="Analyse", font=Font.f(35))

button_load = Button(Spec.DIM_MEDIUM_BUTTON, (X_BAR2, Y_BAR), 
                color=C.LIGHT_BLUE, text="Load", font=Font.f(35))

button_save = Button(Spec.DIM_MEDIUM_BUTTON, (X_BAR3, Y_BAR), 
                color=C.LIGHT_BLUE, text="Save", font=Font.f(35))

text_status = TextBox(DIM_STATUS, (X_BAR4, Y_BAR),
                font=Font.f(35), text_color=C.WHITE)

text_info = TextBox((0,0), POS_ERROR, dynamic_dim=True,
                font=Font.f(30), text_color=C.WHITE)

title_traceback = TextBox(Spec.DIM_MEDIUM_TEXT, POS_T_TB, 
                text="Traceback", font=Font.f(35), centered=False)

text_traceback = TextBox(DIM_TB, POS_TB, 
                font=Font.f(30), marge=True, continuous_text=True)

components = [
    ('cadre', cadre),
    ('title', title),
    ('b analyse', button_analyse),
    ('b load', button_load),
    ('b save', button_save),
    ('t status', text_status),
    ('title tb', title_traceback),
    ('t tb', text_traceback),
    ('t info', text_info)
]

states = ['base']

class ScriptAnalyser(SubPage):

    def __init__(self, pos):

        super().__init__(states, components, pos)

        self.client = None
        self.n_tb_lines = 12
        self.script_status = False

        # create game object -> test script
        self.game = Game(None, connected=False)
        self.grid = None

        # store script module -> know if need to load or reload module
        self.script_module = None

        self.set_states_components(None, ['cadre', 'title', 'b analyse', 'b load', 'b save', 't status'])
    
        self.add_button_logic('b analyse', self.b_analyse)
        self.add_button_logic('b save', self.b_save)
        self.add_button_logic('b load', self.b_load)

    def in_base(self):
        '''
        Set the script status,  
        Reset texts
        '''
        self.reset()

        # don't use context manager -> keep status stored for menu
        status = self.client.in_data['scst']

        if status != None:
            self.script_status = bool(status)

        self.set_status_text()

    def b_save(self):
        '''Send script to server, set info text'''
        
        # get script
        with open('script.py', 'r') as file:
            script = file.read()

        self.client.send_script(script)
        self.client.send_script_status(self.script_status)
        self.set_status_text()

        # set info text
        self.change_display_state('t info', True)
        self.set_text('t info', "Script saved.")
        self.set_color('t info', C.DARK_GREEN)

    def b_load(self):
        '''
        Load the server script into the script.py file
        '''
        script = self.client.in_data['sc']

        with open('script.py', 'w') as file:
            file.write(script)

        # set info text
        self.change_display_state('t info', True)
        self.set_text('t info', f"Script loaded into script.py.")
        self.set_color('t info', C.DARK_GREEN)

    def b_analyse(self):

        self.reset()

        success = self.analyse_cheat()
        success &= self.analyse_errors()

        self.script_status = success

        if success:
            self.set_success_text()

    def analyse_cheat(self):
        '''
        Try to find if the script contains a cheating attempt
        '''
        # load script
        with open('script.py', 'r') as file:
            script = file.read()

        self.client.send_script(script, analysis=True)

        # wait for server response
        while True:

            time.sleep(0.1)

            with self.client.get_data('rsca') as response:
                
                if response == None:    
                    continue

                if response == 0:
                    self.set_error_text('cheat')
                
                return bool(response)

    def analyse_errors(self):
        '''
        Try to find errors in script.
        '''
        is_error = False

        # try import script
        try:
            if not self.script_module is None:
                self.script_module = importlib.reload(self.script_module)
            else:
                self.script_module = importlib.import_module('script')
        
        except Exception as e:
            
            is_error = True

            # get traceback
            tb = e.__traceback__
            tb_lines = traceback.extract_tb(tb).format()

            # add last line with error type and message
            tb_lines.append(f'{e.__class__.__name__}: {e}')

        if is_error:
            self.set_error('import', tb_lines)
            return False
        
        # try runtime script
        error_type, tb_lines = self.game.test_script(self.grid, self.script_module)

        if error_type == 'runtime':
            self.set_error('runtime', tb_lines)
            return False

        elif error_type == 'execution time':
            self.set_error_text('execution time')
            return False

        return True

    def set_success_text(self):
        '''
        Set a success message on the "t info" component
        '''
        # stop displaying potential traceback
        self.change_display_state('title tb', False)
        self.change_display_state('t tb', False)

        # set succes message
        self.change_display_state('t info', True)
        self.set_text('t info', "Script passed tests succesfully!")
        self.set_color('t info', C.DARK_GREEN)

    def set_error(self, error_type, tb_lines):
        '''
        Set the error text and traceback text. 
        '''
        self.set_error_text(error_type)
        self.set_traceback_text(tb_lines)

    def set_error_text(self, error_type):
        '''
        Set the text and color of text_error
        '''
        self.change_display_state('t info', True)

        if error_type == 'import':
            msg = "Error occured while importing script."
        
        elif error_type == "runtime":
            msg = "Error occured while testing main()."
        
        elif error_type == 'cheat':
            msg = 'Potential maliscious piece of code detected.'

        elif error_type == 'execution time':
            msg = 'Execution time is too long.'

        self.set_text('t info', msg)
        self.set_color('t info', C.DARK_RED)

    def set_traceback_text(self, tb_lines):
        '''
        Set the text of text_traceback
        '''
        self.change_display_state('title tb', True)
        self.change_display_state('t tb', True)

        # first filter traceback lines
        # get first line that is about script.py
        for i, line in enumerate(tb_lines):
            if 'script.py' in line:
                idx = i
                break
        
        tb_lines = tb_lines[idx:]

        # keep only relative path
        root_path = "/home/alexandre/Documents/python/game/CodeShip/"

        for i in range(len(tb_lines)):
            tb_lines[i] = tb_lines[i].replace(root_path, '')
        
        text = functools.reduce(lambda x,y:x+y, tb_lines)

        self.set_text('t tb', text)
    
    def set_status_text(self):
        '''
        Set the text of text_status depending on the current status
        '''
        if self.script_status:
            self.set_text('t status', 'Ready.')
            self.set_color('t status', C.DARK_GREEN)
        else:
            self.set_text('t status', 'Not ready.')
            self.set_color('t status', C.DARK_RED)
            
    def reset(self):
        '''
        Reset the texts
        '''
        self.change_display_state('t info', False)
        self.change_display_state('t tb', False)
        self.change_display_state('title tb', False)