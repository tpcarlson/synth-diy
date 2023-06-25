# Sycamore

##### What is this?

Sycamore is a looping quantized sequencer with up to 64 steps, and up to 100 scales. Sycamore allows for CV control over many of its internal parameters including the loop length, range, and note range in a scale to be quantized to.

##### How much power does it use?

(TODO: Add power draw for v1.1)

(eg.) As measured by the joranalogue Test 3, around x mA on +12v and y mA on -12v at peak. The 5v rail is unused.

##### Where does the design come from?

The original panel design and concept came from the Mutable Instruments [cancelled projects](https://pichenettes.github.io/mutable-instruments-documentation/trivia_and_history/cancelled_projects/) page, and I made some tweaks to get the CV inputs and knob layout to align a little better.

Sycamore also has a few tricks up its sleeve to make it a little more playable, including shuffling the notes in the scale, and changing the harmony or note lag of the second 1v/oct output.

##### Are there any rare/weird parts used?

Sycamore uses easy to find parts, with the possible exceptions of the LTC2632 DAC and the PCA9685 LED driver. The module also uses a Rasperry Pi Pico microcontroller board.

##### Are there any problems with the design?

As Sycamore's firmware runs on top of Circuitpython it's not the _fastest_ module in the world - the trigger inputs require a 5ms+ trigger, although you may get away with as little as 2ms. For most modules that produce triggers this is not a problem, though.

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Everything in this project is easy to source though, so you should not have any trouble.

##### Can I buy PCBs or a kit?

(Links)

##### Other resources

[Kit BOM](BOM.md)

[Firmware guide](FIRMWARE.md)

[Assembly guide](ASSEMBLY.md)

![multmult-panel](images/panel.png)