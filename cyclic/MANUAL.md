# Cyclic - Manual

<!-- Check out the [Divergent Waves Dice Demo](https://www.youtube.com/watch?v=M2XgcmQ6p9Y) for a quick overview of everything! -->

##### Basic usage

Cyclic is a very simple machine - pass in triggers, add steps to a sequence, and get triggers and MIDI out.

As Cyclic doesn't have features beyond adding steps to the sequence, most of the complexity comes from the kinds of clocks patched in to its trigger inputs.

Cyclic has two rows of sockets to its rear side: The topmost sockets are inputs, with 8 trigger inputs and 1 MIDI input (Unused as of the current firmware). The bottommost sockets are outputs, with 8 trigger or gate outputs and 1 MIDI output.

To get started:

- Patch a clock or gate to one of the trigger inputs

- Patch the ouput underneath this input to another device or module

- Start the clock, and start adding steps to the sequence by pressing buttons!

- Press a button to add a step

- Press a button a second time to remove a step

- There are no other controls

##### Input normalling

Input triggers are copied down from tracks 1 through to track 8, stopping if there is anything patched into the input sockets in between. In Eurorack this is sometimes called "Normalling".

Practically speaking, this means you can patch a clock to input 1 and input 5 to split Cyclic into two separately clocked halves. The first input will control clocking of tracks 1, 2, 3, and 4, and the second input will control clocking of tracks 5, 6, 7, and 8.

##### MIDI output

Cyclic includes a TRS MIDI type A output. This is, by default, mapped to the drum pads on a Drumbrute Impact, but the mappngs can be changed...

##### Customising Cyclic

With the power cable removed, plug Cyclic in to your computer using the USB-C port on the rear. It should show up as a removable drive labelled CYCLIC.

Configuraion can then be modified by creating a file called settings.txt. An example settings file is below:

```
{
"channels":
[
  {"input":1, "note":36, "channel":10, "velocity":127, "length":100},
  {"input":2, "note":37, "channel":10, "velocity":127, "length":100},
  {"input":3, "note":42, "channel":10, "velocity":127, "length":100},
  {"input":4, "note":39, "channel":10, "velocity":127, "length":100},
  {"input":5, "note":40, "channel":10, "velocity":127, "length":100},
  {"input":6, "note":43, "channel":10, "velocity":127, "length":100},
  {"input":7, "note":44, "channel":10, "velocity":127, "length":100},
  {"input":8, "note":45, "channel":10, "velocity":127, "length":100}
]
}
```

The parameters are:

- **Input:** Which input/output pair of sockets this line refers to

- **Note:** Which MIDI note this line will trigger

- **Channel:** Which MIDI channel this line's note will be sent on

- **Velocity:** The MIDI velocity for the note being sent

- **Length:** The length, in milliseconds, for both trigger outputs and MIDI notes to be active for

MIDI-CC, program change, clocks and other MIDI miscellenea are currently unsupported, please get in touch if these are something you would like Cyclic to do (hello@divergentwaves.co.uk).
