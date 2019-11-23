#!/usr/bin/env python3
# Socket code inspired by and taken from RealPython tutorial
# on sockets (https://realpython.com/python-sockets/)

import socket
import selectors
import types

HOST = '127.0.0.1'
PORT = 6667

sock_selector = selectors.DefaultSelector()

def accept_connection(client_sock):
    conn, addr = client_sock.accept()
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sock_selector.register(conn, events, data=data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('127.0.0.1', 6667))
    s.listen()
    s.setblocking(False)

    sock_selector.register(s, selectors.EVENT_READ, data=None)

    while True:
        events = sock_selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)



