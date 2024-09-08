# Oak - Firmware

##### Requirements

To program the Oak firmware you will need:

- A USB-C to USB-C or USB-A cable

- The Oak UF2 firmware file. See the [firmware directory](firmware/) for the latest version.

##### Oak Firmware

With Oak powered by your rack, plug the USB-C cable in to the port on the rear of the module. Oak should show up as a new removable drive. Copy the UF2 firmware file to the drive and wait for the module to restart.

To verify that the firmware is installed, press one of the four LED buttons and verify the button lights up.

##### Firmware hacking

Oak's code is very simple, and for the most part hands off logic to Sycamore. However, if you wish to hack on Oak, download the Arduino IDE and open the .ino sketch. Oak uses polling to listen for events like button presses and trigger inputs, and interrupts for i2c communication with Sycamore. 

##### i2c protocol

The i2c protocol used for Sycamore and Oak to talk to one another is very simple! There are two kinds of i2c messages - messages which Sycamore sends to Oak, and messages which Oak sends to Sycamore. Sycamore is the controller, Oak the device.

For messages from Sycamore to Oak:

```
UNUSED | loop start | note change | step | shift | quant | length | range
```

For messages from Oak to Sycamore:

```
UNUSED | scale shuffle | scale reset | reset loop | shift | quant | length | range
```

Oak has the i2c device address 0x42.
