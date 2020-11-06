import socket, threading, time
from tcp.server import Server
from db.db import DataBase
from spec import Spec

server = Server()
DataBase.load()


try:
    server.run()
except KeyboardInterrupt:
    DataBase.store()