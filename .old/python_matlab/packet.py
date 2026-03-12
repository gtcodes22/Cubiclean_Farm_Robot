class PacketMessage():
    def __init__(self, address, str_utf8):
        self.address = address
        self.str_utf8 = str_utf8
        
        # attributes from message
        self.src = str_utf8[:3].upper()
        self.des = str_utf8[3:6].upper()
        self.mtype = str_utf8[6:9].upper()
        self.length = int.from_bytes(bytes(str_utf8[9:13], 'utf-8'), 'big')
        self.data = str_utf8[13:13 + self.length]
        self.end = str_utf8[-3:]
        
        if self.end != '\x00\xa8\x6b':
        #if self.end != '\x00\xc2\xa8\x6b':  # corrected for utf
            print(f'w: packet didn\'t end correctly {len(self.end)}:{self.end.encode('utf-8').hex()}')

def construct_packet(src: str, des: str, mtype: str, data):
    length = len(data)
    sLength = length.to_bytes(4, 'big')
    end = '\x00\xa8\x6b'
    
    if mtype == 'IMG':
        return bytes(f'{src}{des}{mtype}', 'utf-8') + sLength + data + bytes(f'{end}', 'utf-8')
        
    return bytes(f'{src}{des}{mtype}', 'utf-8') + sLength + bytes(f'{data}{end}', 'utf-8')
    
def is_valid_packet(data: str) -> bool:
    if (len(data) >= 16 and \
        data[0:3].upper() in ('RPI','SPC','APP') and \
        data[3:6].upper() in ('RPI','SPC','APP') and \
        data[6:9].upper() in ('MSG','DAT','IMG') and \
        data[-3:] == '\x00\xa8\x6b'):
        return True
    
    return False
    
def is_valid_properties(data: str) -> bool:
    print(f'checking {data}') 
    if (data[0:3].upper() in ('RPI','SPC','APP') and \
        data[3:6].upper() in ('RPI','SPC','APP') and \
        data[6:9].upper() in ('MSG','DAT','IMG')):
        return True
    
    print('packet check failed!')
    return False
        