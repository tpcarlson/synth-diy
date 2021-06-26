# VCADSR

##### What is this?

Voltage controlled ADSR, using the [ElectricDruid EnvGen8](https://electricdruid.net/product/envgen8/) chip. The module provides voltage control over most parameters (Attack, decay, sustain, release, time, level) as well as manual control with sliders. There are also three switches for toggling the mode, linear/exponential, and a fifth stage called "punch" which adds a little bit more to the attack on an envelope.

The mode toggle switch allows for gated looping, just looping (Almost like an LFO), and normal ADSR mode.

##### How much power does it use?

As measured by the joranalogue Test 3, around 40mA on +12v and 30mA on -12v at peak. The 5v rail is unused.

##### Where does the design come from?

The schematic is really an extension of the reference design on the [ElectricDruid](https://electricdruid.net/product/envgen8/) site, with some changes to add LEDs, and cutting features that would otherwise take up more panel space than I was comfortable with - I dropped the attenuators for CV inputs in favour of nice big manual controls with linear potentiometers instead.

##### Are there any rare/weird parts used?

You'll need one of the EnvGen8 chips in order to make this function at all!

##### Are there any problems with the design?

Just a couple, which are corrected in the version here. First, the LEDs for gate and trigger had some issues drawing too much power due to an oversight in the schematic. As it turns out LEDs don't really like being driven without a resistor! Second, the panel design had the mode and linear/exponential graphics switched which makes operating it a little bit more confusing than it otherwise ought to be.

These problems are both fixed in the repository right now though, however the fixes are *untested*. If I make another run of these boards, I will verify that the fix worked and remove this whole section!

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Everything in this project is easy to source though, so you should not have any trouble.

##### Other resources

- [Assembly instructions](ASSEMBLY.md)

![](images/vcadsr.png)
