from scales2 import Scales
from adafruit_simplemath import map_range, constrain

class Quantizer:
    def __init__(self, scales: Scales, expandedDacLookup, rowanEnabled: bool):
        self._scales = scales
        self._expandedDacLookup = expandedDacLookup
        # These are actually only used by quantize, but to avoid allocations, store these
        # as class variables instead of on the stack.
        self._stepRawWithRange = None
        self._shiftOffset = None
        self._stepRawWithOffset = 0
        self._stepTranslated = None
        self._stepTranslatedIndex = 0
        self._targetScaleSlice = None
        self._rowanEnabled = rowanEnabled
        self._scaledValues = {0: 0, 1: 0}

    def rawValue(self, channel: int) -> int:
        return self._scaledValues[channel]

    def quantize(self,
                 stepRaw: int,
                 rangePotAdc: int,
                 rangeAdc: int,
                 shiftPotAdc: int,
                 shiftAdc: int,
                 quantPotAdc: int,
                 quantAdc: int,
                 channel: int) -> int:
        # Range divides the raw step data BEFORE adding a shift offset
        # Range goes from 0-100%
        # As range and stepRaw are both 0-4095, we can simply divide stepRaw by range/4096
        # range | stepRaw | result
        #     0 |    1000 |      0
        #  2048 |    1000 |    500
        #  4096 |    1000 |   1000
        self._stepRawWithRange = stepRaw * (rangePotAdc/4096) # 0-4096, full range
        # Now add on the CV value as well. CV may add 50% of stepRaw to the ranged step.
        #    CV | stepRaw | stepRawRanged |result
        # -2048 |    1000 |             0 |     0
        #     0 |    1000 |             0 |     0
        #  2048 |    1000 |             0 |   500
        #  2048 |    1000 |           500 |  1000
        self._stepRawWithRange = constrain(self._stepRawWithRange + (stepRaw * (rangeAdc/4095)), 0, 4095) # May be negative
        self._scaledValues[channel] = self._stepRawWithRange
        # Shift by up to 12 semitones (1 octave) to the left or right
        # 0 value is halfway through the range (2048)
        # +12 is 4095
        # -12 is 0
        # So, we need 4096 mapped onto -12 to + 12
        # This could be reduced to -12*68.26 to +12*68.26 to save a multiplication
        # but for readibility we're going with this for now.
        # shiftAdc might be negative, so we map -2048 (-5v) to 4095+2048 (pot value to +5v)
        # Note that shift moves the sequence in key - it's more an inversion than a transposition
        self._shiftOffset = int(map_range(constrain(shiftPotAdc + shiftAdc, 0, 4096), 0, 4096, -12, 12) * 68.26)
        self._stepRawWithOffset = int(constrain(self._stepRawWithRange + self._shiftOffset, 0, 4095))
        self._stepTranslatedIndex = self._expandedDacLookup[self._stepRawWithOffset]

        # Quantize is another 0-100% range pot + jack value.
        # 0% will output just the first note in the targetScaleFull
        # 100% will output all notes
        # As targetScaleFull is initialised note by note, in order, across 5 octaves
        # we eliminate the first 5 notes from the scale first, then the next 5 notes
        # and so on. This means the ordering of scale notes matters, and we can take
        # out (for example) a 7th in a root-third-fifth-seventh "scale" first, before
        # taking out the fifth/third/root.
        # quantPotAdc = 0-4096
        # quantAdc = -2048 to 2048
        # Note that if Rowan is enabled, we can skip this step as code.py calls
        # updateScaleForQuantization regularly.
        if not self._rowanEnabled:
            self._targetScaleSlice = int(map_range(constrain(quantPotAdc + quantAdc, 0, 4096), 0, 4096, 1, self._scales.currentScaleLength()))
            self._scales.updateScaleForQuantization(self._targetScaleSlice)

        return min(self._scales.previousTargetScaleSliceContents, key=lambda x: abs(x-self._stepTranslatedIndex))
