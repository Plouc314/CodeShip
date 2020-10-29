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

        self.add_frame_function(self.look_comm_login)

        self.set_in_page_func(Spec.PAGE_CONN, self.in_conn)
        self.set_out_page_func(Spec.PAGE_CONN, self.out_conn)

    def out_conn(self):
        '''Stop the execution of look_comm_login'''
        self.set_frame_function_state(self.look_comm_login, False)
    
    def in_conn(self):
        '''Start the execution of look_comm_login'''
        self.set_frame_function_state(self.look_comm_login, True)

    def look_comm_login(self):
        '''
        Check if the server send a login response
        '''
        # look for login response
        rlg = self.client.in_data['rlg']

        # look for sign up response
        rsg = self.client.in_data['rsg']

        if rlg or rsg:
            # get username
            self.username = self.get_page(Spec.PAGE_CONN).username

            # set username attr in menu
            self.get_page(Spec.PAGE_MENU).username = self.username

            self.change_page(Spec.PAGE_MENU, state='logged')


