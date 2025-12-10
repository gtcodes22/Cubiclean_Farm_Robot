SERVER_START = 0
SERVER_END = 1
SERVER_ERROR = 2
NET_MSG = 3
DEVICE_CONNECTED = 4
DEVICE_DISCONNECTED = 5

class QueueEvent():
    def __init__(self, type: int, **kwargs):
        self.type = type
        
        if type == NET_MSG:
            self.msg = kwargs['msg']
        elif type == DEVICE_CONNECTED:
            self.device = kwards['device']
            self.socket = kwargs['socket']
        elif type == DEVICE_DISCONNECTED:
            self.device = kwards['device']
        
        # can add additional queue event types here
