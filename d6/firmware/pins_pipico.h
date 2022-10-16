// Pin assignments for Rasperry Pi Pico
// Using the RP2040 bindings from https://github.com/earlephilhower/arduino-pico
// Skip buttons
#define SKIP_1               2
#define SKIP_2              22
#define SKIP_3               3
#define SKIP_4              21
#define SKIP_5              20
#define SKIP_6              16

// Settings buttons
#define SKIP_AFTER           5
#define EXCLUSIVE            6
#define AUTO_RESET           7
#define RESET_NOW            8

// Jumpers
#define ZERO_CROSSING        1

// AnalogRead mappings
#define RIG_DICE            26

// Input jacks
#define EXT_RESET           11
#define EXT_EXCLUSIVE        4
#define EXT_AUTO_RESET       9
#define EXT_SKIP_AFTER_ROLL  0
#define EXT_CLOCK           13

#define SHIFTER_OE_ENABLE   12

#define LED_CONTROL_DATA    17
#define LED_CONTROL_CLOCK   15
#define LED_CONTROL_LOAD    14
#define DS1882_ENABLE       10
#define DS1882_SDA          18
#define DS1882_SCL          19
