class Channel:
    operator=None
    clients=[]

    # the person who first creates a channel becomes its operator
    def __init__(self, operator):
        self.clients.append(operator)
        self.operator = operator
