import socket, threading, time
from tcp.server import Server
from db.db import DataBase
from spec import Spec

server = Server()
DataBase.load()


server.run()
