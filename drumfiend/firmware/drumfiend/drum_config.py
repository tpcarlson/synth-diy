import drum
import board
import json
import time
import digitalio
import board

from drummer import Drummer

class DrumConfig(Drummer):
    def drumList(self):
        pinLookup = {1: board.D23,2: board.D2, 3: board.D22, 4: board.D3, 5: board.D21, 6: board.D4, 7: board.D20, 8: board.D5, 9: board.D19, 10: board.D6, 11: board.D18, 12: board.D7, 13: board.D17, 14: board.D8, 15: board.D16, 16: board.D9, 17: board.D15, 18: board.D10, 19: board.D12}
        try:
            with open('config.txt', 'r') as infile:
                config = json.load(infile)
                drumList = []
                for configLine in config.get("drums"):
                    note = configLine.get("note")
                    # Convert single notes to a list (Makes code.py a little cleaner)
                    if not isinstance (note, list):
                        note = [note]
                    programChange = configLine.get("programChange")
                    controlChange = configLine.get("controlChange")
                    pin = pinLookup[configLine.get("input")]
                    description = configLine.get("description", "")
                    startStop = configLine.get("startStop")
                    clock = configLine.get("clock")
                    arpMode = configLine.get("arpMode") # True or False
                    channel = configLine.get("channel")
                    drumList.append(drum.Drum(note=note, programChange=programChange, controlChange=controlChange, startStop=startStop, clock=clock, pin=pin, arpMode=arpMode, description=description, channel=channel))
                return drumList, config.get("midi_channel"), config.get("midi_note_off")
        except OSError as error:
            print(error)
            print("Could not read configuration file - missing config.txt?")
            self.sosLed()
        except ValueError as error:
            print(error)
            print("Invalid JSON syntax. Check the config.txt for mistakes")
            self.sosLed()

    def sosLed(self):
        led = digitalio.DigitalInOut(board.D11)
        led.direction = digitalio.Direction.OUTPUT
        while(True):
            # S
            self.blinkLetter(3, 0.1, led)
            time.sleep(0.25)
            # O
            self.blinkLetter(3, 0.25, led)
            time.sleep(0.1)
            # S
            self.blinkLetter(3, 0.1, led)
            time.sleep(0.25)
            # Gap between repeats
            time.sleep(0.5)

    def blinkLetter(self, repeats, delay, led):
        for i in range(repeats):
            led.value = True
            time.sleep(delay)
            led.value = False
            time.sleep(delay)
