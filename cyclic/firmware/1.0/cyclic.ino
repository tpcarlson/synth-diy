#include <Adafruit_NeoPixel.h>
#define NUMPIXELS 16
#define NUMSEGMENTS 8
#define PIXEL_PIN 10
#define DELAYVAL 50

#include "MCP23S17.h"
#include <TimerEvent.h>

#include "SequencerTrack.h"
#include "ButtonGrid.h"

// BUGS/issues:
// - Need to make sure the "Generic RP2350" is set to the B varient for pins beyond 30
// - Hardware addressing for MCP23S17 SPI
// - MCP23S17 ICs don't really like the RP2350's firmware being updated. A hardware revision
// is needed to fix to tie a GPIO pin to all of the MCP23S17 reset pins. For now, 7 of the 8
// ICs seem okay (ish) but generate a LOT of spurious interrupts. The last one completely fails
// and won't work until power-cycled.
// - There is no configuration support at all. A future hardware revision should add an SD card,
// or with the current hardware, USB mass storage support (This might break flashing firmware to the board, though!)

// Need to test:
// MIDI in

// Ideally use hardware SPI, but this will validate the data lines etc. at least...
// MCP23S17(uint8_t select, uint8_t dataIn, uint8_t dataOut, uint8_t clock, uint8_t address = 0x00) constructor SOFTWARE SPI.
MCP23S17 MCP0(33, 16, 19, 18, 0b000);
MCP23S17 MCP1(21, 16, 19, 18, 0b001);
MCP23S17 MCP2(13, 16, 19, 18, 0b010);
MCP23S17 MCP3(5, 16, 19, 18, 0b011);
MCP23S17 MCP4(9, 16, 19, 18, 0b100);
MCP23S17 MCP5(17, 16, 19, 18, 0b101);
MCP23S17 MCP6(25, 16, 19, 18, 0b110);
MCP23S17 MCP7(29, 16, 19, 18, 0b111);

// Weird ordering because of physical layout!
MCP23S17 MCPs[8] = {MCP4, MCP5, MCP6, MCP7, MCP0, MCP1, MCP2, MCP3};
int setupSuccess[8];

Adafruit_NeoPixel pixels(NUMPIXELS * NUMSEGMENTS, PIXEL_PIN, NEO_GRB + NEO_KHZ800);

int stepToPixel0[16] = { 60, 59, 52, 51, 
                         44, 43, 36, 35, 
                         28, 27, 20, 19, 
                         12, 11,  4,  3 };
int stepToPixel1[16] = { 61, 58, 53, 50, 
                         45, 42, 37, 34, 
                         29, 26, 21, 18, 
                         13, 10,  5,  2 };
int stepToPixel2[16] = { 62, 57, 54, 49, 
                         46, 41, 38, 33, 
                         30, 25, 22, 17, 
                         14, 9,  6,  1 };
int stepToPixel3[16] = { 63, 56, 55, 48, 
                         47, 40, 39, 32, 
                         31, 24, 23, 16, 
                         15, 8,  7,  0 };

int stepToPixel4[16] = { 64, 71, 72, 79, 
                         80, 87, 88, 95, 
                         96, 103, 104, 111, 
                         112, 119, 120, 127 };
int stepToPixel5[16] = { 65, 70, 73, 78, 
                         81, 86, 89, 94, 
                         97, 102, 105, 110, 
                         113, 118,  121,  126 };
int stepToPixel6[16] = { 66, 69, 74, 77, 
                         82, 85, 90, 93, 
                         98, 101, 106, 109, 
                         114, 117,  122,  125 };
int stepToPixel7[16] = { 67, 68, 75, 76, 
                         83, 84, 91, 92, 
                         99, 100, 107, 108, 
                         115, 116,  123,  124 };

// Pins for the clock inputs:
int clockInputPins[8] = { 31, 32, 34, 35, 36, 37, 38, 39 };

// Clock output pins are on GPIOs 40-47

