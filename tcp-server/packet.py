class PacketMessage():
    def __init__(self, address, str_ascii):
        self.address = address
        self.str_ascii = str_ascii
        
        # attributes from message
        self.src = str_ascii[:3].upper()
        self.des = str_ascii[3:6].upper()
        self.mtype = str_ascii[6:9].upper()
        self.length = int.from_bytes(str_ascii[9:13], 'big')
        self.data = str_ascii[13:13 + self.length]
        self.end = str_ascii[-3:]
        
        if self.end != '\x00\xa8\x6b':
            print('w: packet didn\'t end correctly')

def construct_packet(src: str, des: str, mtype: str, data: str) -> str:
    length = len(data)
    end = '\x00\xa8\x6b'
    return bytes(f'{src}{des}{mtype}{length}{data}{end}', 'utf-8')
    
def is_valid_packet(data: str) -> bool:
    if (len(data) >= 16 and \
        data[0:3].upper() in ('RPI','SPC','APP') and \
        data[3:6].upper() in ('RPI','SPC','APP') and \
        data[6:9].upper() in ('MSG','DAT','IMG') and \
        data[-3:] == '\x00\xa8\x6b'):
        return True
    
    return False
    
def is_valid_properties(data: str) -> bool:
    if (len(data) >= 16 and \
        data[0:3].upper() in ('RPI','SPC','APP') and \
        data[3:6].upper() in ('RPI','SPC','APP') and \
        data[6:9].upper() in ('MSG','DAT','IMG')):
        return True
    
    return False
        