from lib.plougame import Interface, SubPage, TextBox, ScrollList, InputText, Button, Font, C
from data.spec import Spec
import numpy as np

### MESSAGE ###
DIM_USER = np.array([250,60], dtype='int16')
DIM_MSG = np.array([750,40], dtype='int16')
MSG_Y = 10

### CHAT ###
DIM_SEND = np.array([200, 60], dtype='int16')
DIM_INPUT = np.array([800, 60], dtype='int16')

DIM_SCROLL = (
    Spec.DIM_CHAT[0],
    Spec.DIM_CHAT[1] - DIM_INPUT[1]
)

class Chat(SubPage):

    def __init__(self, pos, general_chat=True, client=None, target=None):
        
        self.MAX_MSG = Spec.CHAT_MAX_MSG

        self.is_general_chat = general_chat
        self.target = target
        self.client = client

        # create components
        scroll = ScrollList(DIM_SCROLL, (0,0), [])

        input_msg = InputText(DIM_INPUT, (0, DIM_SCROLL[1]), 
                        pretext="Write message...", font=Font.f(30))

        button_send = Button(DIM_SEND, (DIM_INPUT[0], DIM_SCROLL[1]), 
                        color=C.LIGHT_BLUE, text='Send', font=Font.f(30))

        components = (
            ('scroll', scroll),
            ('i msg', input_msg),
            ('b send', button_send)
        )

        super().__init__(['base'], components, pos, active_states='all')

        self.add_button_logic('b send', self.on_send)

    def reset(self):
        '''Reset chat'''
        scroll = self.get_component('scroll')

        scroll.clear()

    def on_send(self):
        '''
        Send a message, display it.
        '''
        msg = self.get_text('i msg')

        # check that there is a msg
        if msg == '':
            return

        if self.is_general_chat:
            self.client.send_general_chat_msg(msg)
        else:
            self.client.send_private_chat_msg(self.target, msg)

        self.add_msg(self.client.username, msg)

        self.get_component('i msg').reset_text()

    def add_msg(self, username, msg):
        '''
        Add a message on the ui (`Message` object).
        '''
        if username == self.client.username:
            user_color = C.DARK_GREEN
        else:
            user_color = C.DARK_PURPLE

        scroll = self.get_component('scroll')

        scroll.add_line(self._create_msg(username, msg, user_color))
        scroll.set_cursor_place(down=True)

        # check if there is to many message
        if len(scroll) > self.MAX_MSG:
            # remove oldest msg
            scroll.remove_line(0)
    
    def _create_msg(self, username, msg, user_color):
        '''
        Create the TextBoxs that composed a message (ui),
        return two elements to be use with `ScrollList.add_line`.
        '''
        text_username = TextBox(DIM_USER, (10,0), font=Font.f(40),
                            text=username, text_color=user_color, centered=False)
        
        text_msg = TextBox(DIM_MSG, (DIM_USER[0], MSG_Y), font=Font.f(30),
                            text=msg, centered=False)

        return [text_username, text_msg]
    
    def get_messages(self):
        '''
        Return all the messages of the chat,  
        in format `list`: `{username, message}`
        '''
        scroll = self.get_component('scroll')
        msgs = []

        for i in range(len(scroll)):

            line = scroll.get_line(i)

            username = line[0].get_text()
            msg = line[1].get_text()

            msgs.append({'username':username, 'message':msg})
        
        return msgs