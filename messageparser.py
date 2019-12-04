#Pases messages into logical parsed message objects
class MessageParser:
    
    def parseMessage(self, message):
        prefix=''
        command=''
        parameters=[]

        message_length = len(message)
        beg= 0
        end= 1

        # get prefix
        if message[0] == chr(0x3a):
            if message[1] == chr(0x20):
                raise ValueError("unexpected whitespace after ':'")
            beg+=1
            end+=1
            while message[end] != chr(0x20):
                end+=1
            prefix= message[beg:end]
            beg= end+1
            end= beg+1

        # get command
        if ord(message[beg]) >= 48 and ord(message[beg]) <= 57:
            end= end+2
            for i in range(beg,end):
                command+= message[i]
            beg= end+1
            end= beg+1
        else:
            while message[end] != chr(0x20):
                end+=1
                if message[end] == '\r':
                    command = message[beg:end]
                    return (prefix, command, [])
            command = message[beg:end]
            beg= end+1
            end= beg+1

        # get command params
        param_count=0
        while param_count < 15:

            # handle 'trailing' param
            if message[beg] == ':':
                beg+=1
                while True:
                    end+=1
                    if message[end] == '\r':
                        parameters.append(message[beg:end])
                        return (prefix, command, parameters)

            # handle 'middle' param
            while message[end] != chr(0x20):
                end+=1
                if message[end] == '\r':
                    parameters.append(message[beg:end])
                    return (prefix, command, parameters)
            parameters.append(message[beg:end])
            beg= end+1
            end= beg+1

            param_count+=1

        return (prefix, command, parameters)

    def parse_csv_list(self, _list):
        split_list=[]
        for item in _list.split(','):
            if item != '':
                split_list.append(item.strip())

        return split_list
