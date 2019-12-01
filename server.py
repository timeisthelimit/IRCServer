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
def accept_connection(server_sock, server):
    conn, addr = server_sock.accept()

    # object to store all data on the client
    data = Client()

    # receive and silently ignore 'CAP LS 302' message
    conn.recv(512).decode().split('\n')


    # receive NICK and USER messages
    nick_set = False
    userdata_set = False
    messages = conn.recv(512).decode().split('\n')
    for m in messages:
        if m != '':
            sfn.irc_log("IN", m)
            prefix, command, params = mp.parseMessage(m)
            if command == "NICK":
                try:
                    data.reg_nick(params[0]) # implement raise exception 
                    nick_set = True
                except Exception as e:
                    print(e)
                    # inform the client attempting to connect?
                    return
            if command == "USER":
                try:
                    data.reg_user(*params) # implement raise exception 
                    userdata_set = True
                except Exception as e:
                    print(e)
                    # inform the client attempting to connect?
                    return


    if nick_set == True and userdata_set == True:
        # register new socket with socket selector, and associate it with client data object
        mask = selectors.EVENT_READ | selectors.EVENT_WRITE
        sock_selector.register(conn, mask, data)

        sfn.serv_log('{} connected!'.format(addr))

        sfn.confirm_reg(conn, data, HOST)
        sfn.serv_log("User {} has logged in".format(data.username))
    
        server.clients[data.nick] = {(conn, data)}
        print("These are all our clients:", server.clients)
    else:
        pass #handle registration error here


def service_connection(key, mask):
    conn = key.fileobj
    data = key.data

    if data.timestamp+10 < time.time():
        data.update_timestamp()
        
        msg = "PING {}\r\n".format(data.nick)
        sfn.irc_log("OUT",msg.strip())
        conn.sendall(msg.encode())

    
HOST = '127.0.0.1'
PORT = 6667

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



