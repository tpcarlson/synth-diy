from adafruit_simplemath import constrain
from micropython import const

# Sycamore -> Rowan. Write out the state of Sycamore, which Rowan can process.
# (command0 | command1 | command 2 | channel | 12 data bits)
# Commands:
# 0 0 0: allowed
# 0 0 1: active (Not used at the moment. Set _writeActiveNotes = True to write this value)
# 0 1 0: unquantized
# 0 1 1: quantized
# 1 0 0: red
# 1 0 1: green
# 1 1 0: blue
class Rowan:
    noteOffset = const(0b100000000000)
    scaleOffset = const(0b100000000000)
    scaledACommand = const(0b0100)
    scaledBCommand = const(0b0101)
    chromaticACommand = const(0b0110)
    chromaticBCommand = const(0b0111)
    scaleCommand = const(0b0000)
    activeACommand = const(0b0010)
    activeBCommand = const(0b0011)
    redCommand = const(0b1000)
    greenCommand = const(0b1010)
    blueCommand = const(0b1100)
    rowani2cAddress = const(0x44)
    writeMask = const(0xff)
    maskLeft = 4
    maskRight = 8

    def __init__(self, sequenceRaw, sequenceRaw2, sequenceRaw4, i2c, chromaticScale, quantizer):
        self._sequenceRaw = sequenceRaw
        self._sequenceRaw2 = sequenceRaw2
        self._sequenceRaw4 = sequenceRaw4
        self._i2c = i2c
        self._toWrite = bytearray(2)
        self._chromaticScaleScaled = chromaticScale
        self._quantizer = quantizer
        self._quantizedIndex = 0
        # This is default-false
        self._writeActiveNotes = False
        # Previous values to save writing to Rowan too much
        self._previousScale = 0
        # Avoid allocations
        self._scaleBinary = 0
        self._note = 0
        self._scaledChannelA = 0
        self._scaledChannelB = 0
        self._chromaticA = 0
        self._chromaticB = 0
        self._noteA = 0
        self._out2Value = 0
        self._mode0Offset = 0
        self._red = 0
        self._green = 0
        self._blue = 0

    def setModeZeroOffset(self, offset: int):
        self._mode0Offset = offset

    def write(self, command: int, value: int):
        while not self._i2c.try_lock():
            pass
        try:
            self._toWrite[0] = (command << Rowan.maskLeft) | (value >> Rowan.maskRight)
            self._toWrite[1] = value & writeMask # Trims the top bits
            self._i2c.writeto(Rowan.rowani2cAddress, self._toWrite)
        finally:
            self._i2c.unlock()

    def updateScale(self, previousTargetScaleSliceContents):
        self._scaleBinary = 0
        for self._note in previousTargetScaleSliceContents:
            self._scaleBinary = self._scaleBinary | (Rowan.scaleOffset >> (self._note % 12))

        if self._scaleBinary != self._previousScale:
            self.write(Rowan.scaleCommand, self._scaleBinary)
            self._previousScale = self._scaleBinary

    def updateColours(self, red: int, green: int, blue: int):
        if(self._red != red):
            self._red = red
            self.write(Rowan.redCommand, self._red)
        if(self._green != green):
            self._green = green
            self.write(Rowan.greenCommand, self._green)
        if(self._blue != blue):
            self._blue = blue
            self.write(Rowan.blueCommand, self._blue)

    def updateNotes(self, stepQuantized, stepQuantized2, out2Mode, out2TweakValue):
        # Output 1:
        self._scaledChannelA = int(self._quantizer.rawValue(0))
        self.write(Rowan.scaledACommand, self._scaledChannelA)

        self._chromaticA = min(self._chromaticScaleScaled, key=lambda x:abs(x-self._scaledChannelA))
        self.write(Rowan.chromaticACommand, self._chromaticA)

        # Output 2:
        self._scaledChannelB = 0
        self._chromaticB = 0
        if out2Mode == 0:
            # In output mode 0, want to be a few semis above both _scaledChannelA and _chromaticA
            # But unlike Sycamore, do not have the scale/note indexes handy and instead can
            # set the new value to unquantized + an offset, provided by Sycamore
            # There is a very small chance that, for the highest notes, the offset will overflow.
            # To prevent anything weird from happening, constrain the values allowed)
            self._scaledChannelB = constrain(self._scaledChannelA + self._mode0Offset, 0, 4095)
            self._chromaticB = constrain(self._chromaticA + self._mode0Offset, 0, 4095)
        # Mode 1: Output the previous sequence, but offset
        elif out2Mode == 1:
            self._scaledChannelB = self._sequenceRaw4.get(out2TweakValue[out2Mode]) # 0-4096?
            self._chromaticB = min(self._chromaticScaleScaled, key=lambda x:abs(x-self._scaledChannelB))
        # Mode 2: Output a whole other sequence
        elif out2Mode == 2:
            self._scaledChannelB = int(self._quantizer.rawValue(1))
            self._chromaticB = min(self._chromaticScaleScaled, key=lambda x:abs(x-self._scaledChannelB))

        self.write(Rowan.scaledBCommand, self._scaledChannelB)
        self.write(Rowan.chromaticBCommand, self._chromaticB)

        if self._writeActiveNotes:
            # Note for channel B:
            self._noteB = Rowan.noteOffset >> (stepQuantized2 % 12)
            self.write(Rowan.activeBCommand, self._noteB)
            self._noteA = Rowan.noteOffset >> (stepQuantized % 12)
            self.write(Rowan.activeACommand, self._noteA)