// Top half
SequencerTrack track0 = SequencerTrack(&pixels, stepToPixel0, 10, 36, 40); // drumbrute impact kick
SequencerTrack track1 = SequencerTrack(&pixels, stepToPixel1, 10, 37, 41);
SequencerTrack track2 = SequencerTrack(&pixels, stepToPixel2, 10, 42, 42);
SequencerTrack track3 = SequencerTrack(&pixels, stepToPixel3, 10, 39, 43);

// Bottom half (Different pixel layout)
SequencerTrack track4 = SequencerTrack(&pixels, stepToPixel4, 10, 40, 44);
SequencerTrack track5 = SequencerTrack(&pixels, stepToPixel5, 10, 43, 45);
SequencerTrack track6 = SequencerTrack(&pixels, stepToPixel6, 10, 44, 46);
SequencerTrack track7 = SequencerTrack(&pixels, stepToPixel7, 10, 45, 47);

SequencerTrack* allTracks[8] { &track0, &track1, &track2, &track3, &track4, &track5, &track6, &track7 };

ButtonToTrack buttonsToTracks0A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks0B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks1A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks1B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks2A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks2B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks3A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks3B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks4A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks4B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks5A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks5B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks6A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks6B[8] = {nullptr, 0};

ButtonToTrack buttonsToTracks7A[8] = {nullptr, 0};
ButtonToTrack buttonsToTracks7B[8] = {nullptr, 0};

TimerEvent clockTrigger;

bool needsLedUpdate = false;

// Naming is the same as the hardware.
// Top-left through top-right
ButtonGrid grid7 = ButtonGrid(26, 27, &MCP7, buttonsToTracks0A, buttonsToTracks0B);
ButtonGrid grid6 = ButtonGrid(23, 24, &MCP6, buttonsToTracks1A, buttonsToTracks1B);
ButtonGrid grid5 = ButtonGrid(14, 15, &MCP5, buttonsToTracks2A, buttonsToTracks2B);
ButtonGrid grid4 = ButtonGrid(6, 4, &MCP4, buttonsToTracks3A, buttonsToTracks3B);
// Bottom-left through bottom-right
ButtonGrid grid0 = ButtonGrid(28, 30, &MCP0, buttonsToTracks4A, buttonsToTracks4B);
ButtonGrid grid1 = ButtonGrid(20, 22, &MCP1, buttonsToTracks5A, buttonsToTracks5B);
ButtonGrid grid2 = ButtonGrid(11, 12, &MCP2, buttonsToTracks6A, buttonsToTracks6B);
ButtonGrid grid3 = ButtonGrid(2, 3, &MCP3, buttonsToTracks7A, buttonsToTracks7B);

// This is a map<pinNumber, ButtonGrid>. As each GPIO expander has a pair of interrupt
// pins, this will waste 16 pointers worth of array, but it's a good alternative to a
// std::map without any of the map's baggage.
GridAndSide allGrids[32] = {nullptr, 0};

