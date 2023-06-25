# Sycamore - Assembly

##### PCB Versions and kits

PCB version 1.1 comes _without_ the DAC soldered.

PCB versions 1.2 and up come _with_ the DAC soldered.

Kits for Sycamore include the male and female headers for the Rasperry Pi Pico cut to size already.

##### Getting ready

First, gather together the tools you are going to use to assemble the module. At the bare minimum you should be able to do this with just a soldering iron, solder, and side cutters - but there are some additional tools that will make life easier:

- PCB vice or helping hands to hold the PCB in place
- Fan and absorbent material to get rid of solder/flux fumes
- Overhead lighting
- Silicone mat or scrap piece of wood to protect whatever surface you're soldering on
- Solder dispenser
- Tub to hold parts ready for soldering
- Multi-meter for continuity testing

<img src="images/1-tools.jpg" alt="tools"/>

Take a look through the bill of materials and make sure you have all the parts. I like to organise mine by putting them into tupperware or take-away boxes - if you do, just don't use them for food again afterwards.

###### Preparing the Pico

First, solder the male headers to the Pico. To hold everything in place, use a couple of female headers that you can place the male headers into temporarily.

<img src="images/2-teensy.jpg"/>

Now you can solder the male headers to the Pico. Remove the female headers once you're done and the Pico is good to go.

<img src="images/3-teensy.jpg"/>

If you are building this from your own parts, cut down some female headers to size (2 sets of 10 pins) to match the Pico, you'll use these a bit later. Kits will have these headers cut to size already.

<img src="images/10-teensy.jpg"/>

Connect the Pico to your computer and program it with the firmware. See the [FIRMWARE.md](FIRMWARE.md) guide for more details.

(TODO: The rest of the assembly instructions, photos)

##### LEDs

##### Rear components (Pico, power)

##### 7-segment display headers

##### Front panel parts (Pots, jacks, buttons)

##### 7-segment displays

##### Finishing off (Nuts, washers, light pipes, knobs)

###### Testing

No calibration is needed.

Check for shorts by probing the power header with your multimeter. There should be no continuity between +12v and ground, -12v and ground, or +12v and -12v.

With all the knobs at 12-o-clock, plug output 1 into a VCO. Press the clock button (It should briefly light) and listen to the VCO's output. If everything is correctly soldered and the firmware flashed, the pitch for the VCO should change as the notes output by Sycamore change.

See [MANUAL.md](MANUAL.md) for how to use the module.