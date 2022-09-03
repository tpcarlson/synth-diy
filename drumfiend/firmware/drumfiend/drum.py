import digitalio

class Drum:
    def __init__(self, note, programChange, controlChange, startStop, clock, pin, description):
        self.note = note
        self.programChange = programChange
        self.controlChange = controlChange
        self.startStop = startStop
        self.clock = clock
        self.pin = pin
        self.description = description
        self.value = False
        self.hardwarePin = digitalio.DigitalInOut(self.pin)
        self.hardwarePin.direction = digitalio.Direction.INPUT
