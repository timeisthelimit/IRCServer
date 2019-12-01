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