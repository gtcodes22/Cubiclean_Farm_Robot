from adc3008 import adc3008

# open a spidev device on channel 0, device 0
spi = spidev.SpiDev()
spi.open(0,0)

# the max speed is too fast for the adc, so set it to 50 KHz
spi.max_speed_hz = 50000

# bits to send to the ADC to read data
SingleDiff = '1'    # read only a single channel
                    # 3 bits for the channel selection
DontCares = '11'

