import random
import array
from adafruit_simplemath import constrain

class Scales:
    def __init__(self, targetScales, ledcontrol, gc):
        self._gc = gc
        self._ledcontrol = ledcontrol
        self._targetScales = targetScales
        self._currentScale = 1
        self._previousScale = 1
        self._targetScaleFull = self._targetScales[self._currentScale]
        self._targetScaleFullShuffled = list(self._targetScaleFull) # This is a copy
        self._previousTargetScaleSlice = len(self._targetScaleFullShuffled)

        # A memoryview is used to avoid allocations (list slicing). This memory view needs to
        # be updated whenever the targetScaleFullShuffled is updated.
        # -New scale chosen (Array contents will have changed)
        # -List contents are shuffled with scale tweak mode
        self._targetScaleFullShuffledMv = memoryview(array.array('i', self._targetScaleFullShuffled))
        self._previousTargetScaleSliceContents = (self._targetScaleFullShuffledMv[:self._previousTargetScaleSlice])
        self._newlyShuffled = True
        # Scale shuffle mode. When in scale shuffle mode (Entered with a long press on
        # the encoder), the current scale is shuffled. Subsequent short presses shuffle
        # the scale again.
        # Exiting shuffle mode requires a second long press.
        self._shuffleMode = False

    @property
    def currentScale(self):
        return self._currentScale

    @property
    def previousTargetScaleSlice(self):
        return self._previousTargetScaleSlice

    def currentScaleLength(self):
        return len(self._targetScaleFullShuffled)

    def modifyScale(self, scaleDelta):
        self._previousScale = self._currentScale
        self._currentScale = constrain(self._currentScale + scaleDelta, 0, len(self._targetScales)-1)
        self._newlyShuffled = True

    def update(self):
        # Optimisation: If we're already at the limits (00 or len(targetScales-1)),
        # don't allocate a new list or do any of that work.
        if self._previousScale != self._currentScale:
            # Changing scale takes around 2ms
            self._ledcontrol.set7Seg(self._currentScale)
            self._shuffleMode = False
            self._ledcontrol.setShuffleEnabled(False)
            self._targetScaleFull = self._targetScales[self._currentScale]
            self._targetScaleFullShuffled = list(self._targetScaleFull)
            self._targetScaleFullShuffledMv = memoryview(array.array('i', self._targetScaleFullShuffled))
            # Pre-allocating all the memoryviews for scales would avoid an allocation, but most
            # of the time the module is going to be clocked (Which performs a GC step)
            # To avoid OOM situations when the module is NOT clocked, record how many
            # scale changes have taken place.
            self._gc.incrementScaleChanges()
            self._newlyShuffled = True

    def unshuffle(self):
        self._targetScaleFullShuffled = list(self._targetScaleFull)
        self._targetScaleFullShuffledMv = memoryview(array.array('i', self._targetScaleFullShuffled))
        self._gc.incrementScaleChanges()
        self._newlyShuffled = True
        self._shuffleMode = False
        self._ledcontrol.setShuffleEnabled(False)

    def shuffle(self):
        self._targetScaleFullShuffled.sort(key=lambda x: random.random())
        self._targetScaleFullShuffledMv = memoryview(array.array('i', self._targetScaleFullShuffled))
        self._gc.incrementScaleChanges()
        self._newlyShuffled = True
        self._shuffleMode = True
        self._ledcontrol.setShuffleEnabled(True)

    def updated(self):
        return self._newlyShuffled

    def setShuffled(self, shuffled: bool):
        self._newlyShuffled = shuffled

    def slice(self, slice: int):
        return self._targetScaleFullShuffledMv[:slice]

    def updateScaleForQuantization(self, targetScaleSlice: int) -> bool:
        if self.updated() or self._previousTargetScaleSlice != targetScaleSlice:
            self._previousTargetScaleSliceContents = self.slice(targetScaleSlice)
            self._previousTargetScaleSlice = targetScaleSlice
            self.setShuffled(False)
            return True
        else:
            return False

    @property
    def previousTargetScaleSliceContents(self):
        return self._previousTargetScaleSliceContents

    def toggleShuffleMode(self) -> bool:
        self._shuffleMode = not self._shuffleMode
        # Reset to the original scale:
        if not self._shuffleMode:
            self.unshuffle()
        else:
            self.shuffle()
        return self._shuffleMode

    def maybeShuffle(self) -> bool:
        if self._shuffleMode:
            self.shuffle()
        return self._shuffleMode
