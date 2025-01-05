#include <SPI.h>
#include <Adafruit_NeoPixel.h>

#define RP2040_LED 25

#define DRIVER_A_PIN 7
#define DRIVER_B_PIN 6

#define DAC_SPI_CLOCK 2
#define DAC_SPI_DIN 3
#define DAC_SPI_SYNC 5

// DAC output channels
#define CHROMATIC_A_CHAN 2
#define CHROMATIC_B_CHAN 0
#define QUANTISED_A_CHAN 3
#define QUANTISED_B_CHAN 1

// WS2812B (Xinglight 1010 LEDs)
#define WS2812B_PIN 12
#define LED_COUNT 12
Adafruit_NeoPixel pixels(LED_COUNT, WS2812B_PIN, NEO_GRB + NEO_KHZ800);

const uint16_t updateChromaticA = (2 << 14) | (CHROMATIC_A_CHAN << 12);
const uint16_t updateQuantisedA = (2 << 14) | (QUANTISED_A_CHAN << 12);
const uint16_t updateChromaticB = (2 << 14) | (CHROMATIC_B_CHAN << 12);
const uint16_t updateQuantisedB = (2 << 14) | (QUANTISED_B_CHAN << 12);
const uint16_t updateAllOutputs = (3 << 14) | (2 << 12);

void setup() {
  // put your setup code here, to run once:
  pinMode(RP2040_LED, OUTPUT);

  // Trig outputs
  pinMode(DRIVER_A_PIN, OUTPUT);
  pinMode(DRIVER_B_PIN, OUTPUT);

  // No need to set SPI RX, nor CS, for the DAC7554
  //SPI.setTX(DAC_SPI_DIN);
  //SPI.setSCK(DAC_SPI_CLOCK);
  //SPI.setCS(DAC_SPI_SYNC);
  pinMode(DAC_SPI_DIN, OUTPUT);
  pinMode(DAC_SPI_CLOCK, OUTPUT);
  pinMode(DAC_SPI_SYNC, OUTPUT);

  // Pixel setup
  pixels.begin();

  // Serial port for debugging
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(RP2040_LED, HIGH);
  digitalWrite(DRIVER_A_PIN, HIGH);
  digitalWrite(DRIVER_B_PIN, HIGH);
  writeToDac(4095);
  writeToPixels(0, 0, 32);
  sleep_ms(500);
  digitalWrite(RP2040_LED, LOW);
  digitalWrite(DRIVER_A_PIN, LOW);
  digitalWrite(DRIVER_B_PIN, LOW);
  writeToDac(0);
  writeToPixels(0, 32, 0);
  sleep_ms(500);
}

void writeToPixels(int r, int g, int b) {
  // LED bleed test:
  pixels.clear();
  pixels.setPixelColor(random(0, LED_COUNT), pixels.Color(random(0, 32), random(0, 32), random(0, 32)));
  pixels.show();

  // LED colour test:
  // for (int i=0; i < LED_COUNT; i++) {
  //   pixels.setPixelColor(i, r, g, b);
  //   pixels.show();
  // }
}

// Write the same value to all channels
void writeToDac(uint16_t value) {
  uint16_t maskedVal = updateAllOutputs | value;
  Serial.println(maskedVal, BIN);
  long millisBefore = micros();
  digitalWrite(DAC_SPI_SYNC, LOW);
  shiftOut(DAC_SPI_DIN, DAC_SPI_CLOCK, MSBFIRST, maskedVal >> 8);
  shiftOut(DAC_SPI_DIN, DAC_SPI_CLOCK, MSBFIRST, maskedVal);
  digitalWrite(DAC_SPI_SYNC, HIGH);
  long millisAfter = micros();
  Serial.println(millisAfter - millisBefore);
  // About 50 microseconds to shiftOut()
}