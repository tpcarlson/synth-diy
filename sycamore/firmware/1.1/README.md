# sycamore

Firmware for the Sycamore Eurorack module

#### Changelog

<u>Version 1.1</u>

This version does not introduce any new features, but does make the end to end processing of clocks quicker in most cases. The original latency was up at 20ms+, which caused a noticable glitch when Sycamore was used in conjunction with fast attack on an envelope & VCA.

- Reduced clock input latency
  
  - Switched from automatic garbage collection to manual garbage collection afer clocking
  
  - Reduced heap allocations to reduce required garbage collection time
  
  - Reduced quantizer processing time when clocked. Total time from clock event recieved to DAC output should be less than 5ms, and usually 2-4ms

<u>Version 1.0</u>

-  Initial release
