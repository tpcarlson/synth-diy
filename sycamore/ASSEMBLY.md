# Sycamore - Assembly

##### PCB Versions and kits

PCB versions 1.0 & 1.1 come _without_ the DAC soldered.

PCB versions 1.2 and up come _with_ the DAC soldered.

Kits for Sycamore include the male and female headers for the Rasperry Pi Pico cut to size already.

##### Getting ready

First, gather together the tools you are going to use to assemble the module. At the bare minimum you should be able to do this with just a soldering iron & solder - but there are some additional tools that will make life easier:

- PCB vice or helping hands to hold the PCB in place
- Fan and absorbent material to get rid of solder/flux fumes
- Overhead lighting
- Silicone mat or scrap piece of wood to protect whatever surface you're soldering on
- Solder dispenser
- Tubs to hold parts ready for soldering
- Multi-meter for continuity testing

![parts](images/1-parts.jpg)

Take a look through the bill of materials and make sure you have all the parts. I like to organise mine by putting them into tupperware or take-away boxes - if you do too, just don't use them for food again afterwards.

###### Preparing the Pico

First, solder the male headers to the Pico. To hold everything in place, use a couple of 

<img title="" src="images/2-pico.jpg" alt="pi pico headers">Now you can solder the male headers to the Pico. Remove the female headers once you're done and the Pico is good to go.

<img title="" src="images/3-pico.jpg" alt="soldered pico">

If you are building this from your own parts, cut down some female headers to size (2 sets of 20 pins) to match the Pico, you'll use these a bit later. Kits will have these headers cut to size already.

Connect the Pico to your computer and program it with the firmware. See the [FIRMWARE.md](FIRMWARE.md) guide for more details.

##### LEDs

