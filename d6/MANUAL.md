# Dice - Manual

TODO: Add diagrams for some of the sections

##### The basics

At its heart, Dice is a 6-channel clickless signal router. Inputs are fed to the outputs which may become active on rolling a dice. The behaviour of the dice rolling can be influenced with the buttons along the top, and the fader in the middle.

To begin, plug a signal into the input. This can be anything you like - triggers, gates, audio, or CV. Plug another cable from one of the outputs into another module. Toggle the buttons along the top so that none of the lights are lit, if they are already. Center the fader above the output jack sockets. With this basic setup complete, press the button corresponding to the output and the signal from the input will be routed to the output. Press it again and the signal will be cut.

With audio signals that cross 0v (This is *most* audio in Eurorack, but not all) the cuts in and out should be clickless.

##### Rolling a dice

Plug a clock, gate, or other CV source into the *roll* input. The module will roll a dice, toggling the output rolled. By default multiple outputs may be active at the same time, however different modes can change which outputs may be activated and deactivated, but we'll get to that later...

While the Dice module does not have a dedicated roll button, connecting a gate output to the *roll* input from something like Winterbloom's [Big Honking Button](https://winterbloom.com/shop/big-honking-button) will allow for manual, randomised control.

##### Rigging the dice

To influence which dice is rolled, use the central fader. When centered, the dice is fair, that is, all sides of the dice have an equal chance to be rolled. Moving the fader position over each output biases the dice to roll the corresponding number and those either side of it more often. To try this for yourself, with a clock running into the *roll* input, move the central fader to the left and right. About 50% of the time, the dice rolled will be the one over the output.

##### Exclusive mode

The simplest of the four buttons along the top, exclusive mode allows only one output to be active at a time. For example, with a clock running into the *roll* input, toggling the exclusive mode on will only allow for a single signal output to be active at once. Toggling it off again allows for more than one output to be active.

##### Skip mode

Skip mode prevents the same output from being activated more than once. Once a dice has been rolled, the output is marked with a red LED. Until the skip markers are cleared (Or skip mode is disabled), rolls of that number are ignored.

When combined with Exclusive mode, this allows for non-repeating but random sequences of output activations.

##### Reset

Clearing skip markers can be done in two ways; the easiest to understand is the Reset function. Reset will do two things: Clear the reset markers, and clear the outputs. This means Dice will be back to no outputs active and no skip markers active.

##### Auto-reset mode

The final mode, auto-reset, applies when in Skip mode. Rather than manually clearing the skip markers, auto-reset will automagically clear all skip markers and *toggle* outputs. For example, if all six outputs have skip markers but output one is deactivated, auto-reset will clear the skip markers, deactivate outputs two through five, and activate output one.

##### CV controls

Exclusive, Skip, and Auto-Reset modes all have CV inputs to toggle settings on and off. This means that when the CV input is high, the setting is flipped from on to off, or from off to on.

The Reset CV control allows for completely clearing the skip markers and all outputs, just like pressing the Reset button.

##### Correcting audio signals

If you have an audio input which does *not* cross 0v and has a DC component, you will need to pass the audio through a voltage offset module to enable clickless mutes and unmutes. Clickless muting depends on the audio signal crossing 0v. For example, you may wish to use the [Doepfer A-183-2](https://doepfer.de/a1832.htm).

##### Caveats for CV

Clickless muting and unmuting requires signals cross 0v within 50ms of being activated. For CV sources specifically, this means a slow LFO will remain active for an additional 50ms after an output has been deactivated, or may take up to 50ms to become active.

For more in-depth technical information about the zero-crossing behaviour, see the DS1882 datasheet https://datasheets.maximintegrated.com/en/ds/DS1882.pdf
