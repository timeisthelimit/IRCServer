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
    _channels = {}

    # dict of nicks to (<client socket>, <Client object>) tuples
    _clients = {}

    def getClients(self):
        return self._clients

    def addClient(self, nick, client_socket, client_object):
        self._clients[nick] = (client_socket, client_object)

    def deleteClient(self, nick):
        self._clients.pop(nick, None)

    def getChannels(self):
        return self._channels

    def addChannel(self, channel_name, channel_object):
        self._channels[channel_name] = channel_object

    def deleteChannel(self, channel_name):
        self._channels.pop(channel_name, None)


sock_selector = selectors.DefaultSelector()
mp = MessageParser()
server = Server()
HOST = '127.0.0.1'
PORT = 6667


#accept client connection
def accept_connection(server_sock):
    conn, addr = server_sock.accept()
    conn.setblocking(False)

    # object for storing client details
    client = Client()

    nick_set = user_set = False

    # registration attempts
    attemps = 0

    registration_start_time = time.time()
    while not nick_set or not user_set:

        # After 5 messages it timesout
        # The socket should take care of an actaul timeout (ms)
        if attemps>3: 
            sfn.no_reg(conn, HOST)
            conn.close()
            # close socket
            return

        
        if registration_start_time+0.1 < time.time():
            return

        messages=None

        # try to receive from the client socket
        # simply registring the newly accepted socket with our socket
        # and the handling registration in service connection is another option
        # which might have been slightly better
        try:
            messages = conn.recv(512).decode().split('\n')
        except IOError as e:
            if e.errno == socket.EWOULDBLOCK:
                pass
            else:
                sfn.serv_log(str(e))
        except Exception as e:
            sfn.serv_log(str(e))
            return

        if messages is not None:
            for m in messages:
                if m != '':
                    sfn.irc_log("IN", m)
                    prefix, command, params = mp.parseMessage(m)
                    if command == "NICK":
                        if len(params) <1 :
                            sfn.no_nick(conn, HOST)
                        else:
                            client.reg_nick(params[0])
                        
                            if  client.nick in server.getClients().keys():
                                attemps +=1
                                sfn.nick_collision(conn, client, HOST)
                                nick_set = False
                            else:
                                nick_set = True

                    elif command == "USER":
                        client.reg_user(*params)
                        user_set = True 
                    else:
                        attemps+=1
    
    if not nick_set:
        sfn.no_nick(conn, HOST)

    if nick_set and user_set:
        sfn.confirm_reg(conn, client, HOST)
        sfn.serv_log("User {} has logged in".format(client.username))

        server.addClient(client.nick, conn, client)

        mask = selectors.EVENT_READ | selectors.EVENT_WRITE
        sock_selector.register(conn, mask, client)
        sfn.serv_log('{} connected!'.format(addr))

# service client connection
def service_connection(key, mask):
    conn = key.fileobj
    client = key.data

    if mask & selectors.EVENT_WRITE:

        # ping client if they haven't been pinged in the last 10 seconds
        if client.timestamp+10 < time.time():
            client.update_timestamp()
            
            msg = "PING {}\r\n".format(client.nick)
            sfn.irc_log("OUT",msg.strip())
            conn.sendall(msg.encode())
    
    if mask & selectors.EVENT_READ:
        messages = conn.recv(512).decode().split('\n')

        # split messages and queue them in inboud buffer
        for m in messages:
            if m != '':
                sfn.irc_log("IN", m)
                client.inb.append(m)
    
        # pop one message off inbound buffer and handle it
        # using a try block because it is expected that if we are reading
        # then there should be a message ready to be popped,
        # thus empty list means an problem occured somewhere else
        try:
            prefix, command, params = mp.parseMessage(client.inb.pop(0))
        except Exception as e:
            sfn.remove_client(key, sock_selector, server)
            sfn.serv_log(str(e))
            sfn.serv_log("Safely removed client of nick '{}' from server".format(client.nick))
        

        if command == "QUIT":
            sfn.remove_client(key, sock_selector, server)
            return

        # attempt to execute command extrapolated from the message
        # inform server if the command is not in our command_handlers dictionary
        try:
            command_handlers[command](params, server, client, HOST)
        except KeyError as e:
            sfn.serv_log("Unhandled IRC Command:" + str(e))
        except Exception as e:
            sfn.remove_client(key, sock_selector, server)
            sfn.serv_log(str(e))
            sfn.serv_log("Safely removed client of nick '{}' from server".format(client.nick))
            
                
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 6667))
    s.listen()
    s.setblocking(False)

    sock_selector.register(s, selectors.EVENT_READ, data=None)

    while True:
        # Get a list of all sockets which are ready to be written to, read from, or both
        events = sock_selector.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                service_connection(key, mask)



