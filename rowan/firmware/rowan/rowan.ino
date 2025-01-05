#include <Adafruit_NeoPixel.h>
#include <Wire.h>

#define RP2040_LED 25

#define DRIVER_A_PIN 7
#define DRIVER_B_PIN 6

#define DAC_SPI_CLOCK 2
#define DAC_SPI_DIN 3
#define DAC_SPI_SYNC 5

// DAC output channels
#define CHROMATIC_A_CHAN   3
#define CHROMATIC_B_CHAN   1
#define UNQUANTISED_A_CHAN 2
#define UNQUANTISED_B_CHAN 0

const uint16_t updateChromaticA = (2 << 14) | (CHROMATIC_A_CHAN << 12);
const uint16_t updateUnquantisedA = (2 << 14) | (UNQUANTISED_A_CHAN << 12);
const uint16_t updateChromaticB = (2 << 14) | (CHROMATIC_B_CHAN << 12);
const uint16_t updateUnquantisedB = (2 << 14) | (UNQUANTISED_B_CHAN << 12);
const uint16_t updateAllOutputs = (3 << 14) | (2 << 12);

// WS2812B (Xinglight 1010 LEDs)
#define WS2812B_PIN 12
#define LED_COUNT 12
Adafruit_NeoPixel pixels(LED_COUNT, WS2812B_PIN, NEO_GRB + NEO_KHZ800);

// For I2C communications with Sycamore
#define I2C_ADDRESS 0x44
#define I2C_SDA 10
#define I2C_SCL 11
#define I2C_CLOCK_SPEED 1000000

// TODO: These should probably be uint16_t as RP2040 has 32-bit ints!
volatile bool i2cReceived = false;
volatile int i2cReceivedData;
volatile int i2cReceivedDataPrevious;
volatile bool ledsUpdated = false;
volatile bool triggersActive = false;

// i2c protocol - Sycamore to Rowan:
/*
(command0 | command1 | command 2 | channel | 12 data bits)
Commands:
0 0 0: allowed
0 0 1: active
0 1 0: unquantized
0 1 1: quantized
1 0 0: red
1 0 1: green
1 1 0: blue

eg.
0 0 0 x (12 data bits) - allowed notes
0 0 1 0 (12 data bits) - active a
0 0 1 1 (12 data bits) - active b
0 1 0 0 (12 data bits) - unquantized a
0 1 0 1 (12 data bits) - unquantized b
0 1 1 0 (12 data bits) - quantized a
0 1 1 1 (12 data bits) - quantized b
1 0 0 x (4 empty) (8 data bits) - Red
1 0 1 x (4 empty) (8 data bits) - Green
1 1 0 x (4 empty) (8 data bits) - Blue

This is a 16-bit data packet, which should fit into 2 bytes, or one 16-bit int.
*/

const int CMD_ALLOWED_NOTES = 0;
const int CMD_ACTIVE_NOTE = 1;
const int CMD_UNQUANT = 2;
const int CMD_QUANT = 3;
const int CMD_RED = 4;
const int CMD_GREEN = 5;
const int CMD_BLUE = 6;

int enabledNotes[LED_COUNT];
int activeNotes[2][LED_COUNT];
long triggersMillis[2] = { 0, 0 };
// Default to white
int red = 42;
int green = 42;
int blue = 42;

#define OUTPUT_TRIGGER_MILLIS 50

// Enabled notes are a little tricky, we need to re-map Sycamore's bit ordering.
// See setActiveNotes() for more details.
#define NOTE_C 11
#define NOTE_CSHARP 0
#define NOTE_D 10
#define NOTE_DSHARP 1
#define NOTE_E 9
#define NOTE_F 8
#define NOTE_FSHARP 2
#define NOTE_G 7
#define NOTE_GSHARP 3
#define NOTE_A 6
#define NOTE_ASHARP 4
#define NOTE_B 5

void setup() {
  // Trig outputs
  pinMode(DRIVER_A_PIN, OUTPUT);
  pinMode(DRIVER_B_PIN, OUTPUT);

  // DAC setup
  pinMode(DAC_SPI_DIN, OUTPUT);
  pinMode(DAC_SPI_CLOCK, OUTPUT);
  pinMode(DAC_SPI_SYNC, OUTPUT);

  // Serial port & LED for debugging
  pinMode(RP2040_LED, OUTPUT);
  Serial.begin(9600);

  setupi2c();

  // Pixel setup
  pixels.begin();

  // Clear LEDs between restarts. This helps during dev-time, 
  // but shouldn't do a whole lot in normal use.
  for (int i = 0; i < LED_COUNT; i++) {
    pixels.setPixelColor(i, 0, 0, 0);
  }
  pixels.show();
}

void setupi2c() {
  digitalWrite(RP2040_LED, HIGH);

  Wire1.setSDA(I2C_SDA);
  Wire1.setSCL(I2C_SCL);
  Wire1.setClock(I2C_CLOCK_SPEED);
  Wire1.begin(I2C_ADDRESS);

  Wire1.onReceive(receiveData);
  i2cReceivedDataPrevious = -1;
  i2cReceived = false;
  digitalWrite(RP2040_LED, LOW);
}

void receiveData(int len) {
  if (!i2cReceived) {
    // MSB first, read 2 bytes. Commands from Sycamore will always be made up of 15-bit packets.
    int rx0 = Wire1.read();
    int rx1 = Wire1.read();
    i2cReceivedData = (rx0 << 8) | rx1;
    i2cReceived = (i2cReceivedDataPrevious != i2cReceivedData); // Repeated same-data will be rejected
  }
}

