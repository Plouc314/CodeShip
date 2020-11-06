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

        self.add_frame_function(self.look_friends, is_active=True)
        self.add_frame_function(self.look_demand_friends, is_active=True)
        self.add_frame_function(self.manage_notif, active_pages=Spec.PAGE_MENU)
        self.add_frame_function(self.look_comm_login, active_pages=Spec.PAGE_CONN)
        self.add_frame_function(self.look_general_chat_msg, active_pages=Spec.PAGE_MENU)
        self.add_frame_function(self.look_rdfr, active_pages=Spec.PAGE_FRIENDS)

    def manage_notif(self):
        '''
        Manage the notif TextBox of page Menu that indicates the number of
        active friend demands.
        '''
        page_fr = self.get_page(Spec.PAGE_FRIENDS)
        page_menu = self.get_page(Spec.PAGE_MENU)
        notif = page_menu.get_component('notif')

        n_dfr  = page_fr.get_n_dfr()

        if n_dfr == 0:
            page_menu.change_display_state('notif', False)
        
        else:
            page_menu.change_display_state('notif', True)
            notif.set_text(str(n_dfr))
        
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

    def look_rdfr(self):
        '''
        Check if the server send a response on a friend demand.
        '''
        with self.client.get_data('rdfr') as content:

            if content == None:
                return
            
            page_fr = self.get_page(Spec.PAGE_FRIENDS)

            page_fr.set_rdfr(content)

    def look_friends(self):
        '''
        Check if the server sent info about friends
        '''
        with self.client.get_data('frs') as contents:

            if contents == None:
                return

            page_fr = self.get_page(Spec.PAGE_FRIENDS)

            for username, connected in contents:
                page_fr.set_friend(username, connected)
    
    def look_demand_friends(self):
        '''
        Check if the server sent a friend demand.
        '''
        with self.client.get_data('dfr') as contents:

            page_fr = self.get_page(Spec.PAGE_FRIENDS)

            for username in contents:
                page_fr.set_demand_friend(username)