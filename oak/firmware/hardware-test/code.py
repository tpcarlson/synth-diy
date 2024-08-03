import digitalio
import board
import time

allButtons = []
scaleButton = digitalio.DigitalInOut(board.GP9)
loopButton = digitalio.DigitalInOut(board.GP8)
shiftLockButton = digitalio.DigitalInOut(board.GP2)
lengthLockButton = digitalio.DigitalInOut(board.GP1)
quantizeLockButton = digitalio.DigitalInOut(board.GP13)
rangeLockButton = digitalio.DigitalInOut(board.GP14)
allButtons.append(scaleButton)
allButtons.append(loopButton)
allButtons.append(shiftLockButton)
allButtons.append(lengthLockButton)
allButtons.append(quantizeLockButton)
allButtons.append(rangeLockButton)

for button in allButtons:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

allInputs = []
shuffleScaleIn = digitalio.DigitalInOut(board.GP24)
resetScaleIn = digitalio.DigitalInOut(board.GP21)
resetLoopIn = digitalio.DigitalInOut(board.GP20)
allInputs.append(shuffleScaleIn)
allInputs.append(resetScaleIn)
allInputs.append(resetLoopIn)

for button in allInputs:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

allOutputs = []
startOut = digitalio.DigitalInOut(board.GP23)
noteOut = digitalio.DigitalInOut(board.GP22)
stepOut = digitalio.DigitalInOut(board.GP19)
allOutputs.append(startOut)
allOutputs.append(noteOut)
allOutputs.append(stepOut)

for output in allOutputs:
    output.direction = digitalio.Direction.OUTPUT

outputsEnabled = True

allLeds = []
shuffleLed = digitalio.DigitalInOut(board.GP7)
resetScaleLed = digitalio.DigitalInOut(board.GP10)
resetLoopLed = digitalio.DigitalInOut(board.GP6)
startLoopLed = digitalio.DigitalInOut(board.GP11)
shiftLed = digitalio.DigitalInOut(board.GP3)
quantizeLed = digitalio.DigitalInOut(board.GP12)
lengthLed = digitalio.DigitalInOut(board.GP0)
rangeLed = digitalio.DigitalInOut(board.GP15)
allLeds.append(shuffleLed)
allLeds.append(resetScaleLed)
allLeds.append(resetLoopLed)
allLeds.append(startLoopLed)
allLeds.append(shiftLed)
allLeds.append(quantizeLed)
allLeds.append(lengthLed)
allLeds.append(rangeLed)

for led in allLeds:
    led.direction = digitalio.Direction.OUTPUT

ledBuiltIn = digitalio.DigitalInOut(board.GP25)
ledBuiltIn.direction = digitalio.Direction.OUTPUT

while True:
    print("=======")
    print("Buttons")
    print("=======")
    for item in allButtons:
        print(not item.value)

    print("======")
    print("Inputs")
    print("======")
    for item in allInputs:
        print(not item.value)

    outputsEnabled = not outputsEnabled
    print("Toggling outputs " + str(outputsEnabled))
    for item in allOutputs:
        item.value = outputsEnabled

    print("Toggling LEDs " + str(outputsEnabled))
    for item in allLeds:
        item.value = outputsEnabled

    ledBuiltIn.value = not outputsEnabled

    print("======================")

    time.sleep(0.5)
