# Rowan - Assembly

##### PCB Versions and kits

PCB version 1.0 - Initial prototype

##### Getting ready

First, gather together the tools you are going to use to assemble the module. At the bare minimum you should be able to do this with just a soldering iron & solder - but there are some additional tools that will make life easier:

- PCB vice or helping hands to hold the PCB in place
- Fan and absorbent material to get rid of solder/flux fumes
- Overhead lighting
- Silicone mat or scrap piece of wood to protect whatever surface you're soldering on
- Solder dispenser
- Tubs to hold parts ready for soldering
- Multi-meter for continuity testing

Take a look through the bill of materials and make sure you have all the parts. I like to organise mine by putting them into tupperware or take-away boxes - if you do too, just don't use them for food again afterwards.

![parts](images/1-parts.jpg)

##### (Big section)

(Paragraph)

![parts](images/2-jst.jpg)

##### Check for shorts

Check for short circuits by probing the power header with your multimeter. There should be no continuity between +12v and ground, -12v and ground, or +12v and -12v.

##### Firmware

To flash Rowan's RP2040, follow the [FIRMWARE](FIRMWARE.md) guide. If you have an older Sycamore revision, you may also need to update the firmware for Sycamore for the two modules to talk to each other.

###### Testing

No calibration is needed.

Ensuring the power is turned off first, plug the module into your Eurorack. Connect Rowan to Sycamore with the included 3 pin JST-XH cable, and turn on power to the rack. If you want to use Rowan and Oak together, daisy-chain from Sycamore Oak and onward to Rowan (Or Rowan to Oak, the order doesn't matter!).

Power up the modules, and verify that Rowan's LEDs show the current scale. Try turning Sycamore's Quantize knob or passing an LFO to the Quantize CV input and check that the display changes.

Clock Sycamore, and check that the trigger outputs for Rowan work. Verify that the four pitch CV outputs (Two unquantized, and two chromatically quantized) work too.

See [MANUAL.md](MANUAL.md) for how to use the module - however, you might not need to, Rowan is quite simple!