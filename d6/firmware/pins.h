#if defined(TEENSYDUINO)
#warning message "Using Teensy bindings"
#include "pins_teensy4.h"
#elif defined(TARGET_RASPBERRY_PI_PICO)
#warning message "Using Rasperry Pi Pico bindings (MBed)"
#include "pins_pipico.h"
#elif defined(ARDUINO_RASPBERRY_PI_PICO)
#warning message "Using Raspberry Pi Pico bindings (Arduino-pico)"
#include "pins_pipico.h"
#else
#error "Unknown board flavour; expecting Teensy or Rasperry Pi Pico"
#endif