The mode LEDs are first to solder. On the back of the LED is a long vertical line, this indicates the 5V side, which is on the left hand side of the module. [This page](https://lighthouseleds.com/blog/polarity-guide-of-0402-0603-0805-1206-and-most-all-smd-leds.html) has a good set of pictures for common LED indicators in case yours are different.

![](images/4-led.jpg)

The vertical line on the LEDs (The anode) should be on the left hand side of the PCB.

You can decide how exactly to solder the LEDs. Either a hot air gun and paste or a soldering iron will work. A hotplate will not work as there are already parts on the other side.

To solder with a soldering iron, first add a little bit of solder to one of the pads, place the LED on top of this, then reflow the solder with your iron before soldering the second pad.

If you're going to use a soldering iron, make sure not to hold the iron on the solder joints for too long to avoid damaging the LEDs.

Here you can see an in-progress shot from soldering with hot air and paste where I added a little too much of the paste Your soldering should look much cleaner than this!

![](images/5-led.jpg)

##### Rear components (Pico, power)

Now solder the rear components. Start with the power connector. This should be placed respecting the silkscreen, with the notch pointed towards the bottom of the PCB. Solder one or two pins then check that the power connector is sitting flush with the PCB before soldering the rest of the pins.

![](images/6-power.jpg)

Slot the Rasperry Pi Pico with its soldered male headers from the first step into the 20-pin female headers. Insert into the PCB with the USB port on the Rasperry Pi Pico pointing upwards. As with the power connector, solder a couple of pins and make sure the headers are flush with the PCB before soldering the rest.

![](images/8-even-more-pico.jpg)

![](images/7-pico.jpg)

![](images/9-more-pico.jpg) 

##### 7-segment display headers

You may skip this step if you prefer your 7-segment displays to sit under the panel rather than aligned with it.

Insert the 7-segment displays' pins into the SIL sockets and set them aside for now.

![](images/10-7seg.jpg)

##### Front panel parts (Pots, jacks, buttons, and light pipes)

Gather up the remaining front panel parts and add them to the PCB. It's best to do this in a certain order as some parts are a bit more fiddly than others to install. Do not solder any of these parts yet!

- Start with the Rotary Encoder in the top-left. Make sure the three legs are pointed towards the bottom of the board!

- Add the four 10k potentiometers

- Add the three LED buttons along the left side of the PCB. These have a small, green dot which should face the right hand side, towards the potentiometers. The PCB also has a dot showing the proper orientation

- Add the 10 mono Thonkiconn sockets to the bottom of the PCB. Make sure they all lie flat against the PCB.

- Add the round button to the top-right of the PCB. Make sure the flat edge of the button is pointing upwards, as indicated by the silkscreen on the PCB

- Finally, add a nut to the Rotary Encoder. Try and get it as level as you can with the four potentiometers - you're aiming to get the top of the nut and the top of the boxy section of the potentiometers to the same height. If it's off by a little then that's OK! Once you're happy, add a washer on top of the bolt

![](images/11-stuffed-pcb.jpg)

![](images/12-washer.jpg)

##### 7-segment displays & Light pipes

Insert the 7-segment displays with their SIL sockets into the cutout at the top of the panel. They should fit side by side, with the decimal points at the bottom.

This is a press fit, and owing to the tolerances of the panel and the 7-segment displays, can be quite tight. If you find that the 7-segment displays just won't fit inside the panel, with a file or some sandpaper, remove a bit of the offending PCB panel material. This stuff really isn't good to breathe in, so please do make sure you do this outside!

Light pipes are another press-fit item, just press them firmly into the panel from behind.

![](images/14-press-fit.jpg)

![](images/13-press-fit.jpg)

##### Securing front panel parts

Thread the panel carefully over the front panel components. The 7-segment displays might need a little bit of gentle persuasion to locate themselves into the PCB, but everything else should slip into place easily. Take care with the round button which has shorter legs than the other parts.

Secure the front panel to the PCB by adding:

- Another nut to the rotary encoder

- Washers and then nut to the potentiometers

- A couple of washers and nuts to the audio jacks

I prefer to just secure two or four of the audio jacks at this point, if anything is wrong with the soldering then undoing all the nuts is a bit of a pain!

At this point, it's worth testing the rotation of the potentiometers and encoder, and the action of the buttons to make sure everything feels correct.

![](images/15-front-panel.jpg)

##### Soldering the front panel parts

Very carefully flip the module over and start soldering the front panel parts. It's best to solder the parts that had nuts and washers added first as these are the "glue" that'll hold everything else together. Especially for the Thonkiconn sockets, solder one pin and then make sure that they are totally flush to the main PCB before soldering the rest.

Take particular care when soldering the center-most potentiometers - these are between the female headers for the Rasperry Pi Pico. Don't melt the headers!

Solder the 7-segment displays and the round button at the top-right last.

![](images/16-front-panel.jpg)

##### Finishing off the front panel

Add D-shaft knobs to the four potentiometers, and a D-shaft knob to the encoder. Make sure the encoder can be pressed down to press it.

If you're feeling confident at this point, add the rest of the washers and nuts to the Thonkiconn sockets. It can be helpful to leave this step to the end in case you need to take the module apart to fix up some soldering, though!

![](images/17-done.jpg)

##### Adding the Rasperry Pi Pico

If you skipped programming the Pico previously, now is the time to revisit the [FIRMWARE](FIRMWARE.md) guide.

Insert the programmed Rasperry Pi Pico into the female headers on the back of the board. The three holes on the Pico should match the 3 holes in the PCB (Although no pins/sockets are present there), with the USB port pointing up towards the 7-segment display.

###### Testing

No calibration is needed.

Check for shorts by probing the power header with your multimeter. There should be no continuity between +12v and ground, -12v and ground, or +12v and -12v.

With all the knobs at 12-o-clock, plug output 1 into a VCO. Press the clock button (It should briefly light) and listen to the VCO's output. If everything is correctly soldered and the firmware flashed, the pitch for the VCO should change as the notes output by Sycamore change with successive clock button presses.

See [MANUAL.md](MANUAL.md) for how to use the module.