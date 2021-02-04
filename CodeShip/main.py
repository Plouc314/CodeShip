from data.spec import Spec

if not Spec.JSON_DATA['setup']:
    # perform setup instructions
    try:
        import setup
    except:
        print("Setup failed...")

    Spec.set_json_variable('setup', True)

import pygame
from lib.plougame import Interface, C

# first setup the interface -> to create Form objects
Interface.setup((3200,1800), 'CodeShip', background_color=C.WHITE, fullscreen=True)
    #flags=pygame.HWSURFACE|pygame.DOUBLEBUF)

from game.game import Game
from ui.app import App
from comm.uiclient import UIClient
from lib.counter import Counter
import sys

# get addr
if '-a1' in sys.argv:
    ip = Spec.IP_HOST1
elif '-a2' in sys.argv:
    ip = Spec.IP_HOST2
elif '-a3' in sys.argv:
    ip = Spec.IP_HOST3
else:
    ip = Spec.IP_PUBLIC

show_stats = False

if '-s' in sys.argv:
    show_stats = True

client = UIClient((ip, Spec.PORT))
game = Game(client)
app = App(client, game)

Interface.run = Counter.add_func(Interface.run)

while Interface.running:

    pressed, events = Interface.run()

    if not game.running:
        app.react_events(pressed, events)

        app.display()

    else:
        game.run(pressed, events)

if show_stats:
    Counter.print_result()

client.disconnect()
game.game_client.stop()