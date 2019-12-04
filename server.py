#!/usr/bin/env python3
# Socket code inspired by and taken from RealPython tutorial
# on sockets (https://realpython.com/python-sockets/)

from messageparser import MessageParser
from client import Client
import serverfunctions as sfn
import socket
import selectors
import time

command_handlers = {'JOIN':sfn.handle_JOIN, 'PRIVMSG':sfn.handle_PRIVMSG}
mp = MessageParser()

class Server:
    # dict of channel names to Channel class object
    channels = {}

    # dict of nicks to (<client socket>, <Client object>) tuples
    clients = {}

mp = MessageParser()
HOST = '127.0.0.1'
PORT = 6667
server = Server()

#accept client connection
def accept_connection(server_sock):
    conn, addr = server_sock.accept()
    data = Client()
    mask = selectors.EVENT_READ | selectors.EVENT_WRITE
    sock_selector.register(conn, mask, data)
    sfn.serv_log('{} connected!'.format(addr))

    nick_set = user_set = False 
    attemps = 0

    while not nick_set or not user_set:

        # After 5 messages it timesout
        # The socket should take care of an actaul timeout (ms)
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
                    data.reg_nick(params[0])
                    if  data.nick in server.clients.keys():
                        attemps +=1
                        sfn.nick_collision(conn, data, HOST)
                        nick_set = False
                    else:
                        nick_set = True

                    # Setting nick if no nick collision
                    #if nick_set:
                    #    data.reg_nick(params[0])

                elif command == "USER":
                    data.reg_user(*params)
                    user_set = True 
                else:
                    attemps+=1
    

    # if not nick_set:
        # sfn.no_nick(conn, HOST)
    
    sfn.confirm_reg(conn, data, HOST)
    sfn.serv_log("User {} has logged in".format(data.username))

    server.clients[data.nick] = (conn, data)
    sfn.serv_log("These are all our clients: {}".format(server.clients))

# service client connection
def service_connection(key, mask):
    conn = key.fileobj
    data = key.data

    if mask & selectors.EVENT_WRITE:

        # ping client if they haven't been pinged in the last 10 seconds
        if data.timestamp+10 < time.time():
            data.update_timestamp()
            
            msg = "PING {}\r\n".format(data.nick)
            sfn.irc_log("OUT",msg.strip())
            conn.sendall(msg.encode())
    
    if mask & selectors.EVENT_READ:
        messages = conn.recv(512).decode().split('\n')

        # split messages and queue them in inboud buffer
        for m in messages:
            if m != '':
                sfn.irc_log("IN", m)
                data.inb.append(m)
    
        # pop one message off inbound buffer
        prefix, command, params = mp.parseMessage(data.inb.pop(0))
        try:
            command_handlers[command](params, server, data, HOST)
        except KeyError as e:
            print("[Server] Unhandled IRC Command:", e)
        

        # if command == "PRIVMSG":
        #     command_handlers['PRIVMSG'](params, server, data, HOST)
        
        # elif command == 'JOIN':
        #     command_handlers['JOIN'](params, server, data, HOST)
            
                
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
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                service_connection(key, mask)



