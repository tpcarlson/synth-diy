# Sycamore

Firmware for the Sycamore Eurorack module

#### Changelog

<u>Version 1.5 (Alpha)</u>

- Added support for the "Rowan" expander module
  
  - Quantized and unquantized outputs
  
  - Currently active notes
    
    - White when unshuffled, purple with scale shuffle enabled

- Significant refactoring to the Python core of Sycamore. It's certainly not perfect, but it's an improvement.

Syntax for enabling the Rowan expander:

```json
{
    "auxMode": "resetClock",
    "expanders": ["rowan"],
    "dacLookupTable": [0, 68.. (etc)]
}
```

<u>Version 1.4</u>

- Added support for the "Oak" expander module
  
  - Parameter locking
  
  - Start of loop, step, note outputs
  
  - Scale shuffle and reset inputs

- Added support for future modules

Syntax for enabling the Oak expander:

```json
{
    "auxMode": "resetClock",
    "expanders": ["oak"],
    "dacLookupTable": [0, 68.. (etc)]
}
```

<u>Version 1.3</u>

- Reduced sequence length ADC jitter. This could cause short sequences to skip around a bit by one or two steps. The reduction in jittle comes at the cost of reduced swiftness in reaction to length CV changes.

- Reduced time spent in GC operations, after a clock event.

- Introduce a new configuration flag, "auxMode", to settings.txt. These are all to aid in development of an expander for Sycamore, but are quite handy on their own! This setting can be (Case-sensitive) one of:
  
  - "mutate": Keep the same behaviour as the original firmware, using the Aux CV as a source of randomness for seeding the scale
  
  - "shuffle": Shuffle the current scale. Acts in the same way a long press on the scale encoder does. A long press on the scale encoder will reset the current scale back to the original ordering
  
  - "resetClock": Reset to the start of the sequence
  
  - As an example, settings.txt might look like this:

```json
{
    "auxMode": "resetClock",
    "dacLookupTable": [0, 68.. (etc)]
}
```

<u>Version 1.2</u>

This version does not introduce new features, but does refactor a lot of the code to be more "pythonic". This should make it a little easier to add new features in future, and improves the readibility of the code.

<u>Version 1.1</u>

This version does not introduce any new features, but does make the end to end processing of clocks quicker in most cases. The original latency was up at 20ms+, which caused a noticable glitch when Sycamore was used in conjunction with fast attack on an envelope & VCA.

- Reduced clock input latency
  
  - Switched from automatic garbage collection to manual garbage collection afer clocking
  
  - Reduced heap allocations to reduce required garbage collection time
  
  - Reduced quantizer processing time when clocked. Total time from clock event recieved to DAC output should be less than 5ms, and usually 2-4ms

<u>Version 1.0</u>

- Initial release
