---
typora-root-url: images
---

# Multimult

##### What is this?

An 8hp, 6 way buffered multiple. For each row, the input is *copied* and the copies are sent to the three output jacks. A small indicator LED per row shows the presence of signal. This buffered multiple is *DC coupled*, which means it's great for both audio and CV use.

##### How much power does it use?

As measured by the joranalogue Test 3, around 50mA on +12v and similar on -12v at peak. The 5v rail is unused.

##### Where does the design come from?

The schematic is based on the Music from outer space DC coupled Voltage Distributor #2, with some tweaks. You can find the original schematics on the MFOS site (http://musicfromouterspace.com/index.php?MAINTAB=SYNTHDIY&VPW=1252&VPH=500).

##### Are there any rare/weird parts used?

No. The design specifies a two-colour LED per input, so you could substitute that for a single colour LED if you only care about positive voltages.

##### Are there any problems with the design?

Not that I'm aware of. Other buffered multiple schematics seem to add a high resistance path to ground for the opamp inputs, but the MFOS design did not - so I skipped it as well. It's worth soldering the two-colour LEDs last after verifying that the positive and negative colours are the right way around - the first LED I soldered red was positive and green negative! A really easy way to check this is to power up the module, feed it some known signals and just touch the legs of your LED to the pads for the LEDs.

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Everything in this project is easy to source though, so you should not have any trouble.

##### Can I buy PCBs or a kit?

Send me an email (twigathy+synth@gmail.com)...

![multmult-panel](/multmult-panel.png)