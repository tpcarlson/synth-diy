import digitalio
import analogio
import board
import busio
from adafruit_debouncer import Button, Debouncer
from adafruit_simplemath import map_range, constrain
import rotaryio
import random
from simplemcp3208 import readAdc
import ltc2632
import ledcontrol
import json
import os
import deque
import supervisor
import gc
import array
from micropython import const
import supervisor

def loadDacLUT():
    with open("settings.txt", "r") as infile:
        config = json.load(infile)
        return config.get("dacLookupTable")

def loadScales():
    toReturn = {}
    allScales = os.listdir("scales/")
    for file in allScales:
        try:
            with open("scales/" + file, "r") as scale:
                scale = json.load(scale)
                targetScaleFull = []
                for i in scale.get("notes"):
                    for j in range(5):
                        if j == 0:
                            targetScaleFull.append(i)
                        else:
                            targetScaleFull.append(i + (j*12))

                toReturn[scale.get("index")] = targetScaleFull
        except ValueError as error:
            print(error)
            print("Invalid JSON syntax. Check the scale configuration for " + file)
        except AttributeError as error:
            print(error)
            print("Invalid JSON syntax. Check the scale configuration for " + file)
    print("Loaded " + str(len(toReturn)) + " scales")
    return toReturn

def updateTriggerInputs():
    clockTriggerDebounced.update()
    seedTriggerDebounced.update()
    mutateTriggerDebounced.update()

def updateButtons():
    # Update switches
    seedSwitch.update()
    mutateSwitch.update()
    modeButton.update()
    clockSwitch.update()

    # Encoder
    encoderSwitch.update()

def seed():
    for i in range(len(sequenceRaw)):
        sequenceRaw[i] = random.randint(0, 4095)
        sequenceRaw2[i] = random.randint(0, 4095)
    ledcontrol.blink(ledcontrol.seedLed)

def stepTranslatedIndexFunc(x):
    return abs(x-stepTranslatedIndex)

def stepRawIndexFunc(x):
    return abs(x-stepRawWithOffset)

def quantize(stepRaw: int) -> int:
    # Range divides the raw step data BEFORE adding a shift offset
    # Range goes from 0-100%
    # As range and stepRaw are both 0-4095, we can simply divide stepRaw by range/4096
    # range | stepRaw | result
    #     0 |    1000 |      0
    #  2048 |    1000 |    500
    #  4096 |    1000 |   1000
    global stepRawWithRange
    stepRawWithRange = stepRaw * (rangePotAdc/4096) # 0-4096, full range
    # Now add on the CV value as well. CV may add 50% of stepRaw to the ranged step.
    #    CV | stepRaw | stepRawRanged |result
    # -2048 |    1000 |             0 |     0
    #     0 |    1000 |             0 |     0
    #  2048 |    1000 |             0 |   500
    #  2048 |    1000 |           500 |  1000
    stepRawWithRange = constrain(stepRawWithRange + (stepRaw * (rangeAdc/4095)), 0, 4095) # May be negative
    # Shift by up to 12 semitones (1 octave) to the left or right
    # 0 value is halfway through the range (2048)
    # +12 is 4095
    # -12 is 0
    # So, we need 4096 mapped onto -12 to + 12
    # This could be reduced to -12*68.26 to +12*68.26 to save a multiplication
    # but for readibility we're going with this for now.
    # shiftAdc might be negative, so we map -2048 (-5v) to 4095+2048 (pot value to +5v)
    # Note that shift moves the sequence in key - it's more an inversion than a transposition
    global shiftOffset
    shiftOffset = int(map_range(constrain(shiftPotAdc + shiftAdc, 0, 4096), 0, 4096, -12, 12) * 68.26)
    global stepRawWithOffset
    stepRawWithOffset = constrain(stepRawWithRange + shiftOffset, 0, 4095)
    global stepTranslated
    stepTranslated = min(dacLUT, key=stepRawIndexFunc)
    global stepTranslatedIndex
    stepTranslatedIndex = dacLUT.index(stepTranslated)

    # Quantize is another 0-100% range pot + jack value.
    # 0% will output just the first note in the targetScaleFull
    # 100% will output all notes
    # As targetScaleFull is initialised note by note, in order, across 5 octaves
    # we eliminate the first 5 notes from the scale first, then the next 5 notes
    # and so on. This means the ordering of scale notes matters, and we can take
    # out (for example) a 7th in a root-third-fifth-seventh "scale" first, before
    # taking out the fifth/fthird/root.
    # quantPotAdc = 0-4096
    # quantAdc = -2048 to 2048
    global targetScaleSlice
    targetScaleSlice = int(map_range(constrain(quantPotAdc + quantAdc, 0, 4096), 0, 4096, 1, len(targetScaleFullShuffled)))
    return min(targetScaleFullShuffledMv[:targetScaleSlice], key=stepTranslatedIndexFunc)

# These are actually used by quantize, but to avoid allocations, store these
# as globals instead of on the stack.
stepRawWithRange = None
stepRawWithRange = None
shiftOffset = None
stepRawWithOffset = 0
stepTranslated = None
stepTranslatedIndex = 0
targetScaleSlice = None

# LUT for the DAC
dacLUT = loadDacLUT()
dacLUTMax = len(dacLUT)
dacLUTAddress = 0

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
# TODO: Make this configurable?
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

clockTriggerDebounced = Debouncer(clockTrigger, interval=0.001) # 1ms
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

# DAC
dacCS = digitalio.DigitalInOut(board.GP13)
dacCS.direction = digitalio.Direction.OUTPUT

ltc2632.setup(dacLUT, spi_bus2, dacCS)

# The other analogue in
lengthPot = analogio.AnalogIn(board.GP26)
lengthMax = 65535 # 0-64 steps gives 1024 blobs per thing
lengthPerStep = 1024 # length / lengthPerStep should give the current length

# The scale encoder & button
encoder = rotaryio.IncrementalEncoder(board.GP5, board.GP4) # HW 1.2

encoderButton = digitalio.DigitalInOut(board.GP12) # HW 1.2
encoderButton.direction = digitalio.Direction.INPUT
encoderButton.pull = digitalio.Pull.UP
encoderSwitch = Button(encoderButton)

# Encoder
last_position = 0
position = 0
encoderUpdated = False

# Storage for the 64-long sequence
sequenceRaw = [None] * 64
for i in range(len(sequenceRaw)):
    sequenceRaw[i] = random.randint(0, 4095)
# Storage for the second, 64-long sequence for output 2's alternate mode
sequenceRaw2 = [None] * 64
for i in range(len(sequenceRaw2)):
    sequenceRaw2[i] = random.randint(0, 4095)
# Storage for the third, 64-long sequence. This is a copy of sequenceRaw, but
# with fully quantized values that lag behind the current note by a few
# beats. This is again 64 long, allowing for very long latency if desired.
# This is populated with zeroes initially and will be populated with DAC output
# values as sequenceRaw is evaluated. The module should be "primed" with some
# clocks prior to using output2's second mode.
sequenceRaw3 = deque.deque(64, [0] * 64)
# Prime sequenceRaw3, otherwise it's all zeroes until seeded
for i in range(len(sequenceRaw3)):
    sequenceRaw3.push(random.randint(0, 4095))

clock = 0

targetScales = loadScales()

# targetScaleFull actually holds the scale we want to use below, so set to 0
currentScale = 1 # len(targetScales) - 1
targetScaleFull = targetScales[currentScale]
ledcontrol.set7Seg(currentScale)

# Storage for the current length
maxClock = 8
clockLimit = 16

# ADC storage
shiftAdc    = 0 # 0 (CV)
lengthAdc   = 0 # 1 (CV)
rangeAdc    = 0 # 2 (CV)
quantAdc    = 0 # 3 (CV)
auxAdc      = 0 # 4 (CV)
rangePotAdc = 0 # 7 (Pot)
quantPotAdc = 0 # 5 (Pot)
shiftPotAdc = 0 # 6 (Pot) (XXX: range/shift pots are swapped in hardware 1.0)

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

# Scale shuffle mode. When in scale shuffle mode (Entered with a long press on
# the encoder), the current scale is shuffled. Subsequent short presses shuffle
# the scale again.
# Exiting shuffle mode requires a second long press.
shuffleMode = False
targetScaleFullShuffled = list(targetScaleFull) # This is a copy

# A memoryview is used to avoid allocations (list slicing). This memory view needs to
# be updated whenever the targetScaleFullShuffled is updated.
# -New scale chosen (Array contents will have changed)
# -List contents are shuffled with scale tweak mode
targetScaleFullShuffledMv = memoryview(array.array('i', targetScaleFullShuffled))

ledcontrol.setMode(out2Mode)

sampleInputs = 0
sampleInputRate = 10 # Every 10 loops
sampleInputRateMem = 2000
sampleInputRateLed = 10
sampleInputRateEncoder = 25

# For timing
start = None
end = None

# Data used in the loop. Avoid GCs by re-using.
stepQuantized = 42
lengthPotOversample = 0

# Static CV value offset for HW 1.0/1.1 which have a bad -10v reference voltage
globalCvOffset = 0

# Set power to PWM mode (Lower efficiency, lower ripple)
powerMode = digitalio.DigitalInOut(board.SMPS_MODE)
powerMode.direction = digitalio.Direction.OUTPUT
powerMode.value = True

# Quantizer core loop.
# Roughly, this will:
# -Update control inputs
# -Toggle LEDs
# -When clocked, change the DAC ouputs
while True:
#    if sampleInputs % sampleInputRateMem == 0:
#        print("Free memory at code point 1: {} bytes".format(gc.mem_free()))

    updateTriggerInputs() # These are critical, we want the clocks to respond promptly

    if seedTriggerDebounced.fell:
        seed()

    if mutateTriggerDebounced.fell:
        # Inverted, 0 to +5v CV:
        auxAdc = 4095 - readAdc(4, spi_bus, adcCS) + globalCvOffset

        sequenceRaw[clock] = auxAdc
        sequenceRaw2[clock] = auxAdc
        ledcontrol.blink(ledcontrol.mutateLed)

    if sampleInputs % sampleInputRateEncoder == 0:
        # Update the rotary encoder, this selects a new scale
        # or changes values when in tweak mode
        position = encoder.position
        if last_position is None or position != last_position:
            if position > last_position:
                if out2TweakMode:
                    # Do something
                    out2TweakValue[out2Mode] = constrain(out2TweakValue[out2Mode] + 1, 0, out2TweakMax[out2Mode])
                else:
                    # Scale goes up
                    currentScale += 1
            elif position < last_position:
                if out2TweakMode:
                    # Do something
                    out2TweakValue[out2Mode] = constrain(out2TweakValue[out2Mode] - 1, 0, out2TweakMax[out2Mode])
                else:
                    # Scale goes down
                    currentScale -= 1

            if out2TweakMode:
                # Do something
                ledcontrol.set7Seg(out2TweakValue[out2Mode])
            else:
                currentScale = constrain(currentScale, 0, len(targetScales)-1)
                ledcontrol.set7Seg(currentScale)
                encoderUpdated = True

            last_position = position

    if sampleInputs % sampleInputRateLed == 0:
        ledcontrol.update()

    ledcontrol.update7Seg()

    if sampleInputs % sampleInputRate == 0:
        updateButtons()

        if seedSwitch.pressed:
            seed()

        if mutateSwitch.pressed:
            sequenceRaw[clock] = random.randint(0, 4095)
            sequenceRaw2[clock] = random.randint(0, 4095)
            ledcontrol.blink(ledcontrol.mutateLed)

        # Long press only does something in modes 0 & 1
        if (out2Mode == 0 or out2Mode == 1) and modeButton.long_press:
            out2TweakMode = not out2TweakMode
            if out2TweakMode:
                # Entering tweak mode
                ledcontrol.set7Seg(out2TweakValue[out2Mode])
            else:
                ledcontrol.set7Seg(currentScale)
            ledcontrol.setTweakEnabled(out2TweakMode)

        # Switch out2 mode:
        if not out2TweakMode and modeButton.short_count != 0:
            out2Mode = (out2Mode+1)%3 # Values 0, 1, 2
            ledcontrol.setMode(out2Mode)


        if encoderSwitch.long_press:
            shuffleMode = not shuffleMode
            ledcontrol.setShuffleEnabled(shuffleMode)
            if not shuffleMode:
                targetScaleFullShuffled = list(targetScaleFull)
                targetScaleFullShuffledMv = memoryview(array.array('i', targetScaleFullShuffled))

        if shuffleMode and encoderSwitch.short_count != 0:
            targetScaleFullShuffled.sort(key=lambda x: random.random())
            targetScaleFullShuffledMv = memoryview(array.array('i', targetScaleFullShuffled))
    sampleInputs += 1

    if not (clockSwitch.pressed or clockTriggerDebounced.fell):
        continue

    updateButtons()

    if encoderUpdated:
        targetScaleFull = targetScales[currentScale]
        targetScaleFullShuffled = list(targetScaleFull)
        targetScaleFullShuffledMv = memoryview(array.array('i', targetScaleFullShuffled))
        encoderUpdated = False

    # Update ADC values
    # Normal. CV values from ~0 to ~4090. 0 to +3.3v
    quantPotAdc = readAdc(5, spi_bus, adcCS) # 0-4096
    shiftPotAdc = readAdc(6, spi_bus, adcCS) # 0-4096
    rangePotAdc = readAdc(7, spi_bus, adcCS) # 0-4096

    print("quantPot: " + str(quantPotAdc))
    print("shiftPot: " + str(shiftPotAdc))
    print("rangePot:" + str(rangePotAdc))
    # As this is +/-, we need to invert and then shift.
    lengthAdc = map_range(readAdc(1, spi_bus, adcCS) + globalCvOffset, 0, 4095, 2048, -2048)

    # Oversample the length pot to try and smooth some noise
    lengthPotOversample = 0
    lengthPotOversample += lengthPot.value
    lengthPotOversample += lengthPot.value
    lengthPotOversample += lengthPot.value
    lengthPotOversample += lengthPot.value
    # lengthPotOversample += 1024 # This could be configurable, but for now it represents an error of 256 per reading
    # print("length pot value" + str(lengthPot.value))
    # print("length pot oversample" + str(lengthPotOversample))
    # print("length pot normalised" + str(((lengthPotOversample >> 2) >> 10)))

    # Update the maximum length (maxClock) based on the the length pot & length input
    # Note that length pot is 16 bits, length CV is 12 bits. Length(adc) may be negative to reduce the current length
    # print("lengthAdc" + str(lengthAdc))
    # print("lengthAdc" + str(lengthAdc/64))

    # Calculate max clocks for both CV and pot first:
    maxClockPot = int(constrain(((lengthPotOversample >> 2) >> 10), 1, 64))
    maxClockCv = int(constrain(lengthAdc / 64, -32, 32))

    # print("maxclockpot: " + str(maxClockPot))
    # print("maxclockcv: " + str(maxClockCv))

    maxClock = maxClockCv + maxClockPot
    # Old maxclock:
    # maxClock = int(constrain(((lengthPotOversample >> 2) >> 10) + (lengthAdc/64), 1, 64)) # >> 10 is /1024
    print("maxclock: " + str(maxClock))
    print("clock:" + str(clock))
    if clock >= maxClock or clock >= 64:
        clock = 0

    # -5 to +5v CV:
    shiftAdc = map_range(readAdc(2, spi_bus, adcCS) + globalCvOffset, 0, 4095, 2048, -2048)
    rangeAdc = map_range(readAdc(0, spi_bus, adcCS) + globalCvOffset, 0, 4095, 2048, -2048)
    quantAdc = map_range(readAdc(3, spi_bus, adcCS) + (globalCvOffset/2), 0, 4095, 1024, -1024)
    #print("Shift, quant, range")
    #print("shift: " + str(shiftAdc)) # Out by around 260
    #print("range: " + str(rangeAdc)) # Out by around 270
    #print("quant: " + str(quantAdc)) # Out by around 130 (Expected, this has half the range?)

    # Output 1:
    stepQuantized = quantize(sequenceRaw[clock])

    sequenceRaw3.push(dacLUT[stepQuantized])
    ltc2632.write(dacLUT[stepQuantized], ltc2632.ZERO)

    # Output 2:
    # Mode 0: Output semitones above
    if out2Mode == 0:
        if stepQuantized + out2TweakValue[out2Mode] >= dacLUTMax:
            stepQuantized -= out2TweakValue[out2Mode]
        else:
            stepQuantized += out2TweakValue[out2Mode]
        ltc2632.write(dacLUT[stepQuantized], ltc2632.ONE)
    # Mode 1: Output the previous sequence, but offset
    elif out2Mode == 1:
        ltc2632.write(sequenceRaw3.get(out2TweakValue[out2Mode]), ltc2632.ONE)
    # Mode 2: Output a whole other sequence
    elif out2Mode == 2:
        stepQuantized = quantize(sequenceRaw2[clock])
        ltc2632.write(dacLUT[stepQuantized], ltc2632.ONE)

    ledcontrol.blink(ledcontrol.clockLed)

    clock += 1
