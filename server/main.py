import socket, threading, time
from udp import ServerUDP, ClientUDP

PORT = 5050

server = ServerUDP(PORT)

clients = []

class Client(ClientUDP):

    def __init__(self, addr):
        super().__init__(addr)

    def on_message(self, msg):
        print("MESSAGE:", msg)
        self.send("Hello you")

def on_connection(addr):
    client = Client(addr)
    clients.append(client)

server.on_connection = on_connection

server.run()

