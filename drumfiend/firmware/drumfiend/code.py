import digitalio
import board
import busio
import adafruit_midi
import supervisor
import drum_config

from adafruit_midi.note_on import NoteOn

drummer = drum_config.DrumConfig()
drumConfig = drummer.drumList()
drums = drumConfig[0]
midi_channel = drumConfig[1]

# RX is unused
midiuart = busio.UART(board.TX, board.RX, baudrate=31250)
midi_io = adafruit_midi.MIDI(midi_out=midiuart, out_channel=midi_channel-1)

print("Pin assignments:")
for d in drums:
    print("Pin " + str(d.pin) + " -> MIDI " + str(d.note) + " (" + d.description + ")")
led = digitalio.DigitalInOut(board.D11)
led.direction = digitalio.Direction.OUTPUT

lastMidi = supervisor.ticks_ms()

# Poll for newly high pins. An alternative
# to polling would be to use interrupts.
while True:
    for d in drums:
        tempValue = d.hardwarePin.value
        if tempValue is True and d.value is False:
            midi_io.send(NoteOn(d.note))
            lastMidi = supervisor.ticks_ms()
        d.value = tempValue
        currentTime = supervisor.ticks_ms()
        # When currentTime overflows this'll break,
        # for one LED blink
        led.value = lastMidi + 250 > currentTime
