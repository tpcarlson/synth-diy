#ifndef SEQTRACK
#define SEQTRACK

#include <Adafruit_NeoPixel.h>

class SequencerTrack {
  public:
    SequencerTrack(Adafruit_NeoPixel* pixels, int (&stepToPixel)[16], int midiChannel, int midiNote, int gateOutput);

    // Clock the sequencer. This will be triggered from an external source,
    // either the MIDI in or the clock input for a given sequencer track.
    // Clocking will also set the previous step low and new current step high.
    // Clock outputs are set asynchronously low within the loop() function.
    // LED changes also happen asynchronously within loop.
    void clockSequencer();

    // Set the state of a single step in the sequence. This will be triggered
    // by an external source, either the MIDI in or the the button pads
    // LED changes happen asynchronously within loop.
    void setActive(int step, bool active);

    // Similar to setActive, but for a caller that does not know the state of
    // the current sequencer track.
    void toggleActive(int step);

    // Perform any loop actions. This should be limited to non-critical tasks
    // such as performing LED operations and (possibly?) unsetting trigger outputs
    void loop();

    // Whether this sequencer track is requesting an LED update. While sequencer
    // tracks may setPixel on any pixel, they should leave updating the array
    // to the main loop.
    bool needsLedUpdate();
    void resetNeedsLedUpdate();
  private:
    // For readability. Could pack this into an int16_t if needed.
    bool stepActive[16] = {false};
    int (&stepToPixel)[16]; // Map<step, pixel number>
    int currentStep;
    bool loopUpdate = false;
    Adafruit_NeoPixel* pixels;
    int midiChannel;
    int midiNote;
    int gateOutput;
    unsigned long lastGate = 0;
    bool gateOutputting = false;
    void noteOn(int cmd, int pitch, int velocity);
};

#endif