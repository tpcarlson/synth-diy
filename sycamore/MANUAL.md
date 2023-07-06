# Sycamore - Manual

TODO: This desperately needs pictures, and also the demo video filming.

## Overview

This is more of an in-depth look at the guts of Sycamore than you might want - if you would prefer to watch a video of it in action, see (TODO: Add video tutorial/demo link). Sycamore lends itself to experimentation and play, probably the best way to learn it is to get a sequence going and start fiddling!

Sycamore is, at its heart, a looping sequencer with quantization. The loop can have its lenth changed, and the notes produced can be shifted up and down along a scale. The scale can also be constrained to just a few notes, or the full scale.

Sycamore doesn't deal with transposition in the _usual_ way, but instead allows you to nudge notes along the scale, keeping everything in the same key.

The data that Sycamore stores about the current sequence means that it is always possible to transition from one set of knob settings to another and back again and get back to your original sequence, even as the loop length changes. All 64 steps in the sequence are persisted through sequence, quantisation, loop length and offset modifications.

## Controls

## Loops

The "Loop" control defines the length of the sequence. Sequences can be anywhere from 1 to 64 steps long. Sycamore does not show the loop length directly. 12-o-clock is length 32, with 64 and 1 step being fully clockwise and counter-clockwise respectively.

If you change the length of a sequence, notes that were _previously_ in the sequence are brought back into existence - unless the sequence has been seeded with "Seed"!

For example, you may start with a 5-step sequence, restrict the loop to 3-steps, and then go back to 5-steps:

| A   | B   | A   | C         | D         |
| --- | --- | --- | --------- | --------- |
| A   | B   | A   | (skipped) | (skipped) |
| A   | B   | A   | C         | D         |

## Range and offset

"Range" and "Offset" are related controls.

Range controls the number of semitones that the sequence may cover, with a maximum of 5 octaves. Dialling back Range allows to constrain all the way down to zero, only allowing for the root note in the lowest octave to be output.

As an example, you may have a 5-step sequence with range wide open and a chromatic scale that looks like this:

| C0  | C1  | C2  | C3  | C4  |
| --- | --- | --- | --- | --- |

Cutting range in half makes the notes look like this:

| C0  | F#0 | C1  | F#1 | C2  |
| --- | --- | --- | --- | --- |

Try to think of the F#s here more like "C and a half". To understand more about why Sycamore breaks notes up like this, we will need to dive more deeply into scales and quantisation.

## Scales and quantisation

Sycamore doesn't actually store note values. Instead, Sycamore stores a number per step in the sequence which can then get modified by the range, offset and quantise controls.

For example, taking another 5-step sequence, here is what the internals might look like.

| 3   | 14  | 22  | 61  | 33  |
| --- | --- | --- | --- | --- |
| C0  | D0  | E0  | C1  | G0  |

Sycamore has a number of scales defined which can constrain the notes to be quantised to. For example, here's the C major scale with some note values:

| C   | 0   |
| --- | --- |
| D   | 10  |
| E   | 20  |
| F   | 25  |
| G   | 35  |
| A   | 45  |
| B   | 55  |
| C   | 60  |

As you can see the notes don't necessary have to line up perfectly with the values given. Going back to the 5-step sequence above, this is what actually happens:

| 3   | 14  | 22  | 61  | 33  |
| --- | --- | --- | --- | --- |
| 0   | 10  | 20  | 60  | 35  |
| C0  | D0  | E0  | C1  | G0  |

Going back to the controls on the front panel, there are two ways to influence how quantisation works:

- Use the "Scale" encoder to choose one of the predefined scales, or a custom one if you have one defined. This defines the full set of notes to be used, for example the Major scale.

- Use the "Quantize" control to constrain the notes in the selected scale that may be chosen to quantize to. For example, you may choose the Major scale, but then restrict the quantization down to just three notes from the scale.

This is a bit clearer with an example! So, using C major again, let's go through what happens as the Quantize control changes.

If the Quantize control is turned to the point where three notes are allowed, being in a major scale will restrict quantization to a major scale. Very approximately:

| 0%  | 25% | 50% | 75% | 100% |
| --- | --- | --- | --- | ---- |
| C   | C   | C   | C   | C    |
|     |     | D   | D   | D    |
|     | E   | E   | E   | E    |
|     |     |     |     | F    |
|     | G   | G   | G   | G    |
|     |     |     | A   | A    |
|     |     | B   | B   | B    |
| C   | C   | C   | C   | C    |

Changing the scale from major to minor would change the E to an E-flat, but the rest of the structure would stay about the same.

With the Quantize control fully clockwise, all notes of the scale may be quantized to.

With the Quantize control at 12-o-clock, half of the notes of the scale are disallowed. This is done with some trickery to keep the sequences sounding as pretty as possible - For each scale, the notes that are kept tend to make up chords or harmonies of some kind.

Sycamore's firmware comes bundled with a number of scales already defined (45 at the time of writing), covering many of the scales on the [List of musical scales and modes](https://en.wikipedia.org/wiki/List_of_musical_scales_and_modes) wikipedia page.

## Quantisation ordering

Now that you know about scales, quantization, ranges and offsets, let's go through the full process of how a note gets quantized.

Let's bring back a 5-step sequence, represented as numbers, and once again using the major scale:

| 42     | 14     | 53      | 31     | 12     | Original sequence               |
| ------ | ------ | ------- | ------ | ------ | ------------------------------- |
| 32     | 11     | 40      | 23     | 9      | **Range ** @ 75%                |
| 92     | 71     | 100     | 83     | 69     | **Shift ** @ 100% (+1 octave)   |
| 95 (G) | 70 (D) | 100 (G) | 85 (F) | 70 (D) | **Quantize** @ 100% (All notes) |

Changing each of Range, Shift, and Quantize, or the scale to be quantized to, will change the notes that pop out at the end.

## Left-hand side buttons

Sycamore has three buttons along the left hand side of the module. These will light up whenever triggers are input and recognised, and also when pressed.

The buttons are:

- "Clock": Clocks the module, moving the sequence along one stop

- "Seed": Randomises all of the notes in the sequence

- "Mutate": Seed the *current step* with a new value, leaving the rest of the steps in the sequence as they are. Sycamore will generate a voltage for the mutated step internally

## Inputs and outputs

Sycamore's inputs and outputs are generally tied to the front panel controls.

Sycamore has three trigger inputs. These require a trigger length of 5ms or more, which _most_ external clocks should be happy to provide.

- "Clock" and "Seed" are the same as the buttons above

- "Mutate" is the same as the buttons above, but the mutate input takes in the voltage from the "Aux" input instead of generating a value for the step itself

Sycamore has several CV inputs:

- "Aux": Used with the "Mutate" trigger. This expects a 0-5v input.

- "Shift", "Length", "Quantize", and "Range"" are linked to the controls and can offset by half of a control's range. These inputs expect a voltage from -5v to +5v.

All of Sycamore's quantization inputs work best with long, slow LFOs, but also try noise or sample and held CV to get more dramatic and sudden changes in range or offset, for example. Using a more spiky CV input source for range works especially well when paired with Output 2's Delay mode.

## Output 2

Output 2's mode is controlled by the Output 2 Mode button. This allows for some interesting variations on the main output.

Output 2's mode is indicated by the three LEDs at the top-right of the panel. The top mode is Harmony, middle Delay, and bottom Independent. Only one of the three modes are allowed to be active at once - you may not have harmony _and_ delay active for example.

### Harmony

Sycamore uses the current sequence's notes to generate a harmony. This is a fifth (7 semitones) above the note being output in output 1.

For example, bringing back yet another 5-step sequence:

| Output 1 | C   | D   | E   | F   | G   |
| -------- | --- | --- | --- | --- | --- |
| Output 2 | G   | A   | B   | C   | D   |

### Delay

Sycamore keeps track of all the notes output to output 1, and delay writes these to output 2 delayed by a certain number of steps. By default, the delay is 4 steps.

For example, with another 5-step sequence, if we switched to Delay mode in time for the G to be output from output 1:

| Output 1 | C   | D   | E   | F   | G   |
| -------- | --- | --- | --- | --- | --- |
| Output 2 | -   | -   | -   | -   | C   |

Left looping, the sequence would then continue on like this:

| Output 1 | C   | D   | E   | F   | G   |
| -------- | --- | --- | --- | --- | --- |
| Output 2 | D   | E   | F   | G   | C   |

If you introduce new notes to Sycamore via the Seed or Mutate functions, output 2 will still remember what was played last.

Output 2 is not quantized and scaled in the same way as Output 1 is, so it will remember what was played through output 1 rather than changing based on panel settings.

### Independent

The last mode for Output 2 is Independent. This allows for Sycamore to output a completely separate sequence, but still has all the same scaling and quantization rules as Output 1.

With the Quantize control fully clockwise this can sound a little messy, it can be helpful to dial back the Quantize control if using independent mode.

## Tweak mode

Sycamore has some hidden tricks! Use these if you want to fiddle with some internals further....

### Scales

Long pressing and holding the Scale control bring you into scales tweak mode. The display will show a little dot on the left hand digit to show you're in scales tweak mode.

Short pressing the Scale knob again will shuffle the notes used for quantizing. For example, in the C Major scale, the first three notes are usually C E G (C Major chord). Pressing the Scale knob could change this to something completely different, like D F B. The notes chosen will still be part of whatever scale is active so everything stays in tune. Note that with the Quantize control all the way clockwise, you won't hear any difference as it will just choose all the notes in the scale anyway!

For example, here is what happens with quantize at about 25% (About 3 notes in the scale active), and scales tweak mode active, hopping into and out of scales tweak mode.

This can be a really nice way of changing up a sequence and then returning to the  original pattern, adding a little performability.

| Original | Pressed | Pressed | Original |
| -------- | ------- | ------- | -------- |
| C        |         | C       | E        |
|          | D       |         |          |
| E        | E       |         | E        |
|          |         | F       |          |
| G        |         |         | G        |
|          |         | A       |          |
|          | B       |         |          |

Short press the Scale knob to continue shuffling through different quantization variations. 

To exit Scale tweak mode and revert back to the original scale ordering, long press the Scale control.

### Output 2

Long press the Output 2 button to enter Output 2 tweak mode. The display will show a little dot on the right hand digit to show you're in tweak mode.

Output 2 has customisation, but only for the Harmony and Delay modes. 

For Harmony, you may _transpose_ the output by a number of semitones, up to 24 offset from Output 1. Turn the Scale encoder to change the semitones for output 2.

For Delay, you may change the delay offset from the default 4 up to 63 steps. Choose the offset amount with the Scale encoder. If you choose 00 as the offset, Output 2 will output the same notes as Output 1.

To exit Output 2 tweak mode, long press the output 2 button.

## Customisation

You will not need to touch the configuration in normal use, but for deeper configuration hackery, read on....

### Scales

Sycamore ships with a number of scales, but these can be customised if you wish! Plug the Rasperry Pi Pico on the back of the module (With the modular switched _off_) into your comptuer, then navigate to the removable drive that shows up. Under the "scales" you'll find the defined scales.

To define your own scale, you may either edit an existing scale or add a new text file with a new scale.

As an example, here's the Chromatic scale, 00:

```
{
    "notes": [0, 4, 7, 9, 11, 2, 5, 1, 3, 5, 6, 8, 10],
    "index": 0
}
```

You might notice these note numbers are out of order! This allows the quantization to choose "nice" notes when the quantize control is restricted.

Note numbers are defined in semitones along a scale:

| C   | C#  | D   | D#  | E   | F   | F#  | G   | G#  | A   | A#  | B   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  | 11  |

### Quantization/DAC lookups

Sycamore, by default, uses a lookup table to calculate the output voltages. Usually these should be perfectly OK as they are, but sometimes the outputs might be slightly non-linear. If you want to try changing the lookup table that gets used, modify "settings.txt" stored on the Rasperry Pi Pico. The `dacLookupTable` values there correspond to the DAC output values. Each entry is 68 or 69 apart.

You may also wish to change the lookup table if you want to try something microtonal or simply want to detune things a little!

### Restoring configuration to default

If you decide you want the original DAC lookup table or set of scales back again, delete the scales/ directory and settings.txt and re-copy them from the firmware ZIP.
