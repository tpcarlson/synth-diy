# Sycamore - Firmware

##### Requirements

To program the Sycamore firmware you will need:

- Rasperry Pi Pico

- Micro USB cable. Make sure the cable is not a "charging" cable, you need data and power

- [Sycamore firmware ZIP](https://raw.githubusercontent.com/tpcarlson/synth-diy/main/sycamore/firmware/sycamore-1.4.zip) (Version 1.4)

- The CircuitPython U2F file for Rasperry Pi Pico ([Pi Pico Download](https://circuitpython.org/board/raspberry_pi_pico/))

##### CircuitPython Installation

*Disconnect the Sycamore module from your modular synth before programming the pico!*

Follow the [Adafruit tutorial]((https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython)) to flash CircuitPython onto the Pi Pico. Essentially, you need to copy the CircuitPython U2F to the Pico and wait for it to restart.

Once installed, you should find the CIRCUITPY drive mounted automatically.

##### Sycamore Firmware

Unzip the firmware.zip somewhere on your computer, then copy the extracted files over to the CIRCUITPY drive. You can overwrite the code.py file already present.

Once you're done, the disk's contents should look like this. You may be missing the boot_out.txt:

![](images/firmware.png)

That's it, the Sycamore firmware is now on your Pico. See [MANUAL.md](MANUAL.md) for how to use the module.

##### Configuring Sycamore

Sycamore has a small configuration file, config.txt, which you may use to configure the module.

auxMode controls the function of the "Aux" input on Sycamore. It can be any of:

- "mutate": Keep the same behaviour as the original firmware, using the Aux CV as a source of randomness when seeding the scale

- "shuffle": Shuffle the current scale. Acts in the same way a long press on the scale encoder does. A long press on the scale encoder will reset the current scale back to the original ordering

- "resetClock": Reset to the start of the sequence

Expanders controls the expanders installed for Sycamore. At the time of writing, Oak is the only expander for Sycamore. To enable Oak, add to the Expanders list in the configuration file. Leave expanders an empty list ("[]") if you have no expanders for Sycamore installed.

```json
{
    "auxMode": "mutate",
    "expanders": ["oak"],
    "dacLookupTable": [0, 68.. (etc)]
}
```

##### Firmware hacking

If you want to change Sycamore's code, try installing the Mu editor first as it does allow for some debugging workflows. Adafruit has an excellent guide to walk through this [Installing the Mu Editor (adafruit.com)](https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor). When modifying the firmware, start with code.py and go from there.
