from lib.plougame import Application
from ui.connection import Connection
from ui.menu import Menu
from ui.friends import Friends
from spec import Spec


class App(Application):

    def __init__(self, client):

        self.client = client
        self.username = None

        pages = [
            (Spec.PAGE_MENU, Menu(client)),
            (Spec.PAGE_CONN, Connection(client)),
            (Spec.PAGE_FRIENDS, Friends(client))
        ]

        super().__init__(pages)

        self.add_frame_function(self.look_friends)

        self.add_frame_function(self.look_comm_login)

        self.set_in_page_func(Spec.PAGE_CONN, self.in_conn)
        self.set_out_page_func(Spec.PAGE_CONN, self.out_conn)

        self.add_frame_function(self.look_general_chat_msg)

        self.set_in_page_func(Spec.PAGE_MENU, self.in_menu)
        self.set_out_page_func(Spec.PAGE_MENU, self.out_menu)

    def out_menu(self):
        ''' Stop the execution of look_general_chat_msg'''
        self.set_frame_function_state(self.look_general_chat_msg, False)

    def in_menu(self):
        '''Start the execution of look_general_chat_msg'''
        self.set_frame_function_state(self.look_general_chat_msg, True)

    def out_conn(self):
        '''Stop the execution of look_comm_login'''
        self.set_frame_function_state(self.look_comm_login, False)
    
    def in_conn(self):
        '''Start the execution of look_comm_login'''
        self.set_frame_function_state(self.look_comm_login, True)

    def look_comm_login(self):
        '''
        Check if the server sent a login response
        '''
        # look for login/signup response
        with self.client.get_data(['rlg', 'rsg']) as (rlg, rsg):

            if rlg == 1 or rsg == 1:
                # get username
                self.username = self.get_page(Spec.PAGE_CONN).username

                # set username attr in menu, chat
                menu = self.get_page(Spec.PAGE_MENU)
                
                menu.username = self.username
                menu.get_component('chat').username = self.username
                
                self.change_page(Spec.PAGE_MENU, state='logged')

            elif rlg == 0 or rsg == 0:
                # set error msg
                conn = self.get_page(Spec.PAGE_CONN)

                conn.set_negative_response()

    def look_general_chat_msg(self):
        '''
        Check if the server sent a message on the general chat.
        '''
        with self.client.get_data('gc') as contents:

            menu = self.get_page(Spec.PAGE_MENU)
                
            chat = menu.get_component('chat')

            for username, msg in contents:
                chat.add_msg(username, msg)

    def look_friends(self):
        '''
        Check if the server sent info about friends
        '''
        with self.client.get_data('frs') as contents:

            if contents == None:
                return

            page_fr = self.get_page(Spec.PAGE_FRIENDS)

            for username, connected in contents:
                page_fr.add_friend(username, connected)