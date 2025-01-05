import gc

# Unfortunately, some of the code in Sycamore still performs memory allocations
# So we need to tell circuitpython that GC is required, if the module
# is not being clocked, if scales update, or if the module has run through a few
# hundred iterations. The only two paths that actually cause allocations
# are the scale shuffle and changing scale, and we can take a pretty good
# guess at how many scale changes without clocks can be performed before
# the whole thing runs out of memory to try and keep the module ready for
# much more infrequent clocks. Clocking itself does some minimal allocation which
# necessitates GCs after a while.
class SycamoreGC:
    def __init__(self):
        # Disable GC for tighter control over performance. This should help
        # prevent problems with missing clocks.
        gc.disable()
        self._gcRequired = False
        self._clockCount = 0 # around 1500 before GC required
        self._scaleChanges = 0 # around 100 before GC required
        self._clockBeforeGc = False

    @property
    def clockBeforeGc(self):
        return self._clockBeforeGc

    def clockedEarly(self):
        self._clockBeforeGc = True

    def disableClockedEarly(self):
        self._clockBeforeGc = False

    def collect(self):
        print("Garbage collecting...")
        gc.collect()
        self._clockBeforeGc = False

    def maybeCollect(self):
        if self._gcRequired:
            self.collect()
            self._gcRequired = False
            self._scaleChanges = 0
            self._clockCount = 0

    def incrementScaleChanges(self):
        self._scaleChanges += 1
        if self._scaleChanges == 25:
            print("GC required (25 scale changes)")
            self._gcRequired = True
            self._scaleChanges = 0

    def incrementClock(self):
        self._clockCount += 1
        if self._clockCount == 500:
            print("GC required (500 clocks)")
            self._gcRequired = True
            self._ClockCount = 0

    # Debugging only. Do not use this function normally, mem_free and mem_alloc are quite
    # expensive to perform.
    def printMemoryStats(self):
        print("Bytes free: " + str(gc.mem_free()))
        print("Bytes allocated: " + str(gc.mem_alloc()))
