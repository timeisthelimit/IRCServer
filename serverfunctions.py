from channel import Channel
from messageparser import MessageParser

mp = MessageParser()

def serv_log(text):
    print("[Server] {}".format(text))

def irc_log(t, text):
    print("[{0}] {1}".format(t,text))

def confirm_reg(conn, data, host):
    msg = ":{0} 001 {1} :Hi welcome to this IRC server \r\n".format(host, data.nick) 
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 002 {1} :Your host is {0} IRC server made as an assignment\r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 003 {1} :This server was created sometime\r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 004 {1} {0} assignment_server 0 0\r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip())



def handle_JOIN(params, server, client, HOST):
    # We are using a try catch here on the assumption
    # most of the time people will be joining existing
    # channels rather than creating new ones. So we are
    # assuming that a channel exists, and the excepional
    # case is that it doesn't.

    channel_name = params[0]

    try:
        # if channel exists

        # add associated Channel object and append new nick to its client list
        channel = server.channels[channel_name]
        channel.clients.append(client.nick)

        msg = ":{} JOIN {} * :realname\r\n".format(client.nick, channel_name)
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel topic
        msg = ":{} 332 {} {} {}\r\n".format(HOST, client.nick, channel_name, channel.topic)
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)
        
        # reply to client with channel nick list
        msg = ":{host} 353 {nick} @ {channel_name} :{client_list}\r\n:{host} 366 {nick} {channel_name} :End of /NAMES list\r\n".format(nick=client.nick, host=HOST, channel_name=channel_name, client_list=(' '.join(channel.clients)))
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

    except KeyError:
        # if channel doesn't exist

        # create new Channel object and add to servers channel dictionary
        server.channels[channel_name] = Channel(client.nick, channel_name)

        msg = ":{} JOIN {}\r\n".format(client.nick, channel_name)
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel topic
        msg = ":{} 332 {} {} {}\r\n".format(HOST, client.nick, channel_name, "no topic here")
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel nick list
        msg = ":{host} 353 {nick} @ {channel_name} :{nick}\r\n:{host} 366 {nick} {channel_name} :End of /NAMES list\r\n".format(nick=client.nick, host=HOST, channel_name=channel_name)
        server.clients[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)



def handle_PRIVMSG(params, server, client, HOST):
    messaging_list = mp.parse_csv_list(params[0])
            
    for m in messaging_list:
        if m[0] == '#':
            # if target is channel
            server.channels[m].broadcast(params[1], client.nick, server)
        else:
            # if targer is client
            msg = ":{}!{}@{} PRIVMSG {} :{}\r\n".format(client.nick, client.nick, HOST, m, params[1])
            server.clients[m][0].sendall(msg.encode())
            irc_log("OUT", msg)

def handle_PONG(params, server, client, HOST):
    pass