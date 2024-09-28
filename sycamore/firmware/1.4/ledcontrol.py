import pwmio
import board
import supervisor
from adafruit_pca9685 import PCA9685
from debug import timed_function
import busio
from micropython import const
import adafruit_ticks

class LedControl:
    """LED controller for Sycamore"""
    def __init__(self, i2c):
        # See update() for frequency details
        self.clockLed = pwmio.PWMOut(board.GP17, frequency = 10000)
        self.seedLed = pwmio.PWMOut(board.GP18, frequency = 10000)
        self.mutateLed = pwmio.PWMOut(board.GP9, frequency = 10000)
        self.modeLed1 = pwmio.PWMOut(board.GP6, frequency = 10000)
        self.modeLed2 = pwmio.PWMOut(board.GP7, frequency = 10000)
        self.modeLed3 = pwmio.PWMOut(board.GP8, frequency = 10000)

        # This would be neater as a Dictionary, but
        # PWMOut doesn't have a __hash__!
        self.lastClock = adafruit_ticks.ticks_ms()
        self.lastSeed = adafruit_ticks.ticks_ms()
        self.lastMutate = adafruit_ticks.ticks_ms()

        self.ledButtonOnDurationMs = const(50)
        self.ledButtonBrightness = const(65535) # no PWM
        self.ledModeBrightness = const(2 ** 15)

        # 7-segment display brightness
        self.segMaxBrightness = const(0xCFFF)
        self.segMinBrightness = const(0xFFFF)

        # 7-segment display font info
        # Somewhat normal, ordered ABCDEFG DP
        self.sevenSegRight  = { 0: 0b11111100, 1: 0b01100000, 2: 0b11011010, 3: 0b11110010, 4: 0b01100110, 5: 0b10110110, 6: 0b10111110, 7: 0b11100000, 8: 0b11111110, 9: 0b11110110 }
        # Wacky. Ordered AFBGCE DP D
        self.sevenSegLeft = { 0: 0b11101101, 1: 0b00101000, 2: 0b10110101, 3: 0b10111001, 4: 0b01111000, 5: 0b11011001, 6: 0b11011101, 7: 0b10101000, 8: 0b11111101, 9: 0b11111001 }

        self.i2c = i2c

        # LED controller
        self.pca = PCA9685(i2c)
        self.pca.reset()
        self.pca.frequency = 1526 # Max PWM freq

        self.currentTime = None
        self.toDisplay = None

        scaleString = ""
        self.digits = [0] * 2
        self.digitsUpdated = False
        self.digitUpdateNum = 0

        self.digitLookup = [[0,0]] * 99
        for i in range(99):
            scaleString = str(i)
            # Pad to 00
            if i <= 9:
                scaleString = "0" + scaleString

            self.digitLookup[i] = [int(scaleString[0]),int(scaleString[1])]

        for i in range(16):
            self.pca.channels[i].duty_cycle = 0xFFFF # Reasonable brightness

    def setMode(self, mode: int):
        self.modeLed1.duty_cycle = mode != 0 or self.ledModeBrightness
        self.modeLed2.duty_cycle = mode != 1 or self.ledModeBrightness
        self.modeLed3.duty_cycle = mode != 2 or self.ledModeBrightness

    # Flag that the LED should be on
    def blink(self, pin: pwmio.PWMOut):
        if pin == self.clockLed:
            self.lastClock = adafruit_ticks.ticks_ms() + self.ledButtonOnDurationMs
        elif pin == self.seedLed:
            self.lastSeed = adafruit_ticks.ticks_ms() + self.ledButtonOnDurationMs
        elif pin == self.mutateLed:
            self.lastMutate = adafruit_ticks.ticks_ms() + self.ledButtonOnDurationMs

    # Disable LEDs that should no longer be lit
    # @timed_function # 3-4ms(!) with a 500Hz PWM freq
    #                 # 0ms with a 10KHz PWM freq
    # Due to https://github.com/adafruit/circuitpython/pull/7299 the frequency of the PWM object should be high,
    # at least for slightly older CircuitPython versions.
    def update(self):
        self.currentTime = adafruit_ticks.ticks_ms()
        self.clockLed.duty_cycle = adafruit_ticks.ticks_less(self.lastClock, self.currentTime) or self.ledButtonBrightness
        self.seedLed.duty_cycle = adafruit_ticks.ticks_less(self.lastSeed, self.currentTime) or self.ledButtonBrightness
        self.mutateLed.duty_cycle = adafruit_ticks.ticks_less(self.lastMutate, self.currentTime) or self.ledButtonBrightness

    def isDigitsUpdating(self) -> bool:
        return self.digitsUpdated

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
    # @timed_function # 0-1ms
    def update7Seg(self):
        if self.digitsUpdated:
            self.toDisplay = self.sevenSegRight[self.digits[0]]

            if self.digitUpdateNum == 0:
                self.set7SegElement(0b10000000, 8, self.toDisplay)
            if self.digitUpdateNum == 1:
                self.set7SegElement(0b01000000, 9, self.toDisplay)
            if self.digitUpdateNum == 2:
                self.set7SegElement(0b00100000, 11, self.toDisplay)
            if self.digitUpdateNum == 3:
                self.set7SegElement(0b00010000, 15, self.toDisplay)
            if self.digitUpdateNum == 4:
                self.set7SegElement(0b00001000, 14, self.toDisplay)
            if self.digitUpdateNum == 5:
                self.set7SegElement(0b00000100, 10, self.toDisplay)
            if self.digitUpdateNum == 6:
                self.set7SegElement(0b00000010, 12, self.toDisplay)

            self.toDisplay = self.sevenSegLeft[self.digits[1]]
            if self.digitUpdateNum == 7:
                self.set7SegElement(0b10000000, 0, self.toDisplay)
            if self.digitUpdateNum == 8:
                self.set7SegElement(0b01000000, 1, self.toDisplay)
            if self.digitUpdateNum == 9:
                self.set7SegElement(0b00100000, 2, self.toDisplay)
            if self.digitUpdateNum == 10:
                self.set7SegElement(0b00010000, 3, self.toDisplay)
            if self.digitUpdateNum == 11:
                self.set7SegElement(0b00001000, 4, self.toDisplay)
            if self.digitUpdateNum == 12:
                self.set7SegElement(0b00000100, 5, self.toDisplay)
            if self.digitUpdateNum == 13:
                self.set7SegElement(0b00000001, 7, self.toDisplay)

            self.digitUpdateNum += 1
            if self.digitUpdateNum == 14:
                self.digitsUpdated = False
                self.digitUpdateNum = 0

    def setTweakEnabled(self, enabled: bool) -> None:
        if enabled:
            self.pca.channels[6].duty_cycle = self.segMaxBrightness # 6 is the right DP channel
        else:
            self.pca.channels[6].duty_cycle = self.segMinBrightness

    def setShuffleEnabled(self, enabled: bool) -> None:
        if enabled:
            self.pca.channels[13].duty_cycle = self.segMaxBrightness # 13 is the left DP channel
        else:
            self.pca.channels[13].duty_cycle = self.segMinBrightness

    def set7SegElement(self, mask: int, channel: int, toDisplay: int):
        if mask & toDisplay and self.pca.channels[channel].duty_cycle != self.segMaxBrightness:
            self.pca.channels[channel].duty_cycle = self.segMaxBrightness # A
        elif self.pca.channels[channel].duty_cycle != self.segMinBrightness:
            self.pca.channels[channel].duty_cycle = self.segMinBrightness

    def set7Seg(self, scale: int) -> None:
        self.digits[0] = self.digitLookup[scale][0]
        self.digits[1] = self.digitLookup[scale][1]
        self.digitsUpdated = True
        self.digitUpdateNum = 0
