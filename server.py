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

    def reg_nick(self, nick):
        self.nick = nick

    def reg_user(self, username, hostname, servername, realname):
        self.username = username
        self.hostname = hostname
        self.servername = servername 
        self.realname = realname
        

HOST = '127.0.0.1'
PORT = 6667

def serv_log(text):
    print("[Server] {}".format(text))

def irc_log(t, text):
    print("[{0}] {1}".format(t,text))

def confirm_reg(conn, data):
    msg = ":{0} 001 {1} :Hi welcome to this IRC server \r\n".format(HOST, data.nick) 
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 002 {1} :Your host is {0} IRC server made as an assignment\r\n".format(HOST,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 003 {1} :This server was created sometime\r\n".format(HOST,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 004 {1} {0} assignment_server 0 0\r\n".format(HOST,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

def accept_connection(server_sock):
    conn, addr = server_sock.accept()

    mask = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = Client()
    sock_selector.register(conn, mask, data)

    serv_log('{} connected!'.format(addr))

    mp = MessageParser()
    nick = user = True 
    while nick or user:
        messages = conn.recv(512).decode().split('\n')
        for m in messages:
            if m != '':
                irc_log("IN", m)
                prefix, command, params = mp.parseMessage(m)
                if command == "NICK":
                    data.reg_nick(params[0])
                    nick = False
                if command == "USER":
                    data.reg_user(*params)
                    user = False 
    confirm_reg(conn, data)
    serv_log("User {} has logged in".format(data.username))
   
    
def service_connection(key, mask):
    conn = key.fileobj
    data = key.data

    if data.timestamp+10 < time.time():
        data.update_timestamp()
        
        msg = "PING {}\r\n".format(data.nick)
        irc_log("OUT",msg.strip())
        conn.sendall(msg.encode())

    

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



