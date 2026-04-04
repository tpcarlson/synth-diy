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
    ButtonGrid(int interruptA, int interruptB, MCP23S17* mcp23S17, ButtonToTrack (&buttonToTrackA)[8], ButtonToTrack (&buttonToTrackB)[8]);
    MCP23S17* mcp23S17;
    static ButtonGrid* instance;
    void loop();
    void begin();
    void isrRouter(int index);
  private:
    // Updated within ISR:
    volatile bool requiresUpdateA;
    volatile bool requiresUpdateB;

    // Interrupt pins (Maybe no longer needed?)
    int interruptA;
    int interruptB;

    // Button -> track maps
    ButtonToTrack (&buttonToTrackA)[8]; // Map<buttonNumber, track+number>
    ButtonToTrack (&buttonToTrackB)[8]; // Map<buttonNumber, track+number>
};

struct GridAndSide {
  ButtonGrid* grid;
  int index;
};

#endif