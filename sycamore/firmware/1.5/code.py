import digitalio
import analogio
import board
import busio
from adafruit_debouncer import Button, Debouncer
from adafruit_simplemath import map_range, constrain
import rotaryio
import random
from simplemcp3208 import MCP3208
from ltc2632 import LTC2632, DAC_ZERO, DAC_ONE
from ledcontrol import LedControl
import deque
from debug import timed_function
import time
from config import Config
from oak import Oak
from rowan import Rowan
from sycamore_gc import SycamoreGC
from sequence import Sequence
from scales2 import Scales
from quantizer import Quantizer

# @timed_function # 0-1ms
def updateTriggerInputs():
    seedTriggerDebounced.update()
    mutateTriggerDebounced.update()

# @timed_function # 3-4ms?
def updateButtons():
    # Update switches
    seedSwitch.update()
    mutateSwitch.update()
    modeButton.update()
    clockSwitch.update()

    # Encoder
    encoderSwitch.update()

def seed():
    sequenceRaw.seed()
    sequenceRaw2.seed()
    ledcontrol.blink(ledcontrol.seedLed)

def mutate(forceRandom: bool):
    if auxModeMutate and not forceRandom:
        # Inverted, 0 to +5v CV:
        auxAdc = 4095 - adc.readAdc(4)
        sequenceRaw.sequence[clock] = auxAdc
        sequenceRaw2.sequence[clock] = auxAdc
    else:
        sequenceRaw.sequence[clock] = random.randint(0, 4095)
        sequenceRaw2.sequence[clock] = random.randint(0, 4095)

    ledcontrol.blink(ledcontrol.mutateLed)

gc = SycamoreGC()

# Load up configuration
config = Config()
config.load()

# LUT for the DAC
dacLUTMax = len(config.getDacLUT())

# Aux mode settings
auxMode = config.getAuxMode()

i2c = busio.I2C(board.GP11, board.GP10, frequency = 1_000_000) # Clock, Data. 1000KHz "fast mode" i2c.

# Set up expanders. This allows for some portions of the
# code to be skipped over when the expanders are not present.
#
# Current expanders
# =================
# Oak: Scale manipulation, parameter locks, loop triggers
expanders = config.getExpanders()
expandersEnabled = {"oak": False, "rowan": False}
for expander in expanders:
    if expander not in expandersEnabled.keys():
        print("Unknown expander (" + expander + "), skipping")
    else:
        print("Enabling expander: " + expander)
        expandersEnabled[expander] = True

oak = Oak(i2c)

auxModeClockReset = auxMode == "resetClock"
auxModeShuffle = auxMode == "shuffle"
auxModeMutate = auxMode == "mutate"

# Buttons (Debounced)
clockButton = digitalio.DigitalInOut(board.GP28)
clockButton.direction = digitalio.Direction.INPUT
clockButton.pull = digitalio.Pull.UP

seedButton = digitalio.DigitalInOut(board.GP27)
seedButton.direction = digitalio.Direction.INPUT
seedButton.pull = digitalio.Pull.UP

mutateButton = digitalio.DigitalInOut(board.GP19)
mutateButton.direction = digitalio.Direction.INPUT
mutateButton.pull = digitalio.Pull.UP

modeButton = digitalio.DigitalInOut(board.GP16)
modeButton.direction = digitalio.Direction.INPUT
modeButton.pull = digitalio.Pull.UP

# The default debounce is 200ms, we tighten that up some:
clockSwitch = Button(clockButton, short_duration_ms=50) # 50ms debounce on buttons
seedSwitch = Button(seedButton, short_duration_ms=50)
mutateSwitch = Button(mutateButton, short_duration_ms=50)
modeButton = Button(modeButton, short_duration_ms=50)

# Trigger inputs (Debounced)
clockTrigger = digitalio.DigitalInOut(board.GP20)
clockTrigger.direction = digitalio.Direction.INPUT
clockTrigger.pull = digitalio.Pull.UP

seedTrigger = digitalio.DigitalInOut(board.GP21)
seedTrigger.direction = digitalio.Direction.INPUT
seedTrigger.pull = digitalio.Pull.UP

mutateTrigger = digitalio.DigitalInOut(board.GP22)
mutateTrigger.direction = digitalio.Direction.INPUT
mutateTrigger.pull = digitalio.Pull.UP

clockTriggerDebounced = Debouncer(clockTrigger, interval=0.0001) # 1ms
seedTriggerDebounced = Debouncer(seedTrigger, interval=0.001)
mutateTriggerDebounced = Debouncer(mutateTrigger, interval=0.001)

# SPI (ADC)
spi_bus = busio.SPI(board.GP2, MISO=board.GP0, MOSI=board.GP3)
while not spi_bus.try_lock():
    pass

try:
    spi_bus.configure(baudrate=1000000, phase=0, polarity=0) # 1MHz
finally:
    spi_bus.unlock()

# SPI bus 2 (DAC)
spi_bus2 = busio.SPI(board.GP14, MISO=None, MOSI=board.GP15)
while not spi_bus2.try_lock():
    pass

try:
    spi_bus2.configure(baudrate=25000000, phase=0, polarity=0) # 25MHz
finally:
    spi_bus2.unlock()


# ADC
adcCS = digitalio.DigitalInOut(board.GP1)
adcCS.direction = digitalio.Direction.OUTPUT

adc = MCP3208(spi_bus, adcCS)

# DAC
dacCS = digitalio.DigitalInOut(board.GP13)
dacCS.direction = digitalio.Direction.OUTPUT

dac = LTC2632(spi_bus2, dacCS)
dac.setup(config.getDacLUT())
gc.collect()

# The other analogue in
lengthPot = analogio.AnalogIn(board.GP26)

# The scale encoder & button
encoder = rotaryio.IncrementalEncoder(board.GP5, board.GP4)

encoderButton = digitalio.DigitalInOut(board.GP12)
encoderButton.direction = digitalio.Direction.INPUT
encoderButton.pull = digitalio.Pull.UP
encoderSwitch = Button(encoderButton)

# Encoder
last_position = 0
position = 0
encoderDelta = 0

# Storage for the 64-long sequences
sequenceRaw = Sequence()
# Storage for the second, 64-long sequence for output 2's alternate mode
sequenceRaw2 = Sequence()

# Storage for the third, 64-long sequence. This is a copy of sequenceRaw, but
# with fully quantized values that lag behind the current note by a few
# beats. This is again 64 long, allowing for very long latency if desired.
# This is populated with zeroes initially and will be populated with DAC output
# values as sequenceRaw is evaluated. The module should be "primed" with some
# clocks prior to using output2's second mode, but is seeded with random, quantized
# values on module initialisation.
sequenceRaw3 = deque.deque(64, [0] * 64)
sequenceRaw3.seed(dac)

# This is a copy of the actually-raw values, not quantized, to be sent to Rowan
# if the expander is enabled.
sequenceRaw4 = deque.deque(64, [0] * 64)
sequenceRaw4.seed(dac)

ledcontrol = LedControl(i2c)

scales = Scales(config.getScales(), ledcontrol, gc)

# Storage for the current length
clock = 0
maxClock = 8

# ADC storage
shiftAdc    = 0 # 0 (CV)
lengthAdc   = 0 # 1 (CV)
rangeAdc    = 0 # 2 (CV)
quantAdc    = 0 # 3 (CV)
auxAdc      = 0 # 4 (CV)
rangePotAdc = 0 # 7 (Pot)
quantPotAdc = 0 # 5 (Pot)
shiftPotAdc = 0 # 6 (Pot)

# Out2 mode. There are a few different modes...
# 0: A fifth up (+7 semitones)
# 1: A delayed sequence, by default 4 steps behind the current sequence
# 2: An alternate stream
out2Mode = 0
out2TweakMode = False
# Storage for:
# 0: The current semitone offset
# 1: The delay offset
out2TweakValue = { 0: 7, 1: 4}
# Max values. 24 semitones (2 octaves), 63 steps (+ 00 step for "same note")
out2TweakMax = { 0: 24, 1: 63 }

ledcontrol.setMode(out2Mode)

sampleInputs = 0
sampleInputRateLed = 10

# Data used in the loop. Avoid GCs by re-using.
stepQuantized = 42
stepQuantized2 = 42
lengthPotOversample = 0

# Set power to PWM mode (Lower efficiency, lower ripple)
powerMode = digitalio.DigitalInOut(board.SMPS_MODE)
powerMode.direction = digitalio.Direction.OUTPUT
powerMode.value = True

# To combat some jitter in the ADC which can cause the sequence length
# to vary +/- 1, take a lot of samples and recalculate infrequently
lengthAdcs = 0
lengthAdcCount = 0

# "note" change detection
stepQuantizedOld = 0

ledcontrol.setLoading()
# Storage for direct DAC lookups
expandedDacLookup = [None] * 4096 # Unquantized value -> scale slice number
for dacLookupKey in range(0, 4096):
    expandedDacLookup[dacLookupKey] = config.getDacLUT().index(min(config.getDacLUT(), key=lambda x: abs(x-dacLookupKey)))
quantizer = Quantizer(scales, expandedDacLookup, expandersEnabled["rowan"])
expandedDacLookup = None

rowan = Rowan(sequenceRaw, sequenceRaw2, sequenceRaw4, i2c, config.getScales()[0], config.getDacLUT(), gc, quantizer)
if expandersEnabled["rowan"]:
    rowan.updateColours(32, 32, 32) # Reset colours, just to make sure Rowan is in the right state.

ledcontrol.set7Seg(1)

targetScaleSlice = 0
scaleUpdateRate = 10 # every 10 loops
loopCount = 0

# With everything expensive out of the way, run a GC pass
gc.collect()

print("Initialisation complete")

