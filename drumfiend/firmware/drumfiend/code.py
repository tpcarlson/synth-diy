import digitalio
import board
import busio
import adafruit_midi
import supervisor
import drum_config

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.control_change import ControlChange
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop
from adafruit_midi.timing_clock import TimingClock

drummer = drum_config.DrumConfig()
drumConfig = drummer.drumList()
drums = drumConfig[0]
midi_channel = drumConfig[1]
midi_note_off = True if drumConfig[2] == 1 else False

# RX is unused
midiuart = busio.UART(board.TX, board.RX, baudrate=31250)
midi_io = adafruit_midi.MIDI(midi_out=midiuart, out_channel=midi_channel-1)

print("Pin Assignments:")
for d in drums:
    print("Pin " + str(d.pin) + " (" + d.description + ") -> MIDI Note: " + str(d.note) + ", Arp mode: " + str(d.arpMode) + ", MIDI PC: " + str(d.programChange) + ", MIDI CC: " + str(d.controlChange) + ", MIDI Start/Stop: " + str(d.startStop) + ", MIDI Clock: " + str(d.clock) + ", channel: " + str(d.channel))
print("MIDI Channel: " + str(midi_channel))
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
            # MIDI Program change. Send this before the MIDI notes!
            if d.programChange is not None:
                midi_io.send(ProgramChange(d.programChange))
            # MIDI Control Change (CC).
            if d.controlChange is not None:
                for ccEntry in d.controlChange:
                    if ccEntry is not None:
                        midi_io.send(ControlChange(ccEntry, d.controlChange[ccEntry]))
            # MIDI Start/stop messages.
            if d.startStop is not None:
                if d.startStop.lower() == "start":
                    midi_io.send(Start())
                elif d.startStop.lower() == "stop":
                    midi_io.send(Stop())

            # MIDI Clock
            if d.clock is not None:
                midi_io.send(TimingClock())

            # MIDI notes in arp mode:
            if d.arpMode == 1:
                # Arp mode sends the current note and increments, outside of arp mode this isn't required
                if d.note is not None:
                    if d.channel is None:
                        midi_io.send(NoteOn(d.note[d.currentNote]))
                    else:
                        midi_io.send(NoteOn(note=d.note[d.currentNote]),channel=d.channel-1)
                d.currentNote = (d.currentNote + 1) % len(d.note)
            else:
            # MIDI notes:
                for note in d.note:
                    if note is not None:
                        if d.channel is None:
                            midi_io.send(NoteOn(note))
                        else:
                            midi_io.send(NoteOn(note=d.note[d.currentNote]),channel=d.channel-1)

            lastMidi = currentTime
        if tempValue is False and d.value is True and midi_note_off is True:
            if d.arpMode == 1:
                arpNoteOffIndex = 0
                for note in d.note:
                    # MIDI NoteOff in arp mode shouldn't interrupt other played notes, just the last-played note
                    if note is not None and arpNoteOffIndex != d.currentNote:
                        if d.channel is None:
                            midi_io.send(NoteOff(note))
                        else:
                            midi_io.send(NoteOff(note),channel=d.channel-1)
                    arpNoteOffIndex = arpNoteOffIndex + 1
            else:
                for note in d.note:
                    if note is not None:
                        if d.channel is None:
                            midi_io.send(NoteOff(note))
                        else:
                            midi_io.send(NoteOff(note),channel=d.channel-1)

            lastMidi = currentTime
        d.value = tempValue
    # When currentTime overflows this'll break,
    # for one LED blink
    led.value = lastMidi + 250 > currentTime
