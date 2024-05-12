import busio
import digitalio
import time
from ulab import numpy
from debug import timed_function
import time
import gc

# Very simple driver for the MCP3208. Operates in single-ended mode,
# pass in an index to read from and a configured SPIDevice.
result = bytearray(3)

# Globals to avoid allocations
cmd = None
val = None

# Oversampling results in an array allocation, but the ADC seems
# to be stable enough that oversampling isn't really needed...
oversampleRate = 1
sampleNum = 0
sampleRunningTotal = 0
sampleBuffer = [None] * oversampleRate

def command(index: int) -> bytes:
    cmd = 128  # 1000 0000 (Start)
    cmd += 64  # 1100 0000 (Single ended)
    cmd += ((index & 0x07) << 3) # (Address)
    return bytes([cmd, 0x0, 0x0])

# Init the 8 different reads so we don't have to make new byte[] every time
commands = { 0: command(0), 1: command(1), 2: command(2), 3: command(3), 4: command(4), 5: command(5), 6: command(6), 7: command(7) }

# @timed_function # 0-1ms each
def readAdc(index: int, spi_bus: busio.SPI, cs: digitalio.DigitalInOut) -> int:
    global sampleNum
    sampleNum = 0
    global sampleRunningTotal
    sampleRunningTotal = 0
    while sampleNum < oversampleRate:
        while not spi_bus.try_lock():
            pass
        try:
            cs.value = False
            global result
            spi_bus.write_readinto(commands[index], result)
            cs.value = True
        finally:
            spi_bus.unlock()

        global val
        val = (result[0] & 0x01) << 11  # only B11 is here
        val |= result[1] << 3           # B10:B3
        val |= result[2] >> 5           # MSB has B2:B0 ... need to move down to LSB
        sampleBuffer[sampleNum] = val
        sampleNum += 1
    if oversampleRate > 1:
        # Using oversampling will add an allocation to the heap for the numpy array
        return numpy.median(numpy.array(sampleBuffer))
    else:
        return sampleBuffer[0]