# Quantizer core loop.
# Roughly, this will:
# -Update control inputs
# -Toggle LEDs
# -When clocked, change the DAC ouputs
while True:
    # Shortcut all other updates if we've got a clock
    if not (clockSwitch.pressed or clockTriggerDebounced.fell or gc.clockBeforeGc == True):
        updateTriggerInputs() # These are less critical, we want clocks to respond promptly, but mutate and seed can come later

        if seedTriggerDebounced.fell:
            seed()

        if mutateTriggerDebounced.fell:
            mutate(False)

        # As this is a clock operation, we want it always to be pretty quick
        # A DC voltage to the aux input will hold the module at clock 0, in
        # other words freezing on one note
        if auxModeClockReset and adc.readAdc(4) < 1024:
            clock = 0

        # Split up reading from the encoder, updating LEDs, reading ADC values
        # across time so that the clock trigger always gets a chance to run regularly
        if sampleInputs == 1:
            # Update the rotary encoder, this selects a new scale
            # or changes values when in tweak mode
            position = encoder.position
            if position != last_position:
                encoderDelta = 1 if position > last_position else -1
                if out2TweakMode:
                    out2TweakValue[out2Mode] = constrain(out2TweakValue[out2Mode] + encoderDelta, 0, out2TweakMax[out2Mode])
                    ledcontrol.set7Seg(out2TweakValue[out2Mode])
                    # For whatever reason, in mode 1 (tweak mode for delay), updating the value
                    # ends up being quite expensive. Treat tweak changes like scale changes to
                    # avoid running out of memory.
                    gc.incrementScaleChanges()
                else:
                    scales.modifyScale(encoderDelta)
                    scales.update()
                    # Changing the scale undoes shuffling, so make sure Rowan is also updated
                    if expandersEnabled["rowan"]:
                        rowan.updateColours(32, 32, 32)

                last_position = position
        elif sampleInputs == 2:
            # Normal. CV values from ~0 to ~4090. 0 to +3.3v
            if not oak.quantizeLock:
                quantPotAdc = adc.readAdc(5) # 0-4096
            if not oak.shiftLock:
                shiftPotAdc = adc.readAdc(6) # 0-4096
            if not oak.rangeLock:
                rangePotAdc = adc.readAdc(7) # 0-4096
        elif sampleInputs == 3 and not oak.lengthLock:
            # As this is +/-, we need to invert and then shift.
            for i in range(4):
                lengthAdcs += int(map_range(adc.readAdc(1), 0, 4095, 128, -127))
            lengthAdcCount += 1
            if lengthAdcCount == 4: # 16 iterations, 2048/128
                lengthAdc = lengthAdcs
                lengthAdcs = 0
        elif sampleInputs == 4 and not oak.lengthLock:
            # Oversample the length pot to try and smooth some noise
            lengthPotOversample = 0
            lengthPotOversample += lengthPot.value
            lengthPotOversample += lengthPot.value
            lengthPotOversample += lengthPot.value
            lengthPotOversample += lengthPot.value

            # Calculate max clocks for both CV and pot first:
            maxClockPot = int(constrain(((lengthPotOversample >> 2) >> 10), 1, 64))
            maxClockCv = int(constrain(lengthAdc >> 6, -32, 32))

            maxClock = maxClockCv + maxClockPot
            if clock >= maxClock or clock >= 64:
                clock = 0
        elif sampleInputs == 11:
            # -5 to +5v CV:
            shiftAdc = map_range(adc.readAdc(2), 0, 4095, 2048, -2048)
            rangeAdc = map_range(adc.readAdc(0), 0, 4095, 2048, -2048)
            quantAdc = map_range(adc.readAdc(3), 0, 4095, 1024, -1024)
        elif sampleInputs == 6:
            updateButtons()

            if seedSwitch.pressed:
                seed()

            if mutateSwitch.pressed:
                mutate(True)

            # Long press only does something in modes 0 & 1
            if (out2Mode == 0 or out2Mode == 1) and modeButton.long_press:
                out2TweakMode = not out2TweakMode
                if out2TweakMode:
                    # Entering tweak mode
                    ledcontrol.set7Seg(out2TweakValue[out2Mode])
                else:
                    ledcontrol.set7Seg(scales.currentScale)
                ledcontrol.setTweakEnabled(out2TweakMode)

            # Switch out2 mode:
            if not out2TweakMode and modeButton.short_count != 0:
                out2Mode = (out2Mode+1)%3 # Values 0, 1, 2
                ledcontrol.setMode(out2Mode)
        elif sampleInputs == 8 and encoderSwitch.long_press:
            if scales.toggleShuffleMode():
                if expandersEnabled["rowan"]:
                    rowan.updateColours(32, 0, 64)
            else:
                if expandersEnabled["rowan"]:
                    rowan.updateColours(32, 32, 32)
        elif sampleInputs == 9 and encoderSwitch.short_count != 0:
            # This will do nothing if not already in shuffle mode
            scales.maybeShuffle()
        elif sampleInputs == 12 and auxModeShuffle and adc.readAdc(4) < 1024:
            # Acts a bit like the first long press to enable shuffle mode, and
            # shuffles the scale on subsequent triggers. Disabling shuffle happens
            # with a long press of the scale button. There is no escaping shuffle mode
            # when triggering via the aux input.
            scales.shuffle()
            if expandersEnabled["rowan"]:
                rowan.updateColours(32, 0, 64)
        elif sampleInputs == 10:
            # This will take around 10ms
            # Note that GC is also performed after quantization and DAC changes,
            # this just prevents running out of memory when the module is unclocked
            # but being otherwise tweaked by a human (ie. scale changes)
            gc.maybeCollect()
        elif sampleInputs == 5: # Originally this was task 11, but swapped with a ADC read to spread out lengthy tasks
            # Make absolutely sure the 7 segment display is properly updated,
            # but escape early if a clock happens
            # Fully updating the display will take around 10ms
            while ledcontrol.isDigitsUpdating():
                ledcontrol.update7Seg()
                clockTriggerDebounced.update()
                if clockTriggerDebounced.fell:
                    gc.clockedEarly()
                    break
        elif sampleInputs == 13 and expandersEnabled["oak"]:
            oak.read()

            if oak.scaleShuffle == 1:
                scale.shuffle()
                if expandersEnabled["rowan"]:
                    rowan.updateColours(32, 0, 64)

            # Scale reset + scale shuffle will result in scale reset
            if oak.scaleReset == 1:
                scale.unshuffle()
                if expandersEnabled["rowan"]:
                    rowan.updateColours(32, 32, 32)

            if oak.loopReset == 1:
                clock = 0
        elif sampleInputs == 14 and expandersEnabled["rowan"] and loopCount == scaleUpdateRate:
            # Rowan's scale display is a little expensive to keep updated constantly. Update a lot
            # less frequently than the other elements.
            targetScaleSlice = int(map_range(constrain(quantPotAdc + quantAdc, 0, 4096), 0, 4096, 1, scales.currentScaleLength()))
            if scales.updateScaleForQuantization(targetScaleSlice):
                rowan.updateScale(scales.previousTargetScaleSliceContents)
            loopCount = 0
            gc.incrementClock()

        # State LEDs are less critical and update quickly, just update them every 10 loops
        if sampleInputs % sampleInputRateLed == 0 and gc.clockBeforeGc == False:
            ledcontrol.update()

        # Skip updating the 7 segment displays if we bailed on updating them previously
        if gc.clockBeforeGc == False and ledcontrol.isDigitsUpdating():
            ledcontrol.update7Seg()

        if sampleInputs == 14:
            sampleInputs = 1
            loopCount += 1
        else:
            sampleInputs += 1

        if gc.clockBeforeGc == False:
            clockTriggerDebounced.update()
    else:
        # Output 1:
        stepQuantizedOld = stepQuantized
        stepQuantized = quantizer.quantize(sequenceRaw.sequence[clock], rangePotAdc, rangeAdc, shiftPotAdc, shiftAdc, quantPotAdc, quantAdc, 0)
        sequenceRaw3.push(config.getDacLUT()[stepQuantized])
        sequenceRaw4.push(sequenceRaw.sequence[clock])
        dac.write(config.getDacLUT()[stepQuantized], DAC_ZERO)

        # Output 2:
        # Mode 0: Output semitones above
        if out2Mode == 0:
            stepQuantized2 = stepQuantized
            if stepQuantized2 + out2TweakValue[out2Mode] >= dacLUTMax:
                stepQuantized2 -= out2TweakValue[out2Mode]
            else:
                stepQuantized2 += out2TweakValue[out2Mode]
            dac.write(config.getDacLUT()[stepQuantized2], DAC_ONE)
            rowan.setModeZeroOffset(config.getDacLUT()[stepQuantized2] - config.getDacLUT()[stepQuantized])
        # Mode 1: Output the previous sequence, but offset
        elif out2Mode == 1:
            dac.write(sequenceRaw3.get(out2TweakValue[out2Mode]), DAC_ONE)
        # Mode 2: Output a whole other sequence
        elif out2Mode == 2:
            stepQuantized2 = quantizer.quantize(sequenceRaw2.sequence[clock], rangePotAdc, rangeAdc, shiftPotAdc, shiftAdc, quantPotAdc, quantAdc, 1)
            dac.write(config.getDacLUT()[stepQuantized2], DAC_ONE)

        clock += 1
        # Make sure the clock doesn't run over maxClock
        if clock >= maxClock or clock >= 64:
            clock = 0

        if expandersEnabled["oak"]:
            oak.update(1 if stepQuantized != stepQuantizedOld else 0, 1 if clock == 0 else 0)

        if expandersEnabled["rowan"]:
            rowan.updateNotes(stepQuantized, stepQuantized2, out2Mode, out2TweakValue)

        ledcontrol.blink(ledcontrol.clockLed)

        # With the assumption that we're not going to immediately get another clock,
        # run garbage collection now rather than before the next clock!
        # Garbage collection takes around 8-10ms, which is quite long.
        # Each clock can take 32 bytes of heap
        gc.incrementClock()
        gc.maybeCollect()
        # If chasing memory performance problems, check the memory stats:
        # gc.printMemoryStats()
        gc.disableClockedEarly()
        clockTriggerDebounced.update()
        if clockSwitch.pressed:
            clockSwitch.update()
