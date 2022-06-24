import digitalio

class Drum:
    def __init__(self, note, pin, description):
        self.note = note
        self.pin = pin
        self.description = description
        self.value = False
        self.hardwarePin = digitalio.DigitalInOut(self.pin)
        self.hardwarePin.direction = digitalio.Direction.INPUT
