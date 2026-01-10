#include "ButtonGrid.h"
#include "Arduino.h"
#include "MCP23S17.h"
#include "SequencerTrack.h"

// TODO: Debounce button inputs!
// Figure out why the MCP23S17 isn't happy if not reading all the time with interrupts enabled
// Wire up button presses to sequencer
// -> Needs a map of button address on A and B ports to 4 sequencer pointers
//    Maybe a struct { SequencerTrack*, sequenceIndex(0-127) }?
//    Then an array of these for the A and B sides (With array index being the map key)
//    16 structs per ButtonGrid, 128 total

ButtonGrid* ButtonGrid::instance = nullptr;

ButtonGrid::ButtonGrid(int interruptA, int interruptB, MCP23S17* mcp23S17, ButtonToTrack (&buttonToTrackA)[8], ButtonToTrack (&buttonToTrackB)[8])
   : interruptA(interruptA), interruptB(interruptB), mcp23S17(mcp23S17), buttonToTrackA(buttonToTrackA), buttonToTrackB(buttonToTrackB) {
  instance = this;
}

void ButtonGrid::begin() {
  //delay(5000);
  //attachInterrupt(digitalPinToInterrupt(interruptA), isrRouterA, CHANGE);
  //attachInterrupt(digitalPinToInterrupt(interruptB), isrRouterB, CHANGE);
  //Serial.println("Attached ISRs");
  //Serial.println(interruptA);
  //Serial.println(interruptB);
}

void ButtonGrid::loop() {
  // TODO: This is hacky, but seems to fix reads only working once...
  mcp23S17->read8(0);
  mcp23S17->read8(1);
  if (requiresUpdateA) {
    int readResult = mcp23S17->getInterruptCaptureRegister8(0);
    int readResult2 = mcp23S17->getInterruptCaptureRegister8(1);

    int mask = 0b10000000;
    int buttonResult = 0;
    for (int i=0; i<8; i++) {
      buttonResult = (~readResult) & mask;
      if (buttonResult) {
        Serial.print("Button pressed: ");
        Serial.println(i);
        // Handle button press?
        buttonToTrackA[i].track->toggleActive(buttonToTrackA[i].index);
      }
      mask = mask >> 1;
    }

    requiresUpdateA = false;
  }

  if (requiresUpdateB) {
    int readResult = mcp23S17->getInterruptCaptureRegister8(1);
    int readResult2 = mcp23S17->getInterruptCaptureRegister8(0);
    int mask = 0b10000000;
    int buttonResult = 0;
    for (int i=0; i<8; i++) {
      buttonResult = (~readResult) & mask;
      if (buttonResult) {
        Serial.print("Button pressed: ");
        Serial.println(i);
        // Handle button press?
        buttonToTrackB[i].track->toggleActive(buttonToTrackB[i].index);
      }
      mask = mask >> 1;
    }

    requiresUpdateB = false;
  }
}

void ButtonGrid::isrRouter(int index) {
  if (index == 0) {
    requiresUpdateA = true;
  } else if (index == 1) {
    requiresUpdateB = true;
  }
}