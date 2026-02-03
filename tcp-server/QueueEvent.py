SERVER_START = 0
SERVER_END = 1
SERVER_ERROR = 2

DEVICE_CONNECTED = 10
DEVICE_DISCONNECTED = 11
DEVICE_GOT_CONFIG = 12

NET_MSG = 20
NET_DAT = 21
NET_IMG = 22

NET_RESPONSE = 25

PACKET_INCOMPLETE = 30

class QueueEvent():
    def __init__(self, type: int, device, **kwargs):
        self.type = type
        self.device = device
        
        if type == DEVICE_CONNECTED:
            self.socket = kwargs['socket']
        elif type == DEVICE_DISCONNECTED:
            pass
        elif type == DEVICE_GOT_CONFIG:
            self.version = kwargs['version']
            self.OS = kwargs['OS']
            self.width = kwargs['width']
            self.height = kwargs['height']
            
        elif type == NET_MSG:
            self.msg = kwargs['msg']
        elif type == NET_DAT:
            self.data = kwargs['data']
        elif type == NET_IMG:
            self.data = kwargs['data']
        elif type == NET_RESPONSE:
            self.msg = kwargs['msg']
        # can add additional queue event types here
