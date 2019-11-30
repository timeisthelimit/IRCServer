from messageparser import MessageParser

mp = MessageParser()

try:
    prefix, command, params = mp.parseMessage('USER oskar oskar 127.0.0.1 :realname\r\n')
except ValueError as e:
    print(e)

print("prefix: ", prefix)
print("command:", command)
print("parameters:", params)

# try:
#     mp.parseMessage(':prefix 001 middle :this is a trailing parameter \r\n')
# except ValueError as e:
#     print(e)

# print("prefix: ", mp.prefix)
# print("command:", mp.command)
# print("parameters:", mp.parameters)