void fillButtonToTrack(SequencerTrack* first, 
                       SequencerTrack* second, 
                       ButtonToTrack allocatedButtonToTracks[8], 
                       int mcpSegment, 
                       int indexOffset) {
  ButtonToTrack button0 {.track=first, .index=0+indexOffset};
  ButtonToTrack button1 {.track=first, .index=1+indexOffset};
  ButtonToTrack button2 {.track=first, .index=2+indexOffset};
  ButtonToTrack button3 {.track=first, .index=3+indexOffset};

  ButtonToTrack button4 {.track=second, .index=0+indexOffset};
  ButtonToTrack button5 {.track=second, .index=1+indexOffset};
  ButtonToTrack button6 {.track=second, .index=2+indexOffset};
  ButtonToTrack button7 {.track=second, .index=3+indexOffset};

  // Bottom half:
  // A layout:
  if (mcpSegment == 0) {
    allocatedButtonToTracks[0] = button0;
    allocatedButtonToTracks[1] = button1;
    allocatedButtonToTracks[2] = button4;
    allocatedButtonToTracks[3] = button5;
    allocatedButtonToTracks[4] = button6;
    allocatedButtonToTracks[5] = button7;
    allocatedButtonToTracks[6] = button3;
    allocatedButtonToTracks[7] = button2;
  }
  // B layout:
  else if (mcpSegment == 1) {
    allocatedButtonToTracks[0] = button6;
    allocatedButtonToTracks[1] = button7;
    allocatedButtonToTracks[2] = button3;
    allocatedButtonToTracks[3] = button2;
    allocatedButtonToTracks[4] = button1;
    allocatedButtonToTracks[5] = button0;
    allocatedButtonToTracks[6] = button5;
    allocatedButtonToTracks[7] = button4;
  }
  // Top half:
  // A layout:
  else if (mcpSegment == 2) {
    allocatedButtonToTracks[0] = button7;
    allocatedButtonToTracks[1] = button6;
    allocatedButtonToTracks[2] = button3;
    allocatedButtonToTracks[3] = button2;
    allocatedButtonToTracks[4] = button1;
    allocatedButtonToTracks[5] = button0;
    allocatedButtonToTracks[6] = button4;
    allocatedButtonToTracks[7] = button5;
  }
  // B layout:
  else if (mcpSegment == 3) {
    allocatedButtonToTracks[0] = button1;
    allocatedButtonToTracks[1] = button0;
    allocatedButtonToTracks[2] = button4;
    allocatedButtonToTracks[3] = button5;
    allocatedButtonToTracks[4] = button6;
    allocatedButtonToTracks[5] = button7;
    allocatedButtonToTracks[6] = button2;
    allocatedButtonToTracks[7] = button3;
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.setTX(0);
  Serial1.setRX(1);
  Serial1.begin(31250);

  delay(500);

  // put your setup code here, to run once:
  pixels.begin();

  MCP0.begin(true);
  MCP1.begin(true);
  MCP2.begin(true);
  MCP3.begin(true);
  MCP4.begin(true);
  MCP5.begin(true);
  MCP6.begin(true);
  MCP7.begin(true);

  for (int mcpNum = 0; mcpNum < 8; mcpNum++) {
    // "hardware addresses" just means the weird i2c-over-spi address pins
    // Because every GPIO expander got its own CS line, can ignore this.
    // MCPs[mcpNum].enableHardwareAddress();

    // Input mode, both banks
    MCPs[mcpNum].pinMode8(0, 0xFF);
    MCPs[mcpNum].pinMode8(1, 0xFF);

    // Pullups (yes)
    MCPs[mcpNum].setPullup8(0, 0xFF);
    MCPs[mcpNum].setPullup8(1, 0xFF);

    // Verify 2-way comms
    setupSuccess[mcpNum] = testConnection(MCPs[mcpNum]);

    // Enable interrupts. This is "CHANGE" which will fire an interrupt
    // when the button is pressed and released. Button presses need to
    // be debounced.
    MCPs[mcpNum].enableInterrupt8(0, 0xFF, CHANGE);
    MCPs[mcpNum].enableInterrupt8(1, 0xFF, CHANGE);

    MCPs[mcpNum].setPolarity8(0, false);
    MCPs[mcpNum].setPolarity8(1, false);
  }

  // Clock inputs:
  pinMode(31, INPUT);
  pinMode(32, INPUT);
  pinMode(34, INPUT);
  pinMode(35, INPUT);
  pinMode(36, INPUT);
  pinMode(37, INPUT);
  pinMode(38, INPUT);
  pinMode(39, INPUT);

  // Gate outputs:
  pinMode(40, OUTPUT);
  pinMode(41, OUTPUT);
  pinMode(42, OUTPUT);
  pinMode(43, OUTPUT);
  pinMode(44, OUTPUT);
  pinMode(45, OUTPUT);
  pinMode(46, OUTPUT);
  pinMode(47, OUTPUT);

  // Test timer
  // clockTrigger.set(250, clockCallback);

  pixels.clear();

  // Top half
  fillButtonToTrack(&track0, &track1, buttonsToTracks0A, 2, 0);
  fillButtonToTrack(&track2, &track3, buttonsToTracks0B, 3, 0);

  fillButtonToTrack(&track0, &track1, buttonsToTracks1A, 2, 4);
  fillButtonToTrack(&track2, &track3, buttonsToTracks1B, 3, 4);

  fillButtonToTrack(&track0, &track1, buttonsToTracks2A, 2, 8);
  fillButtonToTrack(&track2, &track3, buttonsToTracks2B, 3, 8);

  fillButtonToTrack(&track0, &track1, buttonsToTracks3A, 2, 12); // working
  fillButtonToTrack(&track2, &track3, buttonsToTracks3B, 3, 12); // working

  // Bottom half
  fillButtonToTrack(&track4, &track5, buttonsToTracks4B, 1, 0);
  fillButtonToTrack(&track6, &track7, buttonsToTracks4A, 0, 0);

  fillButtonToTrack(&track4, &track5, buttonsToTracks5B, 1, 4);
  fillButtonToTrack(&track6, &track7, buttonsToTracks5A, 0, 4);

  fillButtonToTrack(&track4, &track5, buttonsToTracks6B, 1, 8);
  fillButtonToTrack(&track6, &track7, buttonsToTracks6A, 0, 8);

  fillButtonToTrack(&track4, &track5, buttonsToTracks7B, 1, 12);
  fillButtonToTrack(&track6, &track7, buttonsToTracks7A, 0, 12);

  grid0.begin();
  grid1.begin();
  grid2.begin();
  grid3.begin();
  grid4.begin();
  grid5.begin();
  grid6.begin();
  grid7.begin();

  // ButtonToTrack buttonsToTracks4A[8] = {nullptr, 0};
  // Set up grids and interrupt handler pins:
  // Top half:
  allGrids[27] = {.grid=&grid7, .index=1};
  allGrids[26] = {.grid=&grid7, .index=0};

  allGrids[24] = {.grid=&grid6, .index=1};
  allGrids[23] = {.grid=&grid6, .index=0};

  allGrids[15] = {.grid=&grid5, .index=1};
  allGrids[14] = {.grid=&grid5, .index=0};

  allGrids[6] = {.grid=&grid4, .index=1};
  allGrids[4] = {.grid=&grid4, .index=0};

  // Bottom half:
  allGrids[28] = {.grid=&grid0, .index=0};
  allGrids[30] = {.grid=&grid0, .index=1};

  allGrids[20] = {.grid=&grid1, .index=0};
  allGrids[22] = {.grid=&grid1, .index=1};

  allGrids[11] = {.grid=&grid2, .index=0};
  allGrids[12] = {.grid=&grid2, .index=1};

  allGrids[2] = {.grid=&grid3, .index=0};
  allGrids[3] = {.grid=&grid3, .index=1};

  // Set up a global callback handler for ALL gpio pins that need it (Interrupt pins from the GPIO expanders)
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  pinMode(6, INPUT);
  pinMode(11, INPUT);
  pinMode(12, INPUT);
  pinMode(14, INPUT);
  pinMode(15, INPUT);
  pinMode(20, INPUT);
  pinMode(22, INPUT);
  pinMode(23, INPUT);
  pinMode(24, INPUT);
  pinMode(26, INPUT);
  pinMode(27, INPUT);
  pinMode(28, INPUT);
  pinMode(30, INPUT);
  gpio_set_irq_enabled_with_callback (2, GPIO_IRQ_EDGE_RISE, true, callback);
  gpio_set_irq_enabled(3, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(4, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(6, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(11, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(12, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(14, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(15, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(20, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(22, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(23, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(24, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(26, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(27, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(28, GPIO_IRQ_EDGE_RISE, true);
  gpio_set_irq_enabled(30, GPIO_IRQ_EDGE_RISE, true);

  // Re-use the GPIO interrupt handler for the clock inputs too. If this becomes a problem, the clock
  // inputs should be moved to the second RP2350 core instead, and a new interrupt handler registered
  // on that core (gpio_set_irq_enabled_with_callback specifies the interrupt handlers are a PER CORE thing)
  for (int i=0; i<8; i++) {
    gpio_set_irq_enabled(clockInputPins[i], GPIO_IRQ_EDGE_FALL, true);
  }

  delay(5000);
  // Check that the GPIO chips were set up as expected:
  for (int mcpNum=0; mcpNum < 8; mcpNum++) {
    Serial.println(setupSuccess[mcpNum]);
  }
}

void callback(unsigned int gpio, long unsigned int events) {
  // GPIO interrupts for the clock inputs and GPIO expanders are different. The GPIO expanders are active-high,
  // and the clock inputs active-low. This means we can dispatch events nice and easily! Hurray!
  if (events == GPIO_IRQ_EDGE_FALL) {
    // There is no map for the clock input pins, so do the dumb thing and search through until the proper clock
    // input pin is found:
    for (int i=0; i<8; i++) {
      if(clockInputPins[i] == gpio) {
        allTracks[i]->clockSequencer();
      }
    }
  }
  // Assumed GPIO_IRQ_EDGE_RISE
  else {
    allGrids[gpio].grid->isrRouter(allGrids[gpio].index);
  }
}

void clockCallback() {
  track0.clockSequencer();
  track1.clockSequencer();
  //track2.clockSequencer();
  //track3.clockSequencer();
  //track4.clockSequencer();
  //track5.clockSequencer();
  //track6.clockSequencer();
  //track7.clockSequencer();
}

void loop() {
  // Just read a value, no idea why this isn't working properly
  //Serial.println(MCP0.read8(0));
  //Serial.println(MCP0.read8(1));

  clockTrigger.update();

  if (track0.needsLedUpdate() || 
      track1.needsLedUpdate() || 
      track2.needsLedUpdate() || 
      track3.needsLedUpdate() || 
      track4.needsLedUpdate() || 
      track5.needsLedUpdate() || 
      track6.needsLedUpdate() || 
      track7.needsLedUpdate()) {
    needsLedUpdate = true;
  }

  if (needsLedUpdate) {
    pixels.show();
    needsLedUpdate = false;
    track0.resetNeedsLedUpdate();
    track1.resetNeedsLedUpdate();
    track2.resetNeedsLedUpdate();
    track3.resetNeedsLedUpdate();
    track4.resetNeedsLedUpdate();
    track5.resetNeedsLedUpdate();
    track6.resetNeedsLedUpdate();
    track7.resetNeedsLedUpdate();
  }

  track0.loop();
  track1.loop();
  track2.loop();
  track3.loop();
  track4.loop();
  track5.loop();
  track6.loop();
  track7.loop();

  grid0.loop();
  grid1.loop();
  grid2.loop();
  grid3.loop();
  grid4.loop();
  grid5.loop();
  grid6.loop();
  grid7.loop();
}

int testConnection(MCP23S17 & mcp)
{
  uint16_t magic_test_number = 0xABCD;

  //  Read the current polarity config to restore later
  uint16_t old_value;
  if (! mcp.getPolarity16(old_value)) return -1;

  //  Write the magic number to polarity register
  if (! mcp.setPolarity16(magic_test_number)) return -2;

  //  Read back the magic number from polarity register
  uint16_t temp;
  if (! mcp.getPolarity16(temp)) return -3;

  //  Write old config to polarity register
  if (! mcp.setPolarity16(old_value)) return -4;

  //  Check the magic connection test
  if (temp != magic_test_number) return -5;

  return 0;  //  OK
}
