# Drumfiend

##### What is this?

A 19-channel trigger-to-MIDI processor. Send it triggers, and it'll send out MIDI notes.

##### How much power does it use?

As measured by the Joranalogue Test 3, around 40 mA. The 5v and 12v rails are unused. As LED start to light up, power use goes up a little bit - in the very worst case with all 20 LEDs lit, probably around 50mA.

##### Where does the design come from?

This one's all me! The basic MIDI-out (ie. two resistors) was taken from the excellent [Teensy MIDI documentation.](https://www.pjrc.com/teensy/td_libs_MIDI.html)

##### Are there any rare/weird parts used?

You will need a Teensy 3.2 (Or, untested but should work, Teensy-LC), and a Stereo Thonkiconn to build the module.

Most of the parts are SMT. Any transistor of the proper type ought to work, I picked the parts that I did based purely on what was available at JLCPCB.

##### Are there any problems with the design?

Nope, all works nicely!

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Everything in this project is easy to source though, so you should not have any trouble.

##### Can I buy PCBs or a kit?

Send me an email (twigathy+synth@gmail.com)...

##### Other resources

- [BOM](BOM.md)
- [Assembly guide](ASSEMBLY.md)

![logic-front](images/drumfiend.PNG)

