from micropython import const
import time
import busio
import digitalio

# Combined write & update, appears to have a glitch?
# ZERO = const(0x30)
# ONE  = const(0x31)
ZERO = const(0b00000000)
ONE = const(0b00000001)

UPDATE_ZERO = bytes([0x10, 0x00, 0x00])
UPDATE_ONE = bytes([0x11, 0x00, 0x00])

# LUT for DAC. This pre-loads the bytes for channels 0 and 1
# for all 4095 values(!)

def dacBytes(value: int, channel: int) -> bytes:
    toReturn = (value << 4).to_bytes(2, 'big')
    return bytes([0x00, channel, toReturn[0], toReturn[1]])

dacBytesLUT0 = {}
dacBytesLUT1 = {}
spiBus = None
ltcCs = None

# LTC2632 DAC driver
def setup(dacLUT, spi_bus: busio.SPI, cs: digitalio.DigitalInOut):
    print("Setting DAC external reference")

    global spiBus
    spiBus = spi_bus

    global ltcCs
    ltcCs = cs

    while not spiBus.try_lock():
        pass
    try:
        ltcCs.value = False
        # command = 0111 (select external reference)
        # address = 1111 (all DACs)
        # data    = ignored, all 0s
        spiBus.write(bytes([0b01111111, 0b00000000, 0b00000000]))
        ltcCs.value = True
    finally:
        spiBus.unlock()

    for i in dacLUT:
        dacBytesLUT0.update({i: dacBytes(i, ZERO)})
        dacBytesLUT1.update({i: dacBytes(i, ONE)})

# Write a 0-4095 value to the LTC2632 DAC
def write(value: int, channel: int):
        if channel == ZERO:
            toWrite = dacBytesLUT0[value]
            while not spiBus.try_lock():
                pass
            try:
                ltcCs.value = False
                spiBus.write(toWrite)
                ltcCs.value = True
            finally:
                spiBus.unlock()

            while not spiBus.try_lock():
                pass
            try:
                ltcCs.value = False
                spiBus.write(UPDATE_ZERO)
                ltcCs.value = True
            finally:
                spiBus.unlock()
            return
        elif channel == ONE:
            toWrite = dacBytesLUT1[value]
            while not spiBus.try_lock():
                pass
            try:
                ltcCs.value = False
                spiBus.write(toWrite)
                ltcCs.value = True
            finally:
                spiBus.unlock()

            while not spiBus.try_lock():
                pass
            try:
                ltcCs.value = False
                spiBus.write(UPDATE_ONE)
                ltcCs.value = True
            finally:
                spiBus.unlock()
            return
