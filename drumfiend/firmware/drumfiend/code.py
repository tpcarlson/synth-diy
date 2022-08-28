import digitalio
import board
import busio
import adafruit_midi
import supervisor
import drum_config

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.program_change import ProgramChange

drummer = drum_config.DrumConfig()
drumConfig = drummer.drumList()
drums = drumConfig[0]
midi_channel = drumConfig[1]
midi_note_off = True if drumConfig[2] == 1 else False

# RX is unused
midiuart = busio.UART(board.TX, board.RX, baudrate=31250)
midi_io = adafruit_midi.MIDI(midi_out=midiuart, out_channel=midi_channel-1)

print("Pin assignments:")
for d in drums:
    print("Pin " + str(d.pin) + " -> MIDI Note: " + str(d.note) + " (" + d.description + "), MIDI PC: " + str(d.programChange))
print("MIDI channel: " + str(midi_channel))
print("MIDI NoteOff: " + str(midi_note_off))
led = digitalio.DigitalInOut(board.D11)
led.direction = digitalio.Direction.OUTPUT

lastMidi = supervisor.ticks_ms()

# Poll for newly high pins. An alternative
# to polling would be to use interrupts.
while True:
    currentTime = supervisor.ticks_ms()
    for d in drums:
        tempValue = d.hardwarePin.value
        if tempValue is True and d.value is False:
            # MIDI Program change. Sent this before the MIDI notes!
            if d.programChange is not None:
                midi_io.send(ProgramChange(d.programChange))

            # MIDI notes:
            for note in d.note:
                if note is not None:
                    midi_io.send(NoteOn(note))

            lastMidi = currentTime
        if tempValue is False and d.value is True and midi_note_off is True:
            for note in d.note:
                if note is not None:
                    midi_io.send(NoteOff(note))

            lastMidi = currentTime
        d.value = tempValue
    # When currentTime overflows this'll break,
    # for one LED blink
    led.value = lastMidi + 250 > currentTime
