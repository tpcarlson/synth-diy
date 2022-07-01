# DrumFiend - Manual

## Basic usage

DrumFiend is very simple to use! Plug your TRS to MIDI cable into the MIDI socket, and then patch trigger sources into the inputs.

Trigger inputs are 'high' above about 2.5v, and 'low' below 2.4v.

DrumFiend is not clocked - you are free to send triggers at any time, and at almost any rate that you like, all the way up into low audio rates. Different drum machines react differently to really fast MIDI notes, it's worth experimenting...

## Customising the drum map

*Disconnect the DrumFiend module from your modular synth before modifying the firmware and configuration on the Teensy!*

Plug the Teensy into your computer. If programmed with the CircuitPython and DrumFiend software, a removable disk should appear with the label "CIRCUITPY".

<img src="images/firmware-1.png" title="" alt="" width="317">

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
