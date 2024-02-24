import pwmio
import board
import supervisor
from adafruit_pca9685 import PCA9685
import busio
from micropython import const
import adafruit_ticks

clockLed = pwmio.PWMOut(board.GP17)
seedLed = pwmio.PWMOut(board.GP18)
mutateLed = pwmio.PWMOut(board.GP9)
modeLed1 = pwmio.PWMOut(board.GP6)
modeLed2 = pwmio.PWMOut(board.GP7)
modeLed3 = pwmio.PWMOut(board.GP8)

# This would be neater as a Dictionary, but
# PWMOut doesn't have a __hash__!
lastClock = adafruit_ticks.ticks_ms()
lastSeed = adafruit_ticks.ticks_ms()
lastMutate = adafruit_ticks.ticks_ms()

ledButtonOnDurationMs = const(50)
ledButtonBrightness = const(65535) # no PWM
ledModeBrightness = const(2 ** 15)

# 7-segment display brightness
segMaxBrightness = const(0xCFFF)
segMinBrightness = const(0xFFFF)

# 7-segment display font info
# Somewhat normal, ordered ABCDEFG DP
sevenSegRight  = { 0: 0b11111100, 1: 0b01100000, 2: 0b11011010, 3: 0b11110010, 4: 0b01100110, 5: 0b10110110, 6: 0b10111110, 7: 0b11100000, 8: 0b11111110, 9: 0b11110110 }
# Wacky. Ordered AFBGCE DP D
sevenSegLeft = { 0: 0b11101101, 1: 0b00101000, 2: 0b10110101, 3: 0b10111001, 4: 0b01111000, 5: 0b11011001, 6: 0b11011101, 7: 0b10101000, 8: 0b11111101, 9: 0b11111001 }

# i2c. Swap bitbangio for board i2c in future rev.
i2c = busio.I2C(board.GP11, board.GP10) # Clock, Data

# LED controller
pca = PCA9685(i2c)
pca.reset()
pca.frequency = 1526 # Max PWM freq

# Globals to avoid allocations
currentTime = None

scaleString = ""
digits = [0] * 2
digitsUpdated = False
digitUpdateNum = 0

for i in range(16):
    pca.channels[i].duty_cycle = 0xFFFF #000 # Reasonable brightness

def setMode(mode: int):
    modeLed1.duty_cycle = mode != 0 or ledModeBrightness
    modeLed2.duty_cycle = mode != 1 or ledModeBrightness
    modeLed3.duty_cycle = mode != 2 or ledModeBrightness

# Flag that the LED should be on
def blink(pin: pwmio.PWMOut):
    if pin == clockLed:
        global lastClock
        lastClock = adafruit_ticks.ticks_ms() + ledButtonOnDurationMs
    elif pin == seedLed:
        global lastSeed
        lastSeed = adafruit_ticks.ticks_ms() + ledButtonOnDurationMs
    elif pin == mutateLed:
        global lastMutate
        lastMutate = adafruit_ticks.ticks_ms() + ledButtonOnDurationMs

# Disable LEDs that should no longer be lit
def update():
    currentTime = adafruit_ticks.ticks_ms()
    clockLed.duty_cycle = adafruit_ticks.ticks_less(lastClock, currentTime) or ledButtonBrightness
    seedLed.duty_cycle = adafruit_ticks.ticks_less(lastSeed, currentTime) or ledButtonBrightness
    mutateLed.duty_cycle = adafruit_ticks.ticks_less(lastMutate, currentTime) or ledButtonBrightness

# This is slightly cursed, but updating the 7 segment displays takes
# SEVERAL i2c operations, each of which means that the PCA9685 driver
# eats up a lot of time, taking up around 20ms(!) of processing with bitbangio
# on the prototype board, which is no good with 10ms clocks.
#
# Instead, update the digit segments one at a time and hope for the best, taking a couple
# of ms to update the display slowly over a few cycles of the main loop.
#
# This would be much less of an issue if CircuitPython supported the two cores
# on the pi pico, with clocks and other critical parts on one core and LED driving
# on another. See https://github.com/adafruit/circuitpython/issues/4106.
def update7Seg():
    global digitsUpdated
    if digitsUpdated:
        toDisplay = sevenSegRight[digits[0]]
        global digitUpdateNum

        if digitUpdateNum == 0:
            set7SegElement(0b10000000, 8, toDisplay)
        if digitUpdateNum == 1:
            set7SegElement(0b01000000, 9, toDisplay)
        if digitUpdateNum == 2:
            set7SegElement(0b00100000, 11, toDisplay)
        if digitUpdateNum == 3:
            set7SegElement(0b00010000, 15, toDisplay)
        if digitUpdateNum == 4:
            set7SegElement(0b00001000, 14, toDisplay)
        if digitUpdateNum == 5:
            set7SegElement(0b00000100, 10, toDisplay)
        if digitUpdateNum == 6:
            set7SegElement(0b00000010, 12, toDisplay)

        toDisplay = sevenSegLeft[digits[1]]
        if digitUpdateNum == 7:
            set7SegElement(0b10000000, 0, toDisplay)
        if digitUpdateNum == 8:
            set7SegElement(0b01000000, 1, toDisplay)
        if digitUpdateNum == 9:
            set7SegElement(0b00100000, 2, toDisplay)
        if digitUpdateNum == 10:
            set7SegElement(0b00010000, 3, toDisplay)
        if digitUpdateNum == 11:
            set7SegElement(0b00001000, 4, toDisplay)
        if digitUpdateNum == 12:
            set7SegElement(0b00000100, 5, toDisplay)
        if digitUpdateNum == 13:
            set7SegElement(0b00000001, 7, toDisplay)

        digitUpdateNum += 1
        if digitUpdateNum == 14:
            digitsUpdated = False
            digitUpdateNum = 0

def setTweakEnabled(enabled: bool) -> None:
    if enabled:
        pca.channels[6].duty_cycle = segMaxBrightness # 6 is the right DP channel
    else:
        pca.channels[6].duty_cycle = segMinBrightness

def setShuffleEnabled(enabled: bool) -> None:
    if enabled:
        pca.channels[13].duty_cycle = segMaxBrightness # 15 is the left DP channel
    else:
        pca.channels[13].duty_cycle = segMinBrightness

def set7SegElement(mask: int, channel: int, toDisplay: int):
    if mask & toDisplay and pca.channels[channel].duty_cycle != segMaxBrightness:
        pca.channels[channel].duty_cycle = segMaxBrightness # A
    elif pca.channels[channel].duty_cycle != segMinBrightness:
        pca.channels[channel].duty_cycle = segMinBrightness

# Update the 2-digit 7-segment display
def set7Seg(scale: int) -> None:
    digitNum = 0
    global scaleString
    scaleString = str(scale)
    # Pad to 00
    if scale <= 9:
        scaleString = "0" + scaleString

    for digitStr in scaleString:
        digit = int(digitStr)
        digits[digitNum] = digit

        digitNum += 1

    global digitsUpdated
    digitsUpdated = True
    global digitUpdateNum
    digitUpdateNum = 0
