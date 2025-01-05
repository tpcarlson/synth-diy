from micropython import const
import time
import busio
import digitalio
from debug import timed_function

# External constants.
DAC_ZERO = const(0b00000000)
DAC_ONE = const(0b00000001)

class LTC2632:
    """Driver for the LTC2632 DAC"""
    def __init__(self, spi_bus: busio.SPI, cs: digitalio.DigitalInOut):
        self.UPDATE_ZERO = bytes([0x10, 0x00, 0x00])
        self.UPDATE_ONE = bytes([0x11, 0x00, 0x00])
        self.dacBytesLUT0 = {}
        self.dacBytesLUT1 = {}
        self.spiBus = spi_bus
        self.ltcCs = cs
        self.toWrite = None

    # LUT for DAC. This pre-loads the bytes for channels 0 and 1
    # for all 4095 values
    def dacBytes(self, value: int, channel: int) -> bytes:
        toReturn = (value << 4).to_bytes(2, 'big')
        return bytes([0x00, channel, toReturn[0], toReturn[1]])

    # LTC2632 DAC driver
    def setup(self, dacLUT):
        print("Setting DAC external reference")
        while not self.spiBus.try_lock():
            pass
        try:
            self.ltcCs.value = False
            # command = 0111 (select external reference)
            # address = 1111 (all DACs)
            # data    = ignored, all 0s
            self.spiBus.write(bytes([0b01111111, 0b00000000, 0b00000000]))
            self.ltcCs.value = True
        finally:
            self.spiBus.unlock()

        for i in dacLUT:
            self.dacBytesLUT0.update({i: self.dacBytes(i, DAC_ZERO)})
            self.dacBytesLUT1.update({i: self.dacBytes(i, DAC_ONE)})

    def validDacKeys(self):
        return list(self.dacBytesLUT1.keys())

    # Write a 0-4095 value to the LTC2632 DAC
    # @timed_function (0-1ms)
    def write(self, value: int, channel: int):
            if channel == DAC_ZERO:
                toWrite = self.dacBytesLUT0[value]
                while not self.spiBus.try_lock():
                    pass
                try:
                    self.ltcCs.value = False
                    self.spiBus.write(toWrite)
                    self.ltcCs.value = True
                finally:
                    self.spiBus.unlock()

                while not self.spiBus.try_lock():
                    pass
                try:
                    self.ltcCs.value = False
                    self.spiBus.write(self.UPDATE_ZERO)
                    self.ltcCs.value = True
                finally:
                    self.spiBus.unlock()
                return
            elif channel == DAC_ONE:
                toWrite = self.dacBytesLUT1[value]
                while not self.spiBus.try_lock():
                    pass
                try:
                    self.ltcCs.value = False
                    self.spiBus.write(toWrite)
                    self.ltcCs.value = True
                finally:
                    self.spiBus.unlock()

                while not self.spiBus.try_lock():
                    pass
                try:
                    self.ltcCs.value = False
                    self.spiBus.write(self.UPDATE_ONE)
                    self.ltcCs.value = True
                finally:
                    self.spiBus.unlock()
                return
