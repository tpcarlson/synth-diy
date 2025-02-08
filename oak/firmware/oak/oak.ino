#include "OneButton.h"
#include <Wire.h>

#define SCALE_SHUFFLE_LED D7
#define SCALE_RESET_LED D10
#define LOOP_RESET_LED D6
#define LOOP_START_LED D11

#define QUANTIZE_LED D12
#define SHIFT_LED D3
#define RANGE_LED D15
#define LENGTH_LED D0

#define LOOP_OUTPUT D23
#define NOTE_OUTPUT D22
#define STEP_OUTPUT D19

// Default LED pulse is 10ms, but can be modified
#define LED_PULSE_MILLIS 10
#define OUTPUT_TRIGGER_MILLIS 50

#define I2C_ADDRESS 0x42
#define I2C_SDA D4
#define I2C_SCL D5
#define I2C_CLOCK_SPEED 1000000

OneButton scaleButton;
OneButton loopButton;
OneButton shiftButton;
OneButton quantizeButton;
OneButton lengthButton;
OneButton rangeButton;
OneButton scaleShuffleInput;
OneButton scaleResetInput;
OneButton loopResetInput;
OneButton* allButtons[9];

// State for the 4 top LED millis
unsigned long scaleShuffleLedMillis;
unsigned long scaleResetLedMillis;
unsigned long loopResetLedMillis;
unsigned long loopStartLedMillis;

// State for the 4 toggle buttons.
// Consider refactoring to an int with mask.
volatile bool shiftLock = false;
volatile bool quantizeLock = false;
volatile bool lengthLock = false;
volatile bool rangeLock = false;

// State for the 3 outputs (Loop, note, and step)
unsigned long loopOutputMillis;
unsigned long noteOutputMillis;
unsigned long stepOutputMillis;

// i2c receive
volatile bool i2cReceived = false;
volatile int i2cReceivedData;
/*
* i2c data for Sycamore -> Oak:
* led duration | loop start | note change | step | shift | quant | length | range
* 8 bits or 1 byte
*/
const int ledDurationMask = 0b10000000;
const int loopStartMask = 0b01000000;
const int noteChangeMask = 0b00100000;
const int stepMask = 0b00010000;
const int shiftMask = 0b00001000;
const int quantMask = 0b00000100;
const int lengthMask = 0b00000010;
const int rangeMask = 0b00000001;

// i2c send
/*
 * i2c data for Oak -> Sycamore:
 *  UNUSED | scale shuffle | scale reset | reset loop | shift | quant | length | range
 */
const int scaleShuffleMask = 0b01000000;
const int scaleResetMask = 0b00100000;
const int resetLoopMask = 0b00010000;
// Shift, quant, length, range shared with i2c receive

// Storage for button and input presses
volatile bool scaleClicked = false;
volatile bool loopClicked = false;
volatile bool scaleResetClicked = false;

// LED pulse duration. Should always be >1ms.
int ledPulseMillis = LED_PULSE_MILLIS;

void setup() {
  Serial.begin(9600);
  setupButtons();
  setupCallbacks();
  setupLeds();
  setupOutputs();
  setupi2c();
}

void setupButtons() {
  // Top buttons
  scaleButton.setup(D9, INPUT_PULLUP, true);
  loopButton.setup(D8, INPUT_PULLUP, true);

  // Mid buttons
  shiftButton.setup(D2, INPUT_PULLUP, true);
  quantizeButton.setup(D13, INPUT_PULLUP, true);
  lengthButton.setup(D1, INPUT_PULLUP, true);
  rangeButton.setup(D14, INPUT_PULLUP, true);

  // Inputs, treated as buttons. These have a very low (1ms) debounce.
  scaleShuffleInput.setup(D24, INPUT_PULLUP, true);
  scaleShuffleInput.setDebounceMs(1);
  scaleResetInput.setup(D21, INPUT_PULLUP, true);
  scaleResetInput.setDebounceMs(1);
  loopResetInput.setup(D20, INPUT_PULLUP, true);
  loopResetInput.setDebounceMs(1);

  allButtons[0] = &scaleButton;
  allButtons[1] = &loopButton;
  allButtons[2] = &shiftButton;
  allButtons[3] = &quantizeButton;
  allButtons[4] = &lengthButton;
  allButtons[5] = &rangeButton;
  allButtons[6] = &scaleShuffleInput;
  allButtons[7] = &scaleResetInput;
  allButtons[8] = &loopResetInput;
}

void setupCallbacks() {
  scaleButton.attachClick(scaleClick);
  loopButton.attachClick(loopClick);
  shiftButton.attachClick(shiftClick);
  quantizeButton.attachClick(quantizeClick);
  lengthButton.attachClick(lengthClick);
  rangeButton.attachClick(rangeClick);

  // Unlike the buttons, immediately trigger scale shuffle,
  // scale reset, and loop reset when a trigger is seen. I
  // combination with the low debounce ms, this should reduce
  // the time between triggers being seen and acted upon.
  scaleShuffleInput.attachPress(scaleClick);  // Same as scale button
  scaleResetInput.attachPress(scaleResetClick);
  loopResetInput.attachPress(loopClick); // Same as loop button
}

void setupLeds() {
  pinMode(SCALE_SHUFFLE_LED, OUTPUT);
  pinMode(SCALE_RESET_LED, OUTPUT);
  pinMode(LOOP_RESET_LED, OUTPUT);
  pinMode(LOOP_START_LED, OUTPUT);
  pinMode(QUANTIZE_LED, OUTPUT);
  pinMode(SHIFT_LED, OUTPUT);
  pinMode(RANGE_LED, OUTPUT);
  pinMode(LENGTH_LED, OUTPUT);
}

void setupOutputs() {
  pinMode(LOOP_OUTPUT, OUTPUT);
  pinMode(NOTE_OUTPUT, OUTPUT);
  pinMode(STEP_OUTPUT, OUTPUT);
}

void setupi2c() {
  Wire.setSDA(I2C_SDA);
  Wire.setSCL(I2C_SCL);
  Wire.setClock(I2C_CLOCK_SPEED);
  Wire.begin(I2C_ADDRESS);

  Wire.onReceive(receiveData);
  Wire.onRequest(dataRequested);
}

// Receive data from Sycamore. 
// Update internal state, but do so
// quickly as this is in an interrupt.
// Asking for data twice in quick succession
// will lead to the data in the second 
// request being dropped.
void receiveData(int len) {
  if (!i2cReceived) {
    i2cReceivedData = Wire.read();
    i2cReceived = true;
  }
}

// Send state back to Sycamore.
// Do so quickly as this is in an interrupt
void dataRequested() {
  Serial.println("i2c data requested from Sycamore");
  Wire.write(
    scaleClicked << 6
  | loopClicked << 5
  | scaleResetClicked << 4
  | shiftLock << 3
  | quantizeLock << 2
  | lengthLock << 1
  | rangeLock);

  // Reset triggers. Locks stay as they are.
  scaleClicked = false;
  loopClicked = false;
  scaleResetClicked = false;
}

void loop() {
  updatei2cRead();
  updateButtons();
  updateLeds();
  updateOutputs();
}

// See https://bitwisecmd.com/
void updatei2cRead() {
  if (i2cReceived) {
    bool ledPulseDuration = (i2cReceivedData & ledDurationMask) >> 7;
    if (ledPulseDuration) {
      ledPulseMillis = i2cReceivedData ^ ledDurationMask;
      if (ledPulseMillis == 0) {
        ledPulseMillis = LED_PULSE_MILLIS;
      }
      return;
    }

    // 3 outpouts
    bool loopStart = (i2cReceivedData & loopStartMask) >> 6;
    bool noteChange = (i2cReceivedData & noteChangeMask) >> 5;
    bool step = (i2cReceivedData & stepMask) >> 4;

    // 4 LED toggles (These are confirmation/checks that Sycamore and Oak are in sync)
    bool shift = (i2cReceivedData & shiftMask) >> 3;
    bool quant = (i2cReceivedData & quantMask) >> 2;
    bool length = (i2cReceivedData & lengthMask) >> 1;
    bool range = i2cReceivedData & rangeMask;

    unsigned long currentTime = millis();
    if (loopStart) {
      loopOutputMillis = currentTime;
      loopStartLedMillis = currentTime;
      analogWrite(LOOP_START_LED, 10);
      digitalWrite(LOOP_OUTPUT, HIGH);
    }

    // Note change does not have an associated LED
    if (noteChange) {
      noteOutputMillis = currentTime;
      digitalWrite(NOTE_OUTPUT, HIGH);
    }

    // Step does not have an associated LED
    if (step) {
      stepOutputMillis = currentTime;
      digitalWrite(STEP_OUTPUT, HIGH);
    }

    // This should never happen, but validate that the locks all look the same
    // across both modules. Resetting the state of Oak to match Sycamore's state
    // is OK.
    if (shiftLock != shift) {
      shiftLock = shift;
      digitalWrite(SHIFT_LED, shiftLock);
      Serial.print("Shift lock state mismatch, correcting...");
    }

    if (quantizeLock != quant) {
      quantizeLock = quant;
      digitalWrite(QUANTIZE_LED, quantizeLock);
      Serial.print("Quantize lock state mismatch, correcting...");
    }

    if (lengthLock != length) {
      lengthLock = length;
      digitalWrite(LENGTH_LED, lengthLock);
      Serial.print("Length lock state mismatch, correcting...");
    }

    if (rangeLock != range) {
      rangeLock = range;
      digitalWrite(RANGE_LED, rangeLock);
      Serial.print("Range lock state mismatch, correcting...");
    }

    // If sent another i2c message before processing the first one,
    // the message will be ignored until i2creceived flag has been set.
    // This is unlikely given the sender (Sycamore) is a relatively slow
    // CircuitPython program.
    i2cReceived = false;
  }
}

void updateButtons() {
  for (int i = 0; i < 9; i++) {
    allButtons[i]->tick();
  }
}

// Diable any LEDs which have been lit for long enough
// Future optimisation if needed: Add a flag to indicate
// "all LEDs are off" and skip updateLeds()
void updateLeds() {
  unsigned long currentTime = millis();
  if (scaleShuffleLedMillis + ledPulseMillis < currentTime) {
    digitalWrite(SCALE_SHUFFLE_LED, LOW);
  }

  if (scaleResetLedMillis + ledPulseMillis < currentTime) {
    digitalWrite(SCALE_RESET_LED, LOW);
  }

  if (loopResetLedMillis + ledPulseMillis < currentTime) {
    digitalWrite(LOOP_RESET_LED, LOW);
  }

  if (loopStartLedMillis + ledPulseMillis < currentTime) {
    digitalWrite(LOOP_START_LED, LOW);
  }
}

// Diable any triggers which have been high for long enough
// Future optimisation if needed: Add a flag to indicate
// "all outputs are low" and skip updateOutputs()
void updateOutputs() {
  unsigned long currentTime = millis();
  if (loopOutputMillis + OUTPUT_TRIGGER_MILLIS < currentTime) {
    digitalWrite(LOOP_OUTPUT, LOW);
  }

  if (noteOutputMillis + OUTPUT_TRIGGER_MILLIS < currentTime) {
    digitalWrite(NOTE_OUTPUT, LOW);
  }

  if (stepOutputMillis + OUTPUT_TRIGGER_MILLIS < currentTime) {
    digitalWrite(STEP_OUTPUT, LOW);
  }
}

// Button handling callbacks
void scaleClick() {
  Serial.println("Scale shuffle button clicked");
  analogWrite(SCALE_SHUFFLE_LED, 10);
  scaleShuffleLedMillis = millis();
  scaleClicked = true;
}

void loopClick() {
  Serial.println("Loop button clicked");
  analogWrite(LOOP_RESET_LED, 10);
  loopResetLedMillis = millis();
  loopClicked = true;
}

// Trigger input
void scaleResetClick() {
  Serial.print("Scale reset clicked");
  analogWrite(SCALE_RESET_LED, 10);
  scaleResetLedMillis = millis();
  scaleResetClicked = true;
}

// LED button callbacks
void shiftClick() {
  shiftLock = !shiftLock;
  digitalWrite(SHIFT_LED, shiftLock);
}

void quantizeClick() {
  quantizeLock = !quantizeLock;
  digitalWrite(QUANTIZE_LED, quantizeLock);
}

void lengthClick() {
  lengthLock = !lengthLock;
  digitalWrite(LENGTH_LED, lengthLock);
}

void rangeClick() {
  rangeLock = !rangeLock;
  digitalWrite(RANGE_LED, rangeLock);
}