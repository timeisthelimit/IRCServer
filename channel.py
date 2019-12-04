import serverfunctions as sfn

class Channel:
    channel_name=None
    operator=None
    topic='no topic here'

    clients=[]

    # the person who first creates a channel becomes its operator
    def __init__(self, operator, channel_name):
        self.clients.append(operator)
        self.operator = operator
        self.channel_name = channel_name

    # send message to all clients listening to this channel
    def broadcast(self, message, sender, server):
        for c in self.clients:
            msg = ":{} PRIVMSG {} :{}\r\n".format(sender, self.channel_name, message)
            server.clients[c][0].sendall(msg.encode())
            sfn.irc_log("OUT", msg)