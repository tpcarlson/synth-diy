import digitalio

class Drum:
    def __init__(self, note, programChange, pin, description):
        self.note = note
        self.programChange = programChange
        self.pin = pin
        self.description = description
        self.value = False
        self.hardwarePin = digitalio.DigitalInOut(self.pin)
        self.hardwarePin.direction = digitalio.Direction.INPUT
