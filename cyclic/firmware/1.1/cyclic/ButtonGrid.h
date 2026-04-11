#ifndef BUTTONGRID
#define BUTTONGRID
#include "MCP23S17.h"
#include "SequencerTrack.h"

struct ButtonToTrack {
  SequencerTrack* track;
  int index;
};

class ButtonGrid {
  public:
    ButtonGrid(MCP23S17* mcp23S17, ButtonToTrack (&buttonToTrackA)[8], ButtonToTrack (&buttonToTrackB)[8]);
    MCP23S17* mcp23S17;
    static ButtonGrid* instance;
    void loop();
    void begin();
    void isrRouter(int index);
  private:
    // Updated within ISR:
    volatile bool requiresUpdateA;
    volatile bool requiresUpdateB;

    // Button -> track maps
    ButtonToTrack (&buttonToTrackA)[8]; // Map<buttonNumber, track+number>
    ButtonToTrack (&buttonToTrackB)[8]; // Map<buttonNumber, track+number>

    // Button tracking to better handle hold state
    uint8_t pressedA = 0;
    uint8_t pressedB = 0;

    void processButtonSide(int regA, int regB, uint8_t& pressed, const ButtonToTrack (&buttonToTrack)[8]);
};

struct GridAndSide {
  ButtonGrid* grid;
  int index;
};

#endif