from lib.plougame import Application, TextBox, Font, C
from ui import (Connection,
                Menu,
                Friends,
                Editor,
                Profil,
                Updater,
                Offline)

from data.spec import Spec
import time, numpy as np

class App(Application):

    def __init__(self, client, game):

        self.client = client
        self.game = game
        
        self.username = None
        self.opponent = None

        self.version = TextBox((100, 60), (50, 1700), font=Font.f(30),
                        text_color=C.GREY, text=str(Spec.JSON_DATA['version']))

        pages = [
            (Spec.PAGE_MENU, Menu(client)),
            (Spec.PAGE_CONN, Connection(client)),
            (Spec.PAGE_FRIENDS, Friends(client)),
            (Spec.PAGE_EDITOR, Editor(client)),
            (Spec.PAGE_PROFIL, Profil(client)),
            (Spec.PAGE_OFFLINE, Offline(client))
        ]

        super().__init__(pages)

        self.add_frame_function(self.look_friends, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.look_demand_friends, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.look_game_demands, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.manage_notif, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS])
        self.add_frame_function(self.look_comm_login, active_pages=Spec.PAGE_CONN)
        self.add_frame_function(self.look_general_chat_msg, active_pages=Spec.PAGE_MENU)
        self.add_frame_function(self.look_private_chat_msg, active_pages=[Spec.PAGE_MENU, Spec.PAGE_FRIENDS, Spec.PAGE_PROFIL])
        self.add_frame_function(self.look_rdfr, active_pages=[Spec.PAGE_FRIENDS, Spec.PAGE_PROFIL])
        self.add_frame_function(self.look_rdg, active_pages=[Spec.PAGE_FRIENDS])
        self.add_frame_function(self.look_game_notif, active_pages=None)
        self.add_frame_function(self.look_profil_infos, active_pages=Spec.PAGE_FRIENDS)
        self.add_frame_function(self.manage_updater, active_pages=Spec.PAGE_MENU)

        # set log out logic
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_menu.add_button_logic('b logout', self.logic_logout)

        # set game reference in offline page
        self.get_page(Spec.PAGE_OFFLINE).game = self.game

        # set up updater - start download
        self.updater = self.get_page(Spec.PAGE_MENU).get_component('updater')
        self.updater.load_server_data()

    def manage_updater(self):
        '''
        Manage updater downloadings.
        '''
        self.updater.run()

        # check if game can be launch
        if self.updater.ready:
            # set connection button
            page_menu = self.get_page(Spec.PAGE_MENU)
            page_menu.set_states_components('unlogged', 'b conn')

            # stop run this function, no need to
            self.set_frame_function_state(self.manage_updater, False)

    def manage_notif(self):
        '''
        Manage the notifs of page Menu & page friends that indicates the number of
        active friend demands and unread messages.
        '''
        page_fr = self.get_page(Spec.PAGE_FRIENDS)
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_profil = self.get_page(Spec.PAGE_PROFIL)
        
        # update friends page notifs
        page_fr.update_notifs(page_profil.unreads)

        notif = page_menu.get_component('notif')

        n_notif = page_fr.get_n_requests()
        n_notif += page_profil.get_n_unreads()

        if n_notif == 0:
            page_menu.change_display_state('notif', False)
        
        else:
            page_menu.change_display_state('notif', True)
            notif.set_text(str(n_notif))

    def logic_logout(self):
        '''
        Function executed when button logout is pushed.
        '''
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_fr = self.get_page(Spec.PAGE_FRIENDS)
        page_conn = self.get_page(Spec.PAGE_CONN)
        page_profil = self.get_page(Spec.PAGE_PROFIL)

        self.client.send_logout()

        # store user infos on local
        Spec.store_local_profil(self.username, self.client)
        Spec.set_json_variable('active account', self.username)

        # stop game client
        self.game.game_client.stop()
        
        page_conn.change_state('base')
        page_menu.change_state('unlogged')
        page_menu.get_component('chat').reset()
        page_fr.reset()
        page_profil.reset()     

    def look_comm_login(self):
        '''
        Check if the server sent a login response
        '''
        # look for login/signup response
        with self.client.get_data(['rlg', 'rsg']) as (rlg, rsg):

            if rlg == 1 or rsg == 1:
                
                # activate game client
                self.game.start_udp()
                
                # get username
                self.username = self.get_page(Spec.PAGE_CONN).username

                # set username attr in client
                self.client.username = self.username

                self.change_page(Spec.PAGE_MENU, state='logged')

                # manage profil infos on local
                self.get_page(Spec.PAGE_MENU).check_user_data()

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

    def look_private_chat_msg(self):
        '''
        Check if the server sent a message on the private chat.
        '''
        with self.client.get_data('pc') as contents:

            profil = self.get_page(Spec.PAGE_PROFIL)

            for username, msg in contents:
                profil.add_message(username, msg)

    def look_rdfr(self):
        '''
        Check if the server send a response on a friend demand.
        '''
        with self.client.get_data('rdfr') as content:

            if content == None:
                return

            page = self.get_active_page()
            # check that page has set_rdfr method
            if hasattr(page, 'set_rdfr'):
                page.set_rdfr(content)

    def look_rdg(self):
        '''
        Check if the server send a response on a friend demand.
        '''
        with self.client.get_data('rdg') as content:

            if content == None:
                return

            page = self.get_active_page()
            # check that page has set_rdg method
            if hasattr(page, 'set_rdg'):
                page.set_rdg(content)

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
    
    def look_game_demands(self):
        '''
        Check if the server sent a game demand.
        '''
        with self.client.get_data('dg') as contents:

            page_fr = self.get_page(Spec.PAGE_FRIENDS)

            for username in contents:
                page_fr.set_game_demand(username)

    def look_game_notif(self):
        '''
        Check if the user is entering in a game
        '''
        # look for notification
        with self.client.get_data('ign') as contents:

            if contents == None:
                return
            
            username, team = contents
            self.in_game = True
            self.opponent = username
        
        # wait to be sure to receive every info
        time.sleep(.1)

        # if notified -> get opp's grid
        with self.client.get_data('igsh') as grid:

            opp_grid = grid
        
        own_grid = self.client.in_data['sh']
        
        # load & store script
        script = self.client.in_data['sc']

        with open('script.py', 'w') as file:
            file.write(script)
        
        # set game
        self.game.setup(int(team), own_grid, opp_grid, self.username, self.opponent)
    
        # go to the menu
        self.change_page(Spec.PAGE_MENU)

        # set menu's play button to normal state
        page_menu = self.get_page(Spec.PAGE_MENU)
        page_menu.reset_play()

    def look_profil_infos(self):
        '''
        Check if receiving profil data.
        '''

        with self.client.get_data('rpd') as content:

            if content == None:
                return
            
            page_profil = self.get_page(Spec.PAGE_PROFIL)

            page_profil.setup_page(**content)

            self.change_page(Spec.PAGE_PROFIL)

    def display(self):
        self.version.display()
        super().display()