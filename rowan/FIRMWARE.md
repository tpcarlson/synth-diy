# Rowan - Firmware

##### Requirements

To program the Rowan firmware you will need:

- A USB-C to USB-C or USB-A cable

- The Rowan UF2 firmware file. See the [firmware directory](firmware/) for the latest version.

Sycamore will also need to be configured to see Rowan.

##### Rowan Firmware

With Rowan powered by your rack, plug the USB-C cable in to the port on the rear of the module. Rowan should show up as a new removable drive. Copy the UF2 firmware file to the drive and wait for the module to restart.

##### Sycamore Firmware

If not done already, program Sycamore with the latest firmware. See the Sycamore [firmware guide](../sycamore/FIRMWARE.md) for more information.

Configure Sycamore to enable the Rowan expander:

```json
{
 "auxMode": "mutate",
 "expanders": ["rowan"],
 "dacLookupTable": [0, 68.. (etc)]
}
```

To test that Rowan and Sycamore are both working correctly, power off the modules, disconnect any USB cables, connect the two modules using the JST-XH cable, then clock Sycamore. The outputs should be 0-5v, triggers similar, and the LEDs should show the currently active noces.

##### Firmware hacking

Rowan's code is very simple, and for the most part hands off logic to Sycamore. However, if you wish to hack on Rowan, download the Arduino IDE and open the .ino sketch. Rowan uses interrupts for i2c communication with Sycamore.

##### i2c protocol

The i2c protocol used for Sycamore and Rowan to talk to one another is relatively simple. In terms of i2c, Sycamore is the controller, Rowan the device.

Messages from Sycamore to Rowan are encoded into 2 byte (16 bit) wide messages:

```
command0 | command1 | command 2 | channel | 12 data bits
```

The commands are as follows:

```
0 0 0: allowed notes
0 0 1: active notes
0 1 0: unquantized outputs
0 1 1: quantized outputs
1 0 0: red
1 0 1: green
1 1 0: blue
```

The red, green, and blue refer to the colours for Rowan's RGB LEDs. Setting individual LED colours is not possible with the current protocol, these colours apply to the entire LED array.

Channel refers to the left and right side of Rowan, which relate to the Out 1 and Out 2 outputs of Sycamore.

Rowan has the i2c device address 0x44.
