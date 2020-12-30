import pygame
from lib.plougame import Interface, C

# first setup the interface -> to create Form objects
Interface.setup((3200,1800), 'CodeShip', background_color=C.WHITE, fullscreen=True)

from game.game import Game
from ui.app import App
from comm.uiclient import UIClient
from data.spec import Spec
from lib.counter import Counter
import sys

# get addr
if len(sys.argv) == 1:
    ip = Spec.IP_HOST1
else:
    if sys.argv[1] == '-a1':
        ip = Spec.IP_HOST1
    elif sys.argv[1] == '-a2':
        ip = Spec.IP_HOST2
    elif sys.argv[1] == '-a3':
        ip = Spec.IP_HOST3
    else:
        raise ValueError("Unknown address.")

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

Counter.print_result()

client.disconnect()
game.game_client.disconnect()