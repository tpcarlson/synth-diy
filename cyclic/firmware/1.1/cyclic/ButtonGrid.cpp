#include "ButtonGrid.h"
#include "Arduino.h"
#include "MCP23S17.h"
#include "SequencerTrack.h"

const uint8_t BUTTON_MASK = 0b10000000;

// TODO: Debounce button inputs! This hasn't really been necessary so far, but might be nice to do.
ButtonGrid* ButtonGrid::instance = nullptr;

ButtonGrid::ButtonGrid(MCP23S17* mcp23S17, ButtonToTrack (&buttonToTrackA)[8], ButtonToTrack (&buttonToTrackB)[8])
   : mcp23S17(mcp23S17), buttonToTrackA(buttonToTrackA), buttonToTrackB(buttonToTrackB) {
  instance = this;
}

void ButtonGrid::begin() {
}

void ButtonGrid::processButtonSide(int regA, int regB, uint8_t& pressed, const ButtonToTrack (&buttonToTrack)[8]) {
  int readResult = mcp23S17->getInterruptCaptureRegister8(regA);
  int readResult2 = mcp23S17->getInterruptCaptureRegister8(regB);

  int mask = BUTTON_MASK;
  for (int i = 0; i < 8; i++) {
    int buttonResult = (~readResult) & mask;
    if (buttonResult) {
      if (!(pressed & mask)) {
        buttonToTrack[i].track->toggleActive(buttonToTrack[i].index);
        pressed |= mask;
      }
    } else {
      pressed &= ~mask;
    }
    mask >>= 1;
  }
}

void ButtonGrid::loop() {
  mcp23S17->read8(0);
  mcp23S17->read8(1);

  if (requiresUpdateA) {
    processButtonSide(0, 1, pressedA, buttonToTrackA);
    requiresUpdateA = false;
  }
  if (requiresUpdateB) {
    processButtonSide(1, 0, pressedB, buttonToTrackB);
    requiresUpdateB = false;
  }

  /*
  if (requiresUpdateA) {
    int readResult = mcp23S17->getInterruptCaptureRegister8(0);
    int readResult2 = mcp23S17->getInterruptCaptureRegister8(1);

    int mask = 0b10000000;
    int buttonResult = 0;
    for (int i=0; i<8; i++) {
      buttonResult = (~readResult) & mask;
      if (buttonResult) {
        if (!(pressedA & mask)) {
          Serial.print("Button pressed: ");
          Serial.println(i);
          buttonToTrackA[i].track->toggleActive(buttonToTrackA[i].index);
          pressedA |= mask;
        }
      } else {
        pressedA &= ~mask;
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
        if (!(pressedB & mask)) {
          Serial.print("Button pressed: ");
          Serial.println(i);
          buttonToTrackB[i].track->toggleActive(buttonToTrackB[i].index);
          pressedB |= mask;
        }
      }
      else {
        pressedB &= ~mask;
      }

      mask = mask >> 1;
    }

    requiresUpdateB = false;
  } */
}

// Called from within the GPIO callback, see cyclic.ino.
void ButtonGrid::isrRouter(int index) {
  if (index == 0) {
    requiresUpdateA = true;
  } else if (index == 1) {
    requiresUpdateB = true;
  }
}