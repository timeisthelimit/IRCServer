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
