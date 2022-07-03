# DrumFiend - Assembly

##### PCB Versions and kits

PCB version 1.0 has _green_ solder mask and silkscreen for a Teensy 3.2. PCB version 1.1 has _black_ solder mask and silkscreen for a Teensy 4.0. Other than the PCB colours and Teensy silkscreening the two are electrically identical.

Kits for DrumFiend include the male and female headers cut to size already.

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

###### Preparing the Teensy

First, solder the male headers to the Teensy. To hold everything in place, use a couple of female headers that you can place the male headers into temporarily.

For PCB versions 1.1 onwards, a Teensy 4.0 is used instead of Teensy 3.2.

<img src="images/2-teensy.jpg"/>

Now you can solder the male headers to the Teensy. Remove the female headers once you're done and the Teensy is good to go.

<img src="images/3-teensy.jpg"/>

If you are building this from your own parts, cut down some female headers to size (14 pins) to match the Teensy, you'll use these a bit later. Kits will have these headers cut to size already.

<img src="images/10-teensy.jpg"/>

Connect the Teensy to your computer and program it with the firmware. See the [FIRMWARE.md](FIRMWARE.md) guide for more details.

###### Back board (Power and MIDI IO)

Start off by soldering the "lowest" components on the back board. That means we'll start with the reverse-polarity protection diode. This is a polarity sensitive part, so make sure you get the white stripe on the diode to align with the silkscreen.

<img src="images/4-power.jpg"/>

Next up are the pair of resistors for the MIDI output.

<img src="images/5-midi.jpg"/>

And now the pair of capacitors for the 5v supply.

<img src="images/6-caps.jpg"/>

Depending on your 5v regulator (78L05), you may next need to splay the legs of it a little, like this:

<img src="images/7-5v.jpg"/>

Thread the legs through the place on the board for the regulator, being mindful of the silkscreened flat edge. This is a polarity sensitive part, it needs to go the right way around!

<img src="images/8-5v.jpg"/>

Next, solder the pair of 10uF electrolytic capacitors. These are again polarity-sensitive, so make sure the silkscreen lines up with what's marked on your capacitors.

<img src="images/9-caps.jpg"/>

Now add the 3 pin headers to the MIDI type selector. These should go with the long part sticking out so you can get to them from the back of the module.

<img src="images/11-midi.jpg"/>

With the taller components now soldered, go ahead and solder in the power connector. Follow the silkscreen to make sure the orientation is correct, and if you're not sure verify with a power cable that the red stripe on the cable matches the -12v silkscreen.

<img src="images/12-power.jpg"/>

Solder a couple of the pins on the power connector before checking it lies flat. If it's not quite right, just head up the pad again and push the power connector into place. This is much more difficult to do with all 10 pins soldered, so it's best to get the alignment right now.

<img src="images/13-power.jpg"/>

With the power header soldered, solder the last tall thing on the board - the Teensy. Insert the male headers into the female headers prepared earlier and add these to the board. The Teensy's USB port should point away from the rest of the parts.

<img src="images/14-teensy.jpg"/>

Just like with the power header, solder a couple of the pins of the female connectors before checking that everything lies flush with the board.

<img src="images/15-teensy.jpg"/>

With the Teensy now fully soldered, remove it from the female headers.

<img src="images/16-back.jpg"/>

###### Board-to-board connections

Now that the back board is done, plan out the headers for connecting it to the front board. You will need a pair of 4 pin headers (Male and female), and a pair of 10 pin headers (Male and female). The female headers will go into the board with the Teensy, and the male ones the board with the sockets and SMT parts (On the reverse side).

<img src="images/17-headers.jpg"/>

Insert the male headers into the female ones, then assemble everything together. It might take a couple of attempts to get the two boards mated together but the the headers _should_ all line up nicely once you're done. Solder a pin of each male header from the top first:

<img src="images/18-headers.jpg"/>

Next, carefully flip the board over and do the same for the female headers:

<img src="images/19-headers.jpg"/>

Check for alignment - are the two boards parallel with each other? If they are, that's great! But if not, try heating the solder again and shifting the boards so they line up correctly.

Once you have a few pins soldered, you can carefully prise the two boards apart again, soldering the rest of the pins with the two boards separated out. I found that it was a little tricky to get everything to lie flat otherwise, and this helped a lot.

<img src="images/20-headers.jpg"/>

With headers all soldered, it's on to the front panel components.

###### Sockets and LEDs

First, start by adding three Thonkiconns to positions 1, 2, and 19. Add a Stereo Thonkiconn (ie. a green one, PJ366ST) to the MIDI position. This has to be stereo - a mono jack will not work here!

<img src="images/21-sockets.jpg"/>

Slide the front panel over the top, add washers and nuts to keep everything flush to the front panel and then solder the jacks. Soldering the first four sockets helps make the next set of sockets a bit easier.

<img src="images/22-sockets.jpg"/>

With the first four sockets soldered, take the front panel off again and add the rest of the sockets and LEDs. LEDs are another polarised part, make sure you get them the right way around. The long leg (The anode) should go into the round hole.

Before soldering, carefully thread the panel over the sockets and secure a couple of the top and bottom sockets in place again. This should give you perfect alignment for all the sockets.

For the LEDs in particular, it's worth flipping the whole thing over and checking that the LED you are about to solder is flush with the front panel before soldering.

<img src="images/23-sockets-and-leds.jpg"/>

At this point you'll be faced with a lot of pads to solder! I found it easiest to solder a row at a time, snipping LED legs as I went.

When soldering the components on the front board, be careful not to touch the small SMT parts with your soldering iron or the male headers.

<img src="images/24-sockets-and-leds.jpg"/>

###### Final assembly

Add washers and nuts to the remaining sockets if not done already.

Add jumpers to the MIDI type headers on the rear board, following the silkscreen to get them in the right position. Unfortunately TRS MIDI isn't really standardised, which is why this design has jumpers - you can switch from MIDI A to MIDI B by just moving the jumpers around. To find out which type of MIDI your device speaks, check the manual, or https://minimidi.world/ for your manufacturer. Note that ONLY type A and B MIDI are supported, MIDI TS (Sometimes called type C) isn't supported. Thankfully, nearly everything uses Type A or B.

Next, add the Teensy back to the rear board then carefully slot together the front and back boards, making sure the male and female pins all line up correctly.

<img src="images/25-final.jpg"/>

And that's it, you're done!

###### Testing

No calibration is needed.

Check for shorts by probing the power header with your multimeter. There should be no continuity between +12v and ground, -12v and ground, or +12v and -12v.

Plug the module in to your rack and try patching in a trigger or gate signal to one of the inputs. As the trigger goes high, you should see the LED for that jack light up. The MIDI light at the bottom-right of the module should also light.

Connect the MIDI output to your drum machine. To do this you'll need a TRS to MIDI cable, or a TRS to MIDI adapter and a MIDI cable. [Befaco](https://www.thonk.co.uk/shop/befaco-midi-trs-adaptor-cables/) sells a nice TRS to MIDI cable which is perfect. With triggers, gates, or anything else connected up to the DrumFiend's inputs, the drum machine should now start playing some drums! Try adding clock sources and logic-modulated clocks for instant programmable rhythms.

###### Firmware tweaks

The software for DrumFiend is written with the DrumBrute Impact in mind. This means that the default configuration works on MIDI channel 10, and notes 36 through to 57. For the DrumBrute Impact, the left and right inputs per row match up with the "normal" and "colour" versions of drum sounds. If you want to change which notes the DrumFiend puts out for a given input, see [MANUAL.md](MANUAL.md).