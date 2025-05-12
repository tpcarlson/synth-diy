# Oak - Firmware

##### Requirements

To program the Oak firmware you will need:

- A USB-C to USB-C or USB-A cable

- The Oak UF2 firmware file. See the [firmware directory](firmware/) for the latest version.

Sycamore will also need to be configured to see Oak.

##### Oak Firmware

###### Initial install

- Power off Oak (Turn off power to the rack if it is on)

- Plug the USB-C cable in to the port on the rear of the module

- Power on Oak (Turn on power to the rack)

- Oak should show up as a new removable drive, but if it does not please follow the "Updating Oak" instructions below instead

- Copy the UF2 firmware file to the drive and wait for the module to restart

###### Updating Oak from a previous firmware

- Power off Oak (Turn off power to the rack if it is on)

- Using a 2 pin, 2.54mm jumper or cable, short the two pins next to the button on the rear of Oak

- Plug the USB-C cable in to the port on the rear of the module

- Power on Oak (Turn on power to the rack)

- Oak will show up as a new removable drive

- Remove the jumper

- Copy the UF2 firmware file to the drive and wait for the module to restart

###### Checking the firmware is installed

To verify that the firmware is installed, press one of the four LED buttons and verify the button lights up.

##### Sycamore Firmware

If not done already, program Sycamore with the latest firmware. See the Sycamore [firmware guide](../sycamore/FIRMWARE.md) for more information.

Configure Sycamore to enable the Oak expander:

```json
{
 "auxMode": "mutate",
 "expanders": ["oak"],
 "dacLookupTable": [0, 68.. (etc)]
}
```

##### Firmware hacking

Oak's code is very simple, and for the most part hands off logic to Sycamore. However, if you wish to hack on Oak, download the Arduino IDE and open the .ino sketch. Oak uses polling to listen for events like button presses and trigger inputs, and interrupts for i2c communication with Sycamore. 

##### i2c protocol

The i2c protocol used for Sycamore and Oak to talk to one another is very simple! There are two kinds of i2c messages - messages which Sycamore sends to Oak, and messages which Oak sends to Sycamore. Sycamore is the controller, Oak the device.

For messages from Sycamore to Oak:

```
led brightness | loop start | note change | step | shift | quant | length | range
```

For messages from Oak to Sycamore:

```
UNUSED | scale shuffle | scale reset | reset loop | shift | quant | length | range
```

Oak has the i2c device address 0x42.
