import time

class Client:

    # inbound and outbound stream buffers, respectively
    # each item is the list is a single IRC <message>
    inb = []
    outb = []

    # list of channel objects which client is a part of
    channels = []

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