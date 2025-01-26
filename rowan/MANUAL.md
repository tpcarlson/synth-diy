# Rowan - Manual

##### Installation

Make sure your modular system is powered off. Connect the power cable to the back of Rowan, and connect the 3-pin cable between Rowan and Sycamore. You may use either of the two 3-pin sockets of Rowan to connect up to Sycamore. If you already own another expander like Oak, chain from Sycamore to either Oak or Rowan and then onwards to the last module.

##### The basics

Rowan is the second expander for Sycamore, a dual random quantized looping sequencer. Rowan has a few main functions:

- Pairs of Chromatic and Unquantized outputs

- Dual trigger outputs on each step

- A scale display to show which notes are active

Rowan does not have any inputs.

##### Chromatic and Unquantized outputs

As Sycamore's sequence advances, Rowan outputs a Chromatic and Unquantized copy of steps. As Sycamore has a pair of outputs, Rowan is split into a left and right hand side, correspending to the Out 1 and Out 2 outputs of Sycamore.

As an example, with Sycamore playing a sequence in a major scale, the outputs might look like this:

| Sycamore | Chromatic | Unquantized       |
| -------- | --------- | ----------------- |
| C        | C         | C + 50 cents      |
| E        | E-flat    | E-flat + 20 cents |
| G        | G         | G - 5 cents       |

Both the unquantized and quantized outputs are intended to be run through another quantizer module, or they can be used on their own fed into a VCO (Although the unquantized outputs will be out of tune!).

##### Trigger outputs

As Sycamore is clocked, Rowan will output triggers. This works in a similar way to Oak's trigger outputs. Think of the trigger outputs like a duplicate of the clock input for Sycamore, but with a short (0-4ms) delay.

##### Scale display

Rowan's array of LEDs acts as a way to visualise what is happening to the scale as Sycamore and its expanders modify the allowed notes. Normally, these are lit in white. 

Try turning the Quantize knob to visualise how new notes are introduced - this should give a good feel for what Sycamore is doing as the Quantize control and CV are being changed. 

With the Quantize knob fully clockwise, try changing the scale with the scale control on Sycamore. The allowed notes will change as the scale does.

Finally, try shuffling the scale. If you have Oak, press the Scale Shuffle button. Alternatively, on Sycamore, the scale can be shuffled with a long press on the Scale encoder. Rowan's LEDs change from white to purple to indicate that the scale is in a shuffled state. When shuffled, all the notes of the current scale are randomly distributed across the Quantize knob, so all allowed notes are lit in this mode. Long-press the Scale encoder to exist scale shuffle mode.