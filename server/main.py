from multiprocessing import Queue, Process
from tcp.server import Server as TCPServer
from udp.server import Server as UDPServer
from db.db import DataBase
from spec import Spec

queue = Queue()

server_udp = UDPServer()
server_tcp = TCPServer(queue)

DataBase.load()

p = Process(target=server_udp.run, args=[queue])
p.start()


try:
    server_tcp.run()

except KeyboardInterrupt:
    print('\nStore database...\n')
    DataBase.store()