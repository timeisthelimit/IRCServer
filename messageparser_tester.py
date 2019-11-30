from messageparser import MessageParser

mp = MessageParser()

try:
    mp.parseMessage(':prefix command middle :this is a trailing parameter \r\n')
except ValueError as e:
    print(e)

print("prefix: ", mp.prefix)
print("command:", mp.command)
print("parameters:", mp.parameters)

# try:
#     mp.parseMessage(':prefix 001 middle :this is a trailing parameter \r\n')
# except ValueError as e:
#     print(e)

# print("prefix: ", mp.prefix)
# print("command:", mp.command)
# print("parameters:", mp.parameters)