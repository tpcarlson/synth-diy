# DrumFiend - Manual

## Basic usage

DrumFiend is very simple to use! Plug your TRS to MIDI cable into the MIDI socket, and then patch trigger sources into the inputs.

Trigger inputs are 'high' above about 2.5v, and 'low' below 2.4v.

DrumFiend is not clocked - you are free to send triggers at any time, and at almost any rate that you like, all the way up into low audio rates. Different drum machines react differently to really fast MIDI notes, it's worth experimenting...

## Switching between MIDI-TRS versions

To switch between MIDI-A and MIDI-B versions, follow the silkscreen on the back of the module. For example, this module is set up for MIDI-A.

<img src="images/drumfiend-midi.png" title="" alt="" width="320">

## Configuring DrumFiend

*Disconnect the DrumFiend module from your modular synth before modifying the firmware and configuration on the Teensy!*

Plug the Teensy into your computer. If programmed with the CircuitPython and DrumFiend software, a removable disk should appear with the label "CIRCUITPY".

<img src="images/firmware-1.png" title="" alt="" width="320">

Inside this drive, look for the config.txt. You can open this in any text editor - notepad on Windows is fine, as is TextEdit on Mac.

###### Changing the MIDI channel

Near the top of the config.txt, the MIDI channel the DrumFiend sends MIDI notes on is specified:

```
"midi_channel": 10
```

Valid midi channels are 1 through 16. Most drum machines are on midi channel 10, but if you want to use DrumFiend to drive something on a different midi channel, this is where you should make the change.

###### Editing drum mappings

The rest of config.txt is taken up by the drum mappings. With the default firmware, DrumFiend will output notes for the DrumBrute Impact drum machine. However, if you want to change the mappings to match your drum machine you can do so here.

For example, to change the first input of DrumFiend to output MIDI note 42:

```
{"input":1,"note":42,"description":"Kick"},
```

Make sure to keep the quotes, commas, and brackets in the right place! The description field is only used for debugging purposes, but you may find it useful to fill in details about which drum the MIDI note corresponds to.

###### Using DrumFiend with a polysynth

As DrumFiend outputs MIDI notes, it's also possible to use it with a polysynth. To do this you will need to:

- Feed DrumFiend gates instead of triggers

- Set `"midi_note_off": 1` in the configuration file

An example MIDI mapping for a polysynth is included in the `configs` directory of the firmware. 

Just because DrumFiend can handle 19 triggers or gates at once does not necessarily mean your polysynth will! Check the manual for your syntheiszer to see how many notes of polyphony (Or paraphony) are supported.

Setting `"midi_note_off": 0` will cause notes to be held rather than released when the gate input is low. This can be useful if you wish to sustain notes for longer than the gate period.

###### Playing multiple notes from a single trigger

As well as the ability to play single notes (Drums or keys on a synth), DrumFiend may also play chords.

Configure DrumFiend's inputs like this:

`{"input":1,"note":[48,50,52],"description":"Chord"},`

###### Playing arpeggios from a single trigger

Similar to playing chords, you can play arpeggios from a single trigger.

Configure DrumFiend's inputs like this:

`{"input":1,"note":[48,50,52],"arpMode":1,"description":"Arp"}`

DrumFiend will cycle through the notes in the arp one by one. DrumFiend has no internal clock - send more triggers to advance the played note. As with playing single or multiple notes, send a gate rather than a trigger to hold each note of the arpeggio as it is played.

###### Setting a custom MIDI channel for triggers

The top-level ```midi_channel``` is a default for all triggers, but if you wish to send a trigger to a specific MIDI channel you can. For example, to send note 36 to channel 1:

```{"input":1,"note":36,"channel":1,"description":"Trig 1"}```

###### MIDI Program Change

DrumFiend also supports MIDI Program Change messages. These are usually used to swap between presets on a synthesizer.

Configure DrumFiend's inputs like this:

`{"input":1,"programChange":42,"description":"My wonderful preset"},`

You may also specify both a MIDI Program Change and notes in the same configuration line, however it depends on the device DrumFiend is connected to as to how well this will work!

###### MIDI Control Change

Control Change MIDI messages are also supported, with some limitations. As DrumFiend doesn't know the strength of triggers or gates, the MIDI CC values for a given pin are fixed. However, there's nothing stopping you from assigning multiple different trigger inputs to the same MIDI CC.

Configure DrumFiend's inputs like this:

    {"input":1,"description":"Resonance 0%","controlChange":{127:0}},
    {"input":2,"description":"Resonance 25%","controlChange":{127:25}},
    {"input":3,"description":"Resonance 50%","controlChange":{127:50}},
    {"input":4,"description":"Resonance 100%","controlChange":{127:100}},

The configuration format is MIDI CC _Parameter_ first, and MIDI CC _value_ second.

Or, if you wish to assign multiple MIDI CC values to a single trigger:

    {"input":5,"description":"Many CC changes","controlChange":{127:100, 32:40}},

###### MIDI Clock

DrumFiend may also act as a pass-through clock to send MIDI Clock instructions for synchronisation and clocking. As DrumFiend doesn't attempt to interpolate clocks, or act as a clock multiplier, you will need to provide a fast clock to its inputs to use this feature. Usually this is 24ppqn, but it depends on the device.

To enable MIDI Clock functionality for one of DrumFiend's inputs:

    {"input":7,"description":"TimingClock", "clock":1},

###### MIDI Start/Stop

MIDI Start/Stop messages may also be sent. This should be done alongside the MIDI Clock for most devices, with the device listening to MIDI Clock for sync.

To configure an input for MIDI start/stop, configure DrumFiend's inputs like this:

    {"input":5,"description":"MIDI Start", "startStop":"start"},
    {"input":6,"description":"MIDI Stop", "startStop":"stop"},

###### Resetting DrumFiend's configuration

Copy one of the configuration files from the `configs` directory of the firmware, renaming to config.txt. CircuitPython should pick up the file change and restart with the new configuration file.
