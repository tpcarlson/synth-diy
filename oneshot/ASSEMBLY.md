# Oneshot (3U) - Assembly

##### PCB Versions and kits

PCB version 1.1 has the JST-XH header silkscreen on the wrong side of the PCB

##### Getting ready

First, gather together the tools you are going to use to assemble the module. At the bare minimum you should be able to do this with just a soldering iron & solder - but there are some additional tools that will make life easier:

- PCB vice or helping hands to hold the PCB in place
- Fan and absorbent material to get rid of solder/flux fumes
- Overhead lighting
- Silicone mat or scrap piece of wood to protect whatever surface you're soldering on
- Solder dispenser
- Tubs to hold parts ready for soldering
- Multi-meter for continuity testing
- Wire strippers

![parts](images/1-parts.jpg)

Take a look through the bill of materials and make sure you have all the parts. I like to organise mine by putting them into tupperware or take-away boxes - if you do too, just don't use them for food again afterwards.

###### Preparing the arcade button

Cut the crimped JST cable in half, then strip the wires on the cut ends. 

![parts](images/2-cut.jpg)

Solder the stripped ends to the button's contacts. Hooking the wire through the holes in the button contacts can make the soldering job a little easier.

![parts](images/3-solder.jpg)

Clip the crimped ends into the JST-XH socket, and then set the button and cable assembly aside.

![parts](images/4-jst.jpg)

###### Soldering the bottom PCB

All the SMT parts for the bottom PCB should already be soldered, but do take a quick look to make sure none are missing at this point.

On the rear of the bottom PCB, place and solder the 8-pin IC socket. Solder one pin of the socket before checking the socket lies flush with the PCB before solderng the rest.

![parts](images/5-socket.jpg)

Add the 2x5 2.54mm shrouded header, being careful to follow the silkscreen on the PCB. The notch in the header should be pointed down, toward the IC socket.

![parts](images/6-power.jpg)

###### Joining top and bottom PCBs

Prepare the headers and sockets that will join up the top and bottom PCBs. 

![parts](images/7-headers.jpg)

Slot the sockets into the rear PCB as indicated by the silkscreen, then carefully slide the top PCB into place. Solder one pin on each row and check the two PCBs are aligned correctly, with sockets and headers flush with their PCBs. 

This doesn't have to be perfect, but it looks much neater if the two boards are line up! Solder the rest of the pins on both the top and bottom PCBs, then separate the PCBs carefully setting the bottom PCB aside.

![parts](images/8-stack.jpg)

###### Top PCB parts

Place and solder the 3 resistors on the top PCB. I find it easiest to solder these partly from the top side, just soldering one pin of the standing resistors before flipping the top PCB over and soldering the other.

![parts](images/9-resist.jpg)

Place and solder the 2 pin JST-XH header next. On PCB revision 1.1, the silkscreen is on the wrong side of the PCB - make sure to place the JST-XH header on the same side as the pin headers that attach to the top PCB.

![parts](images/10-jst.jpg)

###### Front panel parts

Populate the PCB with the remaining through-hole parts, but DO NOT solder yet! This should include:

- 4 10k potentiometers

- 8 Thonkiconn mono sockets

- 3 LEDs

![parts](images/11-panel.jpg)

For the LEDs, please make sure to get the orientation correct as this can be quite difficult to fix once everything is soldered!

The "mix" and "out" LEDs should be placed with the long leg toward the top of the PCB, in the square pad.

The "trig" LED should be placed with the long leg toward the bottom of the PCB, in the round pad.

![parts](images/12-led.jpg)

Carefully thread the panel over the top components, then add a couple of washers and nuts to some of the potentiometers and sockets to hold everything in place.

![parts](images/13-panel.jpg)

Solder a single pin on the top-left and top-right Thonkiconn sockets, making sure to keep the sockets flush with the PCB and panel, and similarly solder a pin on the bottom-most potentiometers, making sure all the potentiometers turn freely.

For the LEDs, solder just one leg and make sure the LED is poking through the panel at the proper height.

Once you're happy, solder the rest of the pins & pads for the front panel parts.

![parts](images/14-solder.jpg)

###### Finishing touches

Add the rest of the washers and nuts to the potentiometers and sockets. Also add the potentiometer knobs at this point.

![parts](images/15-finish.jpg)

Thread the arcade button through the top hole, clipping the button into place.

![parts](images/16-button.jpg)

Plug in the JST-XH cable from the button to the top PCB, place the ElectricDruid OneShot IC in the IC socket to the rear PCB, and then join together the top and bottom PCBs.

![parts](images/17-done.jpg)

Congratulations, you're done!

![parts](images/18-reallydone.jpg)

###### Testing

Oneshot does not need any calibration.

With a multimeter, verify that there is no continuity between +12v and ground, -12v and ground, and +12v and -12v.

Plug Oneshot in to the rack, power the rack on, and hit the button. The "trig" LED should light when the button is pressed, and the other two LEDs should light as the CV waveform is output.

See [MANUAL.md](MANUAL.md) for how to use the module.