from lib.plougame import Application
from ui.connection import Connection
from ui.menu import Menu
from spec import Spec


class App(Application):

    def __init__(self, client):

        self.client = client
        self.username = None

        pages = [
            (Spec.PAGE_MENU, Menu(client)),
            (Spec.PAGE_CONN, Connection(client))
        ]

        super().__init__(pages)

        self.add_frame_function(self.look_comm_login)
        
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


