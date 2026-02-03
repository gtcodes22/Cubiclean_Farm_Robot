from spidev import SpiDev
from bitarray import bitarray
from bitarray.util import ba2int

class adc3008:        
    # bits to send to the ADC to read data
    Start = '1'         # signals start of read
    SingleDiff = '1'    # read only a single channel
                        # 3 bits for the channel selection
    DontCares = '000'  # sending two bits 
    
    def __init__(self, bus = 0, device = 0, freq = 50000):
        # open a spidev device on channel 0, device 0
        self.spi = spidev.SpiDev()
        self.spi.open(bus,device)

        # the max speed is too fast for the adc, so set it to 50 KHz
        self.spi.max_speed_hz = freq

    def close(self):
        spi.close()
        
    def get_channel(self, channel):
        # convert channel into a string of the binary number, padded to 
        # three bits
        channelBin = '{0:03b}'.format(channel)
        
        # first byte of spi transfer
        byte = bitarray(Start + SingleDiff + channelBin + DontCares)
        raw = spi.xfer([0, ba2int(byte),0,0,0])
        
        print(raw)
        return raw