class Oak:
    def __init__(self, i2c):
        self._shiftLock = False
        self._quantizeLock = False
        self._lengthLock = False
        self._rangeLock = False
        self._scaleShuffle = False
        self._loopReset = False
        self._scaleReset = False

        self._toWrite = bytearray(1)
        self._toRead = bytearray(1)

        self._i2c = i2c

        # Masks for reading i2c values
        self._scaleShuffleMask = 0b01000000
        self._resetLoopMask    = 0b00100000
        self._scaleResetMask   = 0b00010000
        self._shiftMask        = 0b00001000
        self._quantMask        = 0b00000100
        self._lengthMask       = 0b00000010
        self._rangeMask        = 0b00000001

    @property
    def shiftLock(self):
        return self._shiftLock

    @property
    def quantizeLock(self):
        return self._quantizeLock

    @property
    def lengthLock(self):
        return self._lengthLock

    @property
    def rangeLock(self):
        return self._rangeLock

    @property
    def scaleShuffle(self):
        return self._scaleReset

    @property
    def scaleReset(self):
        return self._scaleReset

    @property
    def loopReset(self):
        return self._loopReset

    def update(self, noteChanged, loopStart):
        while not self._i2c.try_lock():
            pass
        try:
            # Sycamore -> Oak. This writes out Sycamore's current state.
            # UNUSED | loop start | note change | step | shift | quant | length | range
            self._toWrite[0]  = self._rangeLock
            self._toWrite[0] |= self._lengthLock << 1
            self._toWrite[0] |= self._quantizeLock << 2
            self._toWrite[0] |= self._shiftLock << 3
            self._toWrite[0] |= 1 << 4 # step
            self._toWrite[0] |= noteChanged << 5
            self._toWrite[0] |= loopStart << 6
            self._i2c.writeto(0x42, self._toWrite)
        finally:
            self._i2c.unlock()

    def read(self):
        while not self._i2c.try_lock():
            pass
        try:
            # Sycamore -> Oak -> Sycamore. Basically ask Oak for its state.
            # UNUSED | scale shuffle | reset loop | scale reset | shift | quant | length | range
            self._i2c.readfrom_into(0x42, self._toRead)
        finally:
            self._i2c.unlock()

        self._scaleShuffle = (self._toRead[0] & self._scaleShuffleMask) >> 6
        self._loopReset = (self._toRead[0] & self._resetLoopMask) >> 5
        self._scaleReset = (self._toRead[0] & self._scaleResetMask) >> 4

        self._shiftLock = (self._toRead[0] & self._shiftMask) >> 3
        self._quantizeLock = (self._toRead[0] & self._quantMask) >> 2
        self._lengthLock = (self._toRead[0] & self._lengthMask) >> 1
        self._rangeLock = self._toRead[0] & self._rangeMask