// TODO: Refactor to update based on i2c data, and apply in separate functions?
// TODO: RP2040 has two cores, could use them both!
void loop() {
  updatei2cRead();
  updateLeds();
  updateTriggers();
}

int updateTrigger(int trigger, unsigned long currentTime, int pin) {
    if (triggersMillis[trigger] + OUTPUT_TRIGGER_MILLIS < currentTime) {
      digitalWrite(pin, LOW);
      return 0;
    }
    return 1;
}

void updateTriggers() {
  if (triggersActive) {
    unsigned long currentTime = millis();
    int changes = 0;
    changes += updateTrigger(0, currentTime, DRIVER_A_PIN);
    changes += updateTrigger(1, currentTime, DRIVER_B_PIN);
    if (changes == 0) {
      triggersActive = false;
    }
  }
}

// Update the LED display. The display has the ordering: Output A, Output B, Enabled notes
// For example, if Output A is an enabled note, the display will light red.
// By default, Sycamore has active notes disabled as I didn't like it very much, and preferred
// the scale display only.
void updateLeds() {
  if (ledsUpdated) {

    for (int i = 0; i < LED_COUNT; i++) {
      int r = 0;
      int g = 0;
      int b = 0;

      if (activeNotes[0][i] == 1) {
        r += 64;
      }
      
      if (activeNotes[1][i] == 1) {
        b += 64;
      }
      
      if (enabledNotes[i] == 1) {
        r += red;
        g += green;
        b += blue;
      } 
      
      pixels.setPixelColor(i, r, g, b);
    }
    pixels.show();
    ledsUpdated = false;
  }
}

int targetToDacChannelUnquantized(int target) {
  return target == 0 ? updateUnquantisedA : updateUnquantisedB;
}

int targetToDacChannelChromatic(int target) {
  return target == 0 ? updateChromaticA : updateChromaticB;
}

int targetToPin(int target) {
  return target == 0 ? DRIVER_A_PIN : DRIVER_B_PIN;
}

void updatei2cRead() {
  if (i2cReceived) {
    int command = i2cReceivedData >> 13; // cmd0 | cmd1 | cmd 2 | (13 bits)
    int target = (i2cReceivedData & 0b001000000000000) >> 12; // cmd1 | cmd2 | target | (12 bits)
    int payload = i2cReceivedData & 0b000111111111111; // skip cmd 1 | cmd 2 | target
    int dacChannel = 0;

    switch(command) {
      case CMD_RED:
        red = payload;
        ledsUpdated = true;
        break;
      case CMD_GREEN:
        green = payload;
        ledsUpdated = true;
        break;
      case CMD_BLUE:
        blue = payload;
        ledsUpdated = true;
        break;
      case CMD_ALLOWED_NOTES:
        setAllowedNotes(payload);
        ledsUpdated = true;
        break;
      case CMD_ACTIVE_NOTE:
        setActiveNote(target, payload);
        ledsUpdated = true;
        break;
      case CMD_UNQUANT:
        writeToDac(targetToDacChannelUnquantized(target), payload);
        break;
      case CMD_QUANT:
        writeToDac(targetToDacChannelChromatic(target), payload);
        digitalWrite(targetToPin(target), HIGH);
        triggersMillis[target] = millis();
        triggersActive = true;
        break;
    }
    i2cReceived = false;
  }
}

void writeToDac(int dacChannel, uint16_t payload) {
  uint16_t maskedVal = dacChannel | payload;
  digitalWrite(DAC_SPI_SYNC, LOW);
  shiftOut(DAC_SPI_DIN, DAC_SPI_CLOCK, MSBFIRST, maskedVal >> 8);
  shiftOut(DAC_SPI_DIN, DAC_SPI_CLOCK, MSBFIRST, maskedVal);
  digitalWrite(DAC_SPI_SYNC, HIGH);
}

void setAllowedNotes(int payload) {
  setActiveNotes(enabledNotes, payload);
}

void setActiveNote(int target, int payload) {
  setActiveNotes(activeNotes[target], payload);
}

// Show the allowed notes on the display. The display is wired up a bit strangely, so
// we need to do a bit of massaging of the incoming data for it to all make sense.
// Sycamore will send data in this order:
// C  C# D  D# E  F F# G G# A A# B
// Ordering in hardware is:
// C# D# F# G# A# B A  G F  E D  C
// 0  1  2  3  4  5 6  7 8  9 10 11
void setActiveNotes(int target[], int payload) {
  target[NOTE_B] = payload & 0b000000000000001;
  target[NOTE_ASHARP] = (payload & 0b000000000000010) >> 1;
  target[NOTE_A] = (payload & 0b000000000000100) >> 2;
  target[NOTE_GSHARP] = (payload & 0b000000000001000) >> 3;
  target[NOTE_G] = (payload & 0b000000000010000) >> 4;
  target[NOTE_FSHARP] = (payload & 0b000000000100000) >> 5;
  target[NOTE_F] = (payload & 0b000000001000000) >> 6;
  target[NOTE_E] = (payload & 0b000000010000000) >> 7;
  target[NOTE_DSHARP] = (payload & 0b000000100000000) >> 8;
  target[NOTE_D] = (payload & 0b000001000000000) >> 9;
  target[NOTE_CSHARP] = (payload & 0b000010000000000) >> 10;
  target[NOTE_C] = (payload & 0b000100000000000) >> 11;
}