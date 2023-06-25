# Sycamore - Firmware

##### Requirements

To program the DrumFiend firmware you will need:

- Rasperry Pi Pico

- Micro USB cable. Make sure the cable is not a "charging" cable, you need data and power

- Firmware.zip (TODO: Add a link to the firmware)

- The CircuitPython U2F file for Rasperry Pi Pico ([Pi Pico Download]([Pico Download](https://circuitpython.org/board/raspberry_pi_pico/)))

##### CircuitPython Installation

*Disconnect the Sycamore module from your modular synth before programming the pico!*

Follow the [Adafruit tutorial]((https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython)) to flash CircuitPython onto the Pi Pico. Essentially, you need to copy the CircuitPython U2F to the Pico and wait for it to restart.

Once installed, you should find the CIRCUITPY drive mounted automatically.

##### Sycamore Firmware

Unzip the firmware.zip somewhere on your computer, then copy the extracted files over to the CIRCUITPY drive. You can overwrite the code.py file already present.

Once you're done, the disk's contents should look like this. You may be missing the boot_out.txt:

(TODO: Add sycamore firmware screenshot)

<img title="" src="images/firmware-2.png" alt="" width="147">

That's it, the Sycamore firmware is now on your Pico.

##### Firmware hacking

If you want to change Sycamore's code, try installing the Mu editor first as it does allow for some debugging workflows. Adafruit has an excellent guide to walk through this [Installing the Mu Editor (adafruit.com)](https://learn.adafruit.com/welcome-to-circuitpython/installing-mu-editor). When modifying the firmware, start with code.py and go from there.
