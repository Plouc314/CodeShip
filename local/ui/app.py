from lib.plougame import Application
from ui.connection import Connection
from ui.menu import Menu
from ui.friends import Friends
from ui.ship import Ship
from spec import Spec
import time

class App(Application):

    def __init__(self, client, game):

        self.client = client
        self.game = game
        
        self.username = None
        self.in_game = False
        self.opponent = None

        pages = [
            (Spec.PAGE_MENU, Menu(client)),
            (Spec.PAGE_CONN, Connection(client)),
            (Spec.PAGE_FRIENDS, Friends(client)),
            (Spec.PAGE_SHIP, Ship(client))
        ]

        super().__init__(pages)

        self.add_frame_function(self.look_friends, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.look_demand_friends, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.manage_notif, active_pages=Spec.PAGE_MENU)
        self.add_frame_function(self.look_comm_login, active_pages=Spec.PAGE_CONN)
        self.add_frame_function(self.look_general_chat_msg, active_pages=Spec.PAGE_MENU)
        self.add_frame_function(self.look_rdfr, active_pages=Spec.PAGE_FRIENDS)
        self.add_frame_function(self.look_game_notif, active_pages=Spec.PAGE_MENU)

        # set log out logic
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_menu.add_button_logic('b logout', self.logic_logout)

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

    def logic_logout(self):
        '''
        Function executed when button logout is pushed.
        '''
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_fr = self.get_page(Spec.PAGE_FRIENDS)
        page_conn = self.get_page(Spec.PAGE_CONN)

        self.client.send_logout()

        # stop game client
        self.game.game_client.disconnect()
        
        page_conn.change_state('base')
        page_menu.change_state('unlogged')
        page_menu.get_component('chat').reset()
        page_fr.reset()
        
    def look_comm_login(self):
        '''
        Check if the server sent a login response
        '''
        # look for login/signup response
        with self.client.get_data(['rlg', 'rsg']) as (rlg, rsg):

            if rlg == 1 or rsg == 1:
                
                # activate game client
                self.game.game_client.start()
                
                # get username
                self.username = self.get_page(Spec.PAGE_CONN).username

                # set username attr in client
                self.client.username = self.username
                
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
    
    def look_game_notif(self):
        '''
        Check if the user is entering in a game
        '''
        # look for notification
        with self.client.get_data('ign') as contents:

            if contents == None:
                return
            
            username, pos_id = contents
            self.in_game = True
            self.opponent = username
        
        time.sleep(.1)

        # if notified -> get opp's grid
        with self.client.get_data('igsh') as grid:

            opp_grid = grid
        
        with self.client.get_data('sh') as grid:

            own_grid = grid
        
        # load & store script
        script = self.client.in_data['sc']

        with open('script.py', 'w') as file:
            file.write(script)
        
        # set game
        self.in_game = True
        self.game.set_own_id(int(pos_id))
        self.game.create_ships(own_grid, opp_grid)
        self.game.setup_interface(self.username, self.opponent)
        self.game.setup_api()