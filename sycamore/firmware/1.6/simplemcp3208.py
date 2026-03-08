import busio
import digitalio
import time
from ulab import numpy
from debug import timed_function
import time
import gc

class MCP3208:
    """Driver for the MCP3208 ADC. Operates in single-ended mode,
    pass in an index to read from and a configured SPIDevice."""
    def __init__(self, spi_bus: busio.SPI, cs: digitalio.DigitalInOut):
        # Pre-allocate some space for read results
        self.result = bytearray(3)
        self.val = None
        self.sampleNum = 0
        # Oversampling results in an array allocation due to numpy use,
        # but the ADC seems to be stable enough that oversampling isn't
        # strictly needed...
        self.oversampleRate = 1
        self.sampleBuffer = [None] * self.oversampleRate
        # Init the 8 different reads so we don't have to make new byte[] every time
        self.commands = { 0: self.command(0), 1: self.command(1), 2: self.command(2), 3: self.command(3), 4: self.command(4), 5: self.command(5), 6: self.command(6), 7: self.command(7) }
        self.cs = cs
        self.spi_bus = spi_bus

    def command(self, index: int) -> bytes:
        cmd = 128  # 1000 0000 (Start)
        cmd += 64  # 1100 0000 (Single ended)
        cmd += ((index & 0x07) << 3) # (Address)
        return bytes([cmd, 0x0, 0x0])

    # @timed_function # 0-1ms each
    def readAdc(self, index: int) -> int:
        self.sampleNum = 0
        while self.sampleNum < self.oversampleRate:
            while not self.spi_bus.try_lock():
                pass
            try:
                self.cs.value = False
                self.spi_bus.write_readinto(self.commands[index], self.result)
                self.cs.value = True
            finally:
                self.spi_bus.unlock()

            self.val = (self.result[0] & 0x01) << 11  # only B11 is here
            self.val |= self.result[1] << 3           # B10:B3
            self.val |= self.result[2] >> 5           # MSB has B2:B0 ... need to move down to LSB
            self.sampleBuffer[self.sampleNum] = self.val
            self.sampleNum += 1
        if self.oversampleRate > 1:
            # Using oversampling will add an allocation to the heap for the numpy array
            return numpy.median(numpy.array(self.sampleBuffer))
        else:
            return self.sampleBuffer[0]
