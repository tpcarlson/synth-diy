# Cyclic - Assembly

NOTE: This needs photos! The build guide below documents how the first Cyclic went together.

##### Getting ready

First, gather together the tools you are going to use to assemble Cyclic. At the bare minimum you should be able to do this with just a soldering iron, solder, and side cutters - but there are some additional tools that will make life easier:

- PCB vice or helping hands to hold the PCB in place
- Fan and absorbent material to get rid of solder/flux fumes
- Overhead lighting
- Silicone mat or scrap piece of wood to protect whatever surface you're soldering on
- Solder dispenser
- Tub to hold parts ready for soldering
- Multi-meter for continuity testing
- Flux and desoldering braid
- Mini hex driver (For m2 screws)
- Heat-set insert tool for the soldering iron (If building your own case)
- Cyanoacetate superglue (If building your own case)

Take a look through the [bill of materials](BOM.md) and make sure you have all the parts. I like to organise mine by putting them into tupperware or take-away boxes - if you do, just don't use them for food again afterwards.

(Photo of TH parts in a box)

##### Case printing

For full kits, a case will be provided. If you just have the PCBs, follow along...

Cyclic's case is printable in two halves, with hardware to affix the two halves together. The two halves need to be printed in a slightly different way and might take some tweaking to get a good result, depending on your 3D printer.

**Bottom**: This includes the base plate and supports for the PCB, sides, and rear. Print this with the base plate face down, ie. in the orientation you'd expect to use Cyclic.

**Top**: This includes the front, top, riser for the socket cover, and the socket cover. this needs to be printed with the side facing the bottom of the print bed, from left to right or right to left. Attempting to print the top of the case in the orientation you expect to use Cyclic will result in using a LOT of support material.

**Supports**: Two small supporting pieces to secure the top and bottom portions together.

While not completely necessary, printing a **Jig** consisting only of the back panel can be very helpful when trying to get the mono and stereo sockets to sit properly.

##### Case preparation

Add heat-set inserts to the following places:

- 1 in each of the supports in the corners of the base plate (4 total)

- 2 each on the left and right hand sides of the base plate (4 total)

- 1 in each support piece (2 total)

Once done, superglue the support pieces to the top case. Small ribs indicate where the support pieces should be placed. 

Make sure the two halves slot together well, and clean up any flash or other 3D printing gunk (Stringing and so on) that has found its way onto your prints.

###### Preparing Cyclic's firmware

Plug the main PCB in to your computer using a USB-C cable. This can be a USB-C to USB-C or a USB-C to USB-A, as long as the cable can be used for data.

Wait for the removable drive to show up, then copy and paste the firmware hex file onto the drive. The removable drive should vanish and be replaced with a drive labelled "CYCLIC".

If Cyclic has previously had another firmware installed, hold down the "BOOTSEL" button while plugging it in to get the removable drive back again.

The latest firmware is [version 1.1](firmware/1.1/cyclic/cyclic-1.1.zip).

###### Top PCB

Using a print of the back panel as a jig for this helps keep everything aligned and is recommended.

Solder in the following order:

- 8 pin IC socket

- 2x tactile switches

- 8x mono (red) and 1x stereo (blue) sockets. The blue socket should be closest to the IC socket.

Now trim the sockets as close you can to the PCB. Flush cutters are definitely recommended here. You may wish to touch up the soldering after doing this, but be careful not to add too much as the top and bottom sockets sit on top of each other.

Add the optoisolator IC to the socket, taking care to follow the silkscreen or IC socket for orientation.

###### Bottom PCB

Again using the rear panel jig is strongly recommended to try and keep everything lined up.

Solder in the following order:

- 8x mono (red) and 1x stereo (blue) sockets. The blue socket should be closest to the USB-C port on the bottom PCB

- Power socket

Unlike the top socket there is no need to trim the pins on the rear, there's lots of clearance on the bottom side.

###### Connecting the PCBs together

Locate the standoffs and screws. These will go between the two boards and keep them well attached to one another. To start, add the standoff on top of the bottom PCB, screwing it in to place from the underside.

Find the pinheader and pinsockets, and put them together. Place the combined header & socket onto the bottom PCB in the indicated spots, with the headers facing up.

Now, carefully thread the smaller top PCB onto the pinheaders. This can be a little tricky to get right as the top sockets need to fit perfectly onto the bottom sockets.

Using the back panel as a jig, or the jig if you printed one specifically, ensure the top and bottom sets of sockets, the USB port, tactile buttons, and power socket all line up correctly. If there doesn't seem to be enough pinheader to go through the board to solder to, you will need longer pinheaders! If there's too much pinheader, take the boards apart and trim a little off the top before continuing.

Screw the two PCBs together using the remaining screws for the standoffs.

Solder one pin of each pinheader from the top, and another one from the pinsocket from the bottom, and check to make sure it's all straight. Screwing together the PCBs helps, but sometimes these things can get a little wonky.

Once you're happy, solder the remaining pinheader and pinsocket pins.

All the soldering is now complete!

###### Final assembly

Place the combined top and bottom PCBs onto the set of plastic standoffs at the bottom of the case, threading sockets through the holes in the rear of the case.

Place the 8 4x4 button pads on top of the PCB, making sure to align the little nubs on the underside of the button pads with holes in the PCB.

Screw through the button pads into the 4 heat-set inserts embedded in the plastic standoffs. The pads have a small hole to fit a screw through. Don't overtighten as this might damage the button pads, just make sure the button pad PCB is held in place.

Thread the top case onto the bottom case, taking care to align the button pad holes in the top case with the pads themselves.

Using more screws, secure the sides (4 screws total) and the rear (Another 2 screws).

Finally, add washers and nuts to the audio sockets to the rear.

###### Calibration and testing

Cyclic requires no calibration.

Power up Cyclic by connecting either the USB or power socket.

Patch a clock into the top-left input socket (As seen from the front of the device). With the clock enabled, the play-head for the sequencer will sweep from left to right.

Patch the trigger output from the socket underneat that input to anything that'll take a trigger. That might be another sequencer, a drum module, a voice, or an envelope.

Activate steps on the first track and ensure the trigger outputs as expected.

Repeat for the rest of the trigger inputs and outputs.

To test the MIDI output, patch a TRS cable to any MIDI-enabled device. By default, Cyclic is programmed to work with the DrumBrute Impact and will send out notes on channel 10. Activating, and then triggering, steps on any track should send out MIDI.
