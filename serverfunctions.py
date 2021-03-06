import socket
from channel import Channel
from messageparser import MessageParser

mp = MessageParser()

def serv_log(text):
    print("[Server] {}".format(text))

def irc_log(t, text):
    print("[{0}] {1}".format(t,text))

###################
# Server responses#
###################

def confirm_reg(conn, data, host):
    msg = ":{0} 001 {1} :Hi welcome to this IRC server \r\n".format(host, data.nick) 
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 002 {1} :Your host is {0} IRC server made as an assignment \r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 003 {1} :This server was created sometime \r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip()) 

    msg = ":{0} 004 {1} {0} assignment_server 0 0 \r\n".format(host,data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip())

##################
# Error responses#
##################

def no_reg(conn, host):
    msg = ":{0} 451 :You have not registered \r\n".format(host) 
    conn.send(msg.encode())
    irc_log("OUT",msg.strip())

def no_nick(conn, host):
    msg = ":{0} 431 :No nickname given \r\n".format(host)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip())

def nick_collision(conn, data, host):
    msg = ":{0} 433 {1} :Nickname is already in use \r\n".format(host, data.nick)
    conn.send(msg.encode())
    irc_log("OUT",msg.strip())

##################
#Command Handlers#
##################

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
        channel = server.getChannels()[channel_name]
        channel.clients.append(client.nick)

        msg = ":{} JOIN {} * :realname\r\n".format(client.nick, channel_name)
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel topic
        msg = ":{} 332 {} {} {}\r\n".format(HOST, client.nick, channel_name, channel.topic)
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)
        
        # reply to client with channel nick list
        msg = ":{host} 353 {nick} @ {channel_name} :{client_list}\r\n:{host} 366 {nick} {channel_name} :End of /NAMES list\r\n".format(nick=client.nick, host=HOST, channel_name=channel_name, client_list=(' '.join(channel.clients)))
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

    except KeyError:
        # if channel doesn't exist

        # create new Channel object and add to servers channel dictionary
        channel = Channel(client.nick, channel_name)
        channel.clients.append(client.nick)
        client.channels.append(channel)
        server.addChannel(channel_name, channel)

        msg = ":{} JOIN {}\r\n".format(client.nick, channel_name)
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel topic
        msg = ":{} 332 {} {} {}\r\n".format(HOST, client.nick, channel_name, "no topic here")
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)

        # reply to client with channel nick list
        msg = ":{host} 353 {nick} @ {channel_name} :{nick}\r\n:{host} 366 {nick} {channel_name} :End of /NAMES list\r\n".format(nick=client.nick, host=HOST, channel_name=channel_name)
        server.getClients()[client.nick][0].sendall(msg.encode())
        irc_log("OUT", msg)


def handle_PRIVMSG(params, server, client, HOST):
    target_list = mp.parse_csv_list(params[0])
            
    for target in target_list:
        if target[0] == '#':
            # if target is channel
            server.getChannels()[target].broadcast(params[1], client.nick, server) # broadcast here just means send to all the channel subscribers, nothing else!
        else:
            # if targer is client
            msg = ":{}!{}@{} PRIVMSG {} :{}\r\n".format(client.nick, client.nick, HOST, target, params[1])
            server.getClients()[target][0].sendall(msg.encode())
            irc_log("OUT", msg)

def handle_PONG(params, server, client, HOST):
    pass

###################################
# CLIENT REMOVAL CLEANUP FUNCTION #
###################################

# safely remove clients presence from the server
#
# generally this function will be called on when
# a QUIT command is received, however,
# it may also be called on other exceptional
# situations to prevent inconsistencies in the system
# causing unpredictable errors down the line
def remove_client(key, sock_selector, server):

    conn = key.fileobj
    client = key.data

    # unregister socket from socket selector
    # so no attempt will be made to read or write to it
    sock_selector.unregister(conn)


    # stop reading from the socket, channels may still write
    # as we have to remove 
    conn.shutdown(socket.SHUT_RD)


    # Remove client from channels where client is subscribed
    # before we remove nicks as channel may still reference
    # we will handle that situation as well in channel
    # message sending function but its best to be safe
    for channel in client.channels:
        channel.clients.remove(client.nick)

    # Remove from clients dictionary
    server.deleteClient(client.nick)


    # shutdown writing to socket and close connection
    conn.shutdown(socket.SHUT_WR)
    conn.close()


