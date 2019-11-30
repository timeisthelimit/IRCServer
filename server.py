#!/usr/bin/env python3
# Socket code inspired by and taken from RealPython tutorial
# on sockets (https://realpython.com/python-sockets/)

from messageparser import MessageParser
import socket
import selectors
import time

class Client:
    def __init__(self):
        self.timestamp = time.time()

    def update_timestamp(self):
        self.timestamp = time.time()

HOST = '127.0.0.1'
PORT = 6667


def accept_connection(server_sock):
    conn, addr = server_sock.accept()

    mask = selectors.EVENT_READ | selectors.EVENT_WRITE
    sock_selector.register(conn, mask, data=Client())

    print('{} connected!'.format(addr))

    mp = MessageParser()
    print(conn.recv(512).decode())

    messages = conn.recv(512).decode().split('\n')

    for m in messages:
        if m != '':
            prefix, command, params = mp.parseMessage(m)
            print("prefix:", prefix)
            print("command:", command)
            print("params:", params)



def service_connection(key, mask):
    conn = key.fileobj
    data = key.data

    if data.timestamp+10 < time.time():
        data.update_timestamp()
        print(data.timestamp)
        conn.sendall('PING oskar\r\n'.encode())

    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 6667))
    s.listen()
    s.setblocking(False)

    sock_selector = selectors.DefaultSelector()
    sock_selector.register(s, selectors.EVENT_READ, data=None)

    while True:
        # Get a list of all sockets which are ready to be written to, read from, or both
        events = sock_selector.select(timeout=None)

        for key, mask in events:
            if key.data == None:
                accept_connection(key.fileobj)
            else:
                service_connection(key, mask)



