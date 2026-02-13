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
        self.description = ''
        
        if type == DEVICE_CONNECTED:
            self.socket = kwargs['socket']
            self.description = f'{device} has connected'
        elif type == DEVICE_DISCONNECTED:
            self.description = f'{device} has disconnected'
        elif type == DEVICE_GOT_CONFIG:
            self.version = kwargs['version']
            self.OS = kwargs['OS']
            self.width = kwargs['width']
            self.height = kwargs['height']
            self.description = f'{device} sent config'
            
        elif type == NET_MSG:
            self.msg = kwargs['msg']
            self.description = f'{device} sent network message 💬'
        elif type == NET_DAT:
            self.data = kwargs['data']
            self.description = f'{device} sent network data 📊'
        elif type == NET_IMG:
            self.data = kwargs['data']
            self.description = f'{device} sent network image 🖼️'
        elif type == NET_RESPONSE:
            self.msg = kwargs['msg']
            self.description = f'{device} responded to device query ❓'
        # can add additional queue event types here

        # always add newline escape characters to description
        #self.description += '\r\n'