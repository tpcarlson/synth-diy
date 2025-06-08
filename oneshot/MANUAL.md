# Oneshot - Manual

If you would prefer to watch a video of Oneshot, see https://www.youtube.com/watch?v=v3djYLEpFeE

##### Installation

- Power off the rack

- Connect the power cable to the rack's power supply/busboards, and to Oneshot's power connector

- Mount Oneshot in the rack, secure with two screws to the top and bottom of the module

- Power on the rack

##### Basics

Oneshot is a breakout for the [ElectricDruid Oneshot IC](https://electricdruid.net/product/oneshot-event-generator/). The Oneshot chip gives the Oneshot module 8 different waveforms, and control over the waveform selection, repeats, waveform duration, and the delay between repeats.

The Oneshot module also includes a small CV mixer section, allowing for patching of an external CV source like an LFO, noise, or another envelope to be mixed with the Oneshot output.

Oneshot's outputs are between 0 and about 6.5v. This is a little outside the usual range of 0-5v as seen on many digital modules, but allows for Oneshot to interface a little better with filters and VCAs that require just a bit more voltage to fully open up. Pass Oneshot's outputs through an attenuator or VCA to reduce the amplitude if you do need a different voltage range.

Oneshot can take a variety of trigger sources, all the way from slow LFOs up to low audio rate.

##### Controls & CV input detail

- Arcade button: Immediately trigger a new Oneshot wave. If there is a wave already being output, this will reset back to the start of the wave

- Waveform: Change between waveforms. If there is a wave already being output, changing waveform will switch to the new waveform immediately.

- Duration: Change the duration (And therefore the speed) of the Oneshot waves. Clockwise is faster, counter-clockwise slower.

- Repeats: Change the number of repeats for waves. Repeats are reduced amplitude versions of the original Oneshot wave.

- Delay: Change the delay between repeats. This will not do anything if repeats is fully counter-clockwise (ie. just one wave).

CV inputs for Waveform, Duration, Repeats and Delay all offset/add to the knob position and have a range of -5 to +5v. That is, if you feed a negative CV to a CV input, it's like turning a knob counter-clockwise.

##### Self-patching

While the Oneshot module isn't loopable on its own, patching the Mix or Out outputs back into the Trig input will give looping behaviour. Set the Repeats at about 9-o-clock (ie. not just one wave) and the module should retrigger. Depending on the waveform, this can get pretty weird, so do experiment!

Similarly, the Mix or Out output can be used to patch into the CV inputs, changing the wave as the wave is output. This can drastically change the shape of the output waveform and once again, it's best to experiment to find interesting ways to make use of this.