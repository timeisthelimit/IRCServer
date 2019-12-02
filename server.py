#!/usr/bin/env python3
# Socket code inspired by and taken from RealPython tutorial
# on sockets (https://realpython.com/python-sockets/)

from messageparser import MessageParser
from client import Client
import serverfunctions as sfn
import socket
import selectors
import time

class Server:
    # dict of channel names to lists of client sockets
    channels = {}

    # dict of nicks to (<client socket>, <Client object>) tuples
    clients = {}

 
mp = MessageParser()
HOST = '127.0.0.1'
PORT = 6667

def accept_connection(server_sock, server):
    conn, addr = server_sock.accept()
    data = Client()
    mask = selectors.EVENT_READ | selectors.EVENT_WRITE
    sock_selector.register(conn, mask, data)
    sfn.serv_log('{} connected!'.format(addr))

    nick_set = user_set = False 
    attemps = 0

    while not nick_set or not user_set:

        # After 5 messages it timesout
        # The socket should take care of an actaul timeout (ms/s)
        if attemps>3: 
            sfn.no_reg(conn, HOST)
            conn.close()
            # close socket
            return

        messages = conn.recv(512).decode().split('\n')
        for m in messages:
            if m != '':
                sfn.irc_log("IN", m)
                prefix, command, params = mp.parseMessage(m)
                if command == "NICK":
                    nick_set = True
                    # checking for nick collision
                    for nick in server.clients:
                        if nick == data.nick:
                            attemps += 1
                            sfn.nick_collision(conn, data, HOST)
                            nick_set = False

                    # Setting nick if no nick collision
                    if nick_set:
                        data.reg_nick(params[0])

                elif command == "USER":
                    data.reg_user(*params)
                    user_set = True 
                else:
                    attemps+=1
    
    # if not nick_set:
        # sfn.no_nick(conn, HOST)

    sfn.confirm_reg(conn, data, HOST)
    sfn.serv_log("User {} has logged in".format(data.username))

    server.clients[data.nick] = {(conn, data)}
    sfn.serv_log("These are all our clients: {}".format(server.clients))

def service_connection(key, mask):
    conn = key.fileobj
    data = key.data

    if data.timestamp+10 < time.time():
        data.update_timestamp()
        
        msg = "PING {}\r\n".format(data.nick)
        sfn.irc_log("OUT",msg.strip())
        conn.sendall(msg.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 6667))
    s.listen()
    s.setblocking(False)

    sock_selector = selectors.DefaultSelector()
    sock_selector.register(s, selectors.EVENT_READ, data=Server())

    while True:
        # Get a list of all sockets which are ready to be written to, read from, or both
        events = sock_selector.select(timeout=None)
        for key, mask in events:
            if type(key.data) is Server:
                accept_connection(key.fileobj, key.data)
            else:
                service_connection(key, mask)



