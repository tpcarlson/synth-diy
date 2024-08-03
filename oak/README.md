# Oak

##### What is this?

Oak is an expander for the looping, quantized sequencer Sycamore. Oak includes some controls to extend Sycamore's functionality, giving a little tighter control over the loop along with some additional useful outputs.

Note that the 1.0 revision (Prototype 1) is not yet ready for production. See the problems section below for details.

##### How much power does it use?

As measured by the joranalogue Test 3, at the very most 90 mA on +12v. The -12v and 5v rails are unused.

##### Where does the design come from?

While Sycamore's overall design primarily draws from the Mutable Instruments [cancelled projects](https://pichenettes.github.io/mutable-instruments-documentation/trivia_and_history/cancelled_projects/) page, Oak is entirely my own invention. 

The RP2040 schematic and PCB layout was partly lifted from the RP2040 example schematic and PCB ([Minimal-KICAD.zip](https://datasheets.raspberrypi.com/rp2040/Minimal-KiCAD.zip)).

##### Are there any rare/weird parts used?

Oak's parts are all in production today. The RP2040, crystal, and flash are the parts that are hardest to find.

##### Are there any problems with the design?

As of revision 1.0 (Prototype 1):

The LED brightness for the four top LEDs is significantly higher than for the LED buttons, however these are only supposed to be lit for a brief period. PWM for these LEDs can also help reduce percieved brightness.

The top half of the module bows away from the bottom half when topmost buttons are pressed. This will need resolving in a revision 1.1 with an additional hole in the main PCB, and a spacer to go between the PCB and panel. Rather than add an unsightly screw to the panel itself, I am considering using superglue to attach the spacer to the rear of the panel.

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Everything in this project is easy to source though, so you should not have any trouble.

##### Can I buy PCBs or a kit?

Coming soon...

##### Other resources

(BOM, assembly guide etc.)

![sycamore-panel](images/panel.jpg)