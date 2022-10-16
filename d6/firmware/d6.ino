// The built-in pi pico bindings break with LedControl.h,
// This means we have to use a customised version instead.
// See libraries/ directory for details
#include "LedControl.h"

#if defined(TEENSYDUINO)
#include "Bounce.h"
#elif defined(TARGET_RASPBERRY_PI_PICO) || defined(ARDUINO_RASPBERRY_PI_PICO)
#include "Bounce2.h"
#endif

#include <Wire.h>

#include "pins.h"

#define SKIP_AFTER_SETTING   0
#define EXCLUSIVE_SETTING    1
#define AUTO_RESET_SETTING   2
#define RESET_NOW_SETTING    3

// Constants for DS1882s
#define ds1882config  (0b10000110) // Volatile, Zero-crossing enabled, 63 positions + mute
#define pot1muted  (0b00111111)
#define pot1unmuted  (0b00000000)
#define pot2muted  (0b01111111)
#define pot2unmuted  (0b01000000)

#define ds1882address1 0x28 // A0, A1, A2 low 
#define ds1882address2 0x29 // A0 high, A1, A2 low
#define ds1882address3 0x2A // A1 high, A0, A2 low

// Static roll distributions
int FAIR_WEIGHTED[6] =   { 1, 2, 3, 4, 5, 6 };
int ONE_WEIGHTED[12] =   { 1, 1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6 };
int TWO_WEIGHTED[14] =   { 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 5, 6 };
int THREE_WEIGHTED[14] = { 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5, 6 };
int FOUR_WEIGHTED[14] =  { 1, 2, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 6 };
int FIVE_WEIGHTED[14] =  { 1, 2, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 6, 6 };
int SIX_WEIGHTED[12] =   { 1, 2, 3, 4, 5, 5, 6, 6, 6, 6, 6, 6 };

// These map the state of the slider to the number of elements in the array
// Simply saves calculating sizeof(array) each time.
int WEIGHT_COUNTS[7] = { 6, 12, 14, 14, 14, 14, 12 };

// 5ms debounce on all inputs
// "In" input does not go via the Teensy at all, so is not
// included here - the analogue and digital sections are
// kept (reasonably...) separated
Bounce EXT_RESET_DEBOUNCED = Bounce(EXT_RESET, 5);
Bounce EXT_EXCLUSIVE_DEBOUNCED = Bounce(EXT_EXCLUSIVE, 5);
Bounce EXT_AUTO_RESET_DEBOUNCED = Bounce(EXT_AUTO_RESET, 5);
Bounce EXT_SKIP_AFTER_ROLL_DEBOUNCED = Bounce(EXT_SKIP_AFTER_ROLL, 5);
Bounce EXT_CLOCK_DEBOUNCED = Bounce(EXT_CLOCK, 5);

// 5ms debounce on settings buttons
Bounce SKIP_AFTER_DEBOUNCED = Bounce(SKIP_AFTER, 5);
Bounce EXCLUSIVE_DEBOUNCED = Bounce(EXCLUSIVE, 5);
Bounce AUTO_RESET_DEBOUNCED = Bounce(AUTO_RESET, 5);
Bounce RESET_NOW_DEBOUNCED = Bounce(RESET_NOW, 5);

// 5ms debounce on mute toggling buttons
Bounce SKIP_1_DEBOUNCED = Bounce(SKIP_1, 5);
Bounce SKIP_2_DEBOUNCED = Bounce(SKIP_2, 5);
Bounce SKIP_3_DEBOUNCED = Bounce(SKIP_3, 5);
Bounce SKIP_4_DEBOUNCED = Bounce(SKIP_4, 5);
Bounce SKIP_5_DEBOUNCED = Bounce(SKIP_5, 5);
Bounce SKIP_6_DEBOUNCED = Bounce(SKIP_6, 5);

struct Die {
  bool outputEnabled;
  bool skipped;
  Bounce* debouncedButton;
};

struct Die dice[6];

struct Setting {
  bool state;
  Bounce* buttonInput;
  Bounce* jackInput;
};

struct Setting settings[4];

// One LED controller (MAX7219)
LedControl lc=LedControl(LED_CONTROL_DATA,LED_CONTROL_CLOCK,LED_CONTROL_LOAD,1);

bool firstEverButton = true;
bool firstExclusive = true;
bool skipActivated = false;
int currentRandom = 1;
int currentSkip = -1;

unsigned long lastClockMillis = 0;
unsigned long lastResetMillis = 0;
unsigned long CLOCK_LED_MILLIS = 250;
unsigned long RESET_LED_MILLIS = 250;
unsigned long LED_TEST_MILLIS = 100;

// Histogram of rolls, kind of
int histogram[6] = { 0, 0, 0, 0, 0, 0 };

void testLeds() {
  lc.clearDisplay(0);
  
  // Settings
  for (int i = 1; i <= 4; i++) {
    lc.setLed(0, 3, i, true);
    delay(LED_TEST_MILLIS);
    lc.clearDisplay(0);
  }

  // 7-seg
  for (int i = 1; i <= 6; i++) {
    lc.setDigit(0, 1, i, true);
    delay(LED_TEST_MILLIS);
    lc.clearDisplay(0);
  }

  // Outputs
  for (int i = 1; i <= 6; i++) {
    lc.setLed(0, 2, i, true);
    delay(LED_TEST_MILLIS);
    lc.clearDisplay(0);
  }

  // Skips (Wired to 'Outputs' in schematic)
  for (int i = 1; i <= 6; i++) {
    lc.setLed(0, 0, i, true);
    delay(LED_TEST_MILLIS);
    lc.clearDisplay(0);
  }

  lc.clearDisplay(0);
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(SKIP_1, INPUT_PULLUP);
  pinMode(SKIP_2, INPUT_PULLUP);
  pinMode(SKIP_3, INPUT_PULLUP);
  pinMode(SKIP_4, INPUT_PULLUP);
  pinMode(SKIP_5, INPUT_PULLUP);
  pinMode(SKIP_6, INPUT_PULLUP);

  pinMode(SKIP_AFTER, INPUT_PULLUP);
  pinMode(EXCLUSIVE, INPUT_PULLUP);
  pinMode(AUTO_RESET, INPUT_PULLUP);
  pinMode(RESET_NOW, INPUT_PULLUP);

  pinMode(ZERO_CROSSING, INPUT_PULLUP);

  pinMode(EXT_RESET, INPUT_PULLDOWN);
  pinMode(EXT_EXCLUSIVE, INPUT_PULLDOWN);
  pinMode(EXT_AUTO_RESET, INPUT_PULLDOWN);
  pinMode(EXT_SKIP_AFTER_ROLL, INPUT_PULLDOWN);
  pinMode(EXT_CLOCK, INPUT_PULLDOWN);

  pinMode(SHIFTER_OE_ENABLE, OUTPUT);
  digitalWrite(SHIFTER_OE_ENABLE, HIGH);

  // Start up the LED controller:
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);
  lc.setScanLimit(0, 4); // 4 blocks of LEDS: Settings, 7-segment display, output, and mute

  // Init the dice array, for later use
  dice[0].outputEnabled = false;
  dice[0].skipped = false;
  dice[0].debouncedButton = &SKIP_1_DEBOUNCED;
  
  dice[1].outputEnabled = false;
  dice[1].skipped = false;
  dice[1].debouncedButton = &SKIP_2_DEBOUNCED;
  
  dice[2].outputEnabled = false;
  dice[2].skipped = false;
  dice[2].debouncedButton = &SKIP_3_DEBOUNCED;

  dice[3].outputEnabled = false;
  dice[3].skipped = false;
  dice[3].debouncedButton = &SKIP_4_DEBOUNCED;

  dice[4].outputEnabled = false;
  dice[4].skipped = false;
  dice[4].debouncedButton = &SKIP_5_DEBOUNCED;

  dice[5].outputEnabled = false;
  dice[5].skipped = false;
  dice[5].debouncedButton = &SKIP_6_DEBOUNCED;

  // And settings too:
  settings[0].state = false;
  settings[0].buttonInput = &SKIP_AFTER_DEBOUNCED;
  settings[0].jackInput = &EXT_SKIP_AFTER_ROLL_DEBOUNCED;

  settings[1].state = false;
  settings[1].buttonInput = &EXCLUSIVE_DEBOUNCED;
  settings[1].jackInput = &EXT_EXCLUSIVE_DEBOUNCED;

  settings[2].state = false;
  settings[2].buttonInput = &AUTO_RESET_DEBOUNCED;
  settings[2].jackInput = &EXT_AUTO_RESET_DEBOUNCED;

  settings[3].state = false;
  settings[3].buttonInput = &RESET_NOW_DEBOUNCED;
  settings[3].jackInput = &EXT_RESET_DEBOUNCED;

  // Set up DS1882s
  delay (100);

  #if defined(ARDUINO_RASPBERRY_PI_PICO)
  Wire1.setSDA(DS1882_SDA);
  Wire1.setSCL(DS1882_SCL);
  #endif
  
  Wire1.begin();
  
  pinMode(DS1882_ENABLE, OUTPUT);
  digitalWrite(DS1882_ENABLE, LOW); // Pulls low on every DS1882

  # if defined(ARDUINO_RASPBERRY_PI_PICO)
  Wire1.beginTransmission(ds1882address1);
  Wire1.write(ds1882config);
  Wire1.endTransmission();

  Wire1.beginTransmission(ds1882address2);
  Wire1.write(ds1882config);
  Wire1.endTransmission();

  Wire1.beginTransmission(ds1882address3);
  Wire1.write(ds1882config);
  Wire1.endTransmission();
  # else if defined(TEENSYDUINO)
  Wire.beginTransmission(ds1882address1);
  Wire.write(ds1882config);
  Wire.endTransmission();

  Wire.beginTransmission(ds1882address2);
  Wire.write(ds1882config);
  Wire.endTransmission();

  Wire.beginTransmission(ds1882address3);
  Wire.write(ds1882config);
  Wire.endTransmission();
  # endif
  
  testLeds();

  // Read button states to clear the debounce lib's state (It thinks all the buttons are pressed)
  SKIP_AFTER_DEBOUNCED.update();
  EXCLUSIVE_DEBOUNCED.update();
  AUTO_RESET_DEBOUNCED.update();
  RESET_NOW_DEBOUNCED.update();
  SKIP_1_DEBOUNCED.update();
  SKIP_2_DEBOUNCED.update();
  SKIP_3_DEBOUNCED.update();
  SKIP_4_DEBOUNCED.update();
  SKIP_5_DEBOUNCED.update();
  SKIP_6_DEBOUNCED.update();

  // Finally, set up the slider for use
  // analogReadResolution(10);
}

void printState() {
  Serial.println("SKIP STATES");
  Serial.print(digitalRead(SKIP_1));
  Serial.print(", ");
  Serial.print(digitalRead(SKIP_2));
  Serial.print(", ");
  Serial.print(digitalRead(SKIP_3));
  Serial.print(", ");
  Serial.print(digitalRead(SKIP_4));
  Serial.print(", ");
  Serial.print(digitalRead(SKIP_5));
  Serial.print(", ");
  Serial.println(digitalRead(SKIP_6));

  Serial.println("===================");
  Serial.println("SETTINGS STATES");
  Serial.print(digitalRead(SKIP_AFTER));
  Serial.print(", ");
  Serial.print(digitalRead(EXCLUSIVE));
  Serial.print(", ");
  Serial.print(digitalRead(AUTO_RESET));
  Serial.print(", ");
  Serial.println(digitalRead(RESET_NOW));

  Serial.println("===================");
  Serial.println("JUMPER STATES");
  Serial.print(digitalRead(ZERO_CROSSING));
  Serial.print(", ");
  Serial.println(analogRead(RIG_DICE));
  
  Serial.println("===================");
  Serial.println("INPUT STATES");

  Serial.print(digitalRead(EXT_SKIP_AFTER_ROLL));
  Serial.print(", ");
  Serial.print(digitalRead(EXT_EXCLUSIVE));
  Serial.print(", ");
  Serial.print(digitalRead(EXT_AUTO_RESET));
  Serial.print(", ");
  Serial.print(digitalRead(EXT_RESET));
  Serial.print(", ");
  Serial.println(digitalRead(EXT_CLOCK));
  Serial.println("===================");
}

void printSettings() {
  Serial.println("Settings:");
  Serial.println(settings[SKIP_AFTER_SETTING].state);
  Serial.println(settings[EXCLUSIVE_SETTING].state);
  Serial.println(settings[AUTO_RESET_SETTING].state);
  Serial.println(settings[RESET_NOW_SETTING].state);
}

void writeDs1882State(int address, bool outputEnabled1, bool outputEnabled2) {
  # if defined(ARDUINO_RASPBERRY_PI_PICO)
  Wire1.beginTransmission(address);
  
  if (!outputEnabled1) {
    Wire1.write(pot1muted);
  } else {
    Wire1.write(pot1unmuted);
  }

  if (!outputEnabled2) {
    Wire1.write(pot2muted);
  } else {
    Wire1.write(pot2unmuted);
  }
  
  Wire1.endTransmission();
  # else if defined(TEENSYDUINO)
  Wire.beginTransmission(address);
  
  if (!outputEnabled1) {
    Wire.write(pot1muted);
  } else {
    Wire.write(pot1unmuted);
  }

  if (!outputEnabled2) {
    Wire.write(pot2muted);
  } else {
    Wire.write(pot2unmuted);
  }
  
  Wire.endTransmission();
  #endif
}

void updateMutes() {
  // Dice 0 and 1 are hooked up to DS1882 #1
  // Dice 2 and 3 are hooked up to DS1882 #2
  // Dice 4 and 5 are hooked up to DS1882 #3
  writeDs1882State(ds1882address1, dice[0].outputEnabled, dice[1].outputEnabled);
  writeDs1882State(ds1882address2, dice[2].outputEnabled, dice[3].outputEnabled);
  writeDs1882State(ds1882address3, dice[4].outputEnabled, dice[5].outputEnabled);
}

void updateState(bool rolled) {
  // Update the rolled dice first. In auto-reset mode this gets a bit funky,
  // because the last roll 'resets'
  if (rolled && !dice[currentRandom-1].skipped) {
    dice[currentRandom-1].outputEnabled = !dice[currentRandom-1].outputEnabled;
  }

  // If we get a reset, just clear all outputs and return
  if (settings[RESET_NOW_SETTING].state) {
    for (int i = 0; i < 6; i++) {
      dice[i].outputEnabled = false;
      dice[i].skipped = false;
    }

    // Reset should be a quick toggle, but we do want to light for a brief blip (As with clock)
    lastResetMillis = millis();
    settings[RESET_NOW_SETTING].state = false;
    return;
  }

  // A programmed-reset kind of, check whether we need to reset. This works on skips only, for now
  // to allow for rolling over to the next set of outputs.
  if (settings[AUTO_RESET_SETTING].state) {
    bool allSkips = true;
    for (int i = 0; i < 6; i++) {
      Serial.print("Skipped: ");
      Serial.println(dice[i].skipped);
      allSkips = allSkips && dice[i].skipped;
    }

    if (allSkips) {
      Serial.println("ALL skips, resetting dice");
      for (int i = 0; i < 6; i++) {
        dice[i].skipped = false;
      }

      // Finally, toggle whatever output there was already on the current dice.
      dice[currentRandom-1].outputEnabled = !dice[currentRandom-1].outputEnabled;
    }
  }

  // If we're in exclusive mode, that means only one output may be live at the same time.
  // Reset any outputs that are not the rolled output
  // Exclusive mode does not affect skip mode
  if (settings[EXCLUSIVE_SETTING].state) {
    if (firstExclusive) {
      // If we just entered exclusive mode, reset the number of open channels to 1. Basically
      // find the "first" of the outputting channels.
      int firstEnabledOutput = -1;
      for (int i = 0; i < 6; i++) {
        if (firstEnabledOutput == -1 && dice[i].outputEnabled) {
          firstEnabledOutput = i;
        } else if (dice[i].outputEnabled) {
          dice[i].outputEnabled = false;
        }
      }

      firstExclusive = false;
    } else {
      if (dice[currentRandom-1].skipped) {
        // Do nothing
      } else {
        for (int i = 0; i < 6; i++) {
          if (i != currentRandom-1) { // 1-6 -> 0-5
            dice[i].outputEnabled = false;
          }
        }
      }
    }
  } else {
    firstExclusive = true;
  }

  if (settings[SKIP_AFTER_SETTING].state && rolled && currentSkip != -1) {
    // The dice that was just rolled is now SKIPPED and may not be rolled again
    dice[currentSkip-1].skipped = true;
  }

  if (!settings[SKIP_AFTER_SETTING].state) {
    // Reset all skips.
    for (int i = 0; i < 6; i++) {
      dice[i].skipped = false;
    }

    currentSkip = -1;
  }
}

void updateLeds() {
  // Possibly want to do this in a more targetted way?
  lc.clearDisplay(0);
  lc.setDigit(0, 1, currentRandom, true); // 7-segment display

  for (int i = 0; i < 6; i++) {
    lc.setLed(0, 2, i+1, dice[i].outputEnabled); // Output LEDs
    lc.setLed(0, 0, i+1, dice[i].skipped); // Skip LEDs on line 0                          
  }

  printSettings();
  lc.setLed(0, 3, SKIP_AFTER_SETTING+1, settings[SKIP_AFTER_SETTING].state);
  lc.setLed(0, 3, EXCLUSIVE_SETTING+1, settings[EXCLUSIVE_SETTING].state);
  lc.setLed(0, 3, AUTO_RESET_SETTING+1, settings[AUTO_RESET_SETTING].state);
}

int getRandom(int lookupTable[], int tableLength) {
  int roll = lookupTable[random(tableLength)];
  histogram[roll-1]++;
  Serial.println("=============");
  Serial.print(histogram[0]);
  Serial.print(", ");
  Serial.print(histogram[1]);
  Serial.print(", ");
  Serial.print(histogram[2]);
  Serial.print(", ");
  Serial.print(histogram[3]);
  Serial.print(", ");
  Serial.print(histogram[4]);
  Serial.print(", ");
  Serial.println(histogram[5]);
  Serial.println("===========");
  return roll;
}

int scaleSlider(int analogReadValue) {
  // In hardware, the analog slider is "backwards", with 1023 being low and 0 high
  // So, we run from 6 through to 1:
  
  // Ranges are:
  // 0-127    -> 6
  // 128-255  -> 5
  // 256-383  -> 4
  // 384-639  -> 0 (Fair weighted)
  // 640-767  -> 3
  // 768-895  -> 2
  // 896-1023 -> 1

  if (analogReadValue < 128) {
    return 6;
  } else if (analogReadValue < 256) {
    return 5;
  } else if (analogReadValue < 384) {
    return 4;
  } else if (analogReadValue < 640) {
    return 0;
  } else if (analogReadValue < 768) {
    return 3;
  } else if (analogReadValue < 896) {
    return 2;
  } else if (analogReadValue < 1024) {
    return 1;
  }

  // Should never get here
  testLeds();
  return 0;
}

int getRandom() {
  int slideValue = analogRead(RIG_DICE);
  Serial.print("Slider (Pre-scaling): ");
  Serial.println(slideValue);
  slideValue = scaleSlider(slideValue);
  Serial.print("Slider (Post-scaling): ");
  Serial.println(slideValue);
  
  switch(slideValue) {
    case 0:
      return getRandom(FAIR_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 1:
      return getRandom(ONE_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 2:
      return getRandom(TWO_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 3:
      return getRandom(THREE_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 4:
      return getRandom(FOUR_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 5:
      return getRandom(FIVE_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    case 6:
      return getRandom(SIX_WEIGHTED, WEIGHT_COUNTS[slideValue]);
    default:
      // Should never get here...
      testLeds();
      return 1;
  }
}

void loop() {
  // Clear (or don't clear) the reset LED
  if ((millis() - RESET_LED_MILLIS) > lastResetMillis) {
    lc.setLed(0, 3, RESET_NOW_SETTING+1, false); 
  } else {
    lc.setLed(0, 3, RESET_NOW_SETTING+1, true);
  }

  // Clear the decimal point from the 7-seg display
  if ((millis() - CLOCK_LED_MILLIS) > lastClockMillis) {
    lc.setDigit(0, 1, currentRandom, false);
  }
  
  bool updated = false;
  bool rolled = false;
  // Produces a LOT of output on the serial line.
  // Can be helpful if debugging/adding new features.
  //printState();

  // Toggle output state for input buttons:
  for (int i = 0; i < 6; i++) {
    Bounce* debounced = dice[i].debouncedButton;
    if (debounced->update() && debounced->risingEdge()) {
      dice[i].outputEnabled = !dice[i].outputEnabled;
      updated = true;
    }
  }

  // To keep things simple, toggling output state via the input buttons
  // will skip the rest of the processing; we can catch
  // the clock, settings toggles etc. on the next loop() call instead.
  if (updated) {
    updateLeds();
    updateMutes();
    return;
  }

  // Update settings:
  for (int i = 0; i < 4; i++) {
    Bounce* debounced = settings[i].buttonInput;
    if (debounced->update() && debounced->risingEdge()) {
      settings[i].state = !settings[i].state;
      updated = true;
    }

    debounced = settings[i].jackInput;
    if (debounced->update() && debounced->risingEdge()) {
      settings[i].state = !settings[i].state;
      updated = true;
    }
  }

  if (EXT_CLOCK_DEBOUNCED.update() && EXT_CLOCK_DEBOUNCED.risingEdge()) {
    currentRandom = getRandom();

    if (settings[SKIP_AFTER_SETTING].state) {
      currentSkip = currentRandom;
    } else {
      currentSkip = -1;
    }
    
    lastClockMillis = millis();
    updated = true;
    rolled = true;
  }

  if (updated) {
    updateState(rolled);
    updateLeds();
    updateMutes();
  }
}
