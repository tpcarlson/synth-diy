#include "SequencerTrack.h"

#define ACTIVE_SEQUENCE_STEP pixels->Color(100,0,0)
#define CLOCKED_ACTIVE_SEQUENCE_STEP pixels->Color(0,100,0)
#define OFF_SEQUENCE_STEP pixels->Color(0,0,100)
#define CLOCKED_OFF_SEQUENCE_STEP pixels->Color(100,100,100)

const unsigned long gateLengthMillis = 100;

SequencerTrack::SequencerTrack(Adafruit_NeoPixel* pixels, int (&stepToPixel)[16], int midiChannel, int midiNote, int gateOutput)
   : pixels(pixels), currentStep(0), stepToPixel(stepToPixel), midiChannel(midiChannel-1), gateOutput(gateOutput), midiNote(midiNote) {
}

void SequencerTrack::clockSequencer() {
  pixels->setPixelColor(stepToPixel[currentStep], stepActive[currentStep] ? ACTIVE_SEQUENCE_STEP : OFF_SEQUENCE_STEP);
  currentStep = (currentStep+1) % 16;
  pixels->setPixelColor(stepToPixel[currentStep], stepActive[currentStep] ? CLOCKED_ACTIVE_SEQUENCE_STEP : CLOCKED_OFF_SEQUENCE_STEP);
  loopUpdate = true;

  // TODO: Gate outputs are currently 100% duty (ie. active for the whole step)
  // Adjacent steps will just be tied. Once there is support for firmware, some
  // kind of gate length might be worth adding, with the caveat that as all the
  // sequencer tracks are clocked externally this'll be of the form "delay x ms"
  // rather than the form "50% duty cycle".
  if (stepActive[currentStep]) {
    noteOn(0x90 | midiChannel, midiNote, 0x45);
    digitalWrite(gateOutput, HIGH);
    lastGate = millis();
    gateOutputting = true;
  } else {
    noteOn(0x80 | midiChannel, midiNote, 0);
    digitalWrite(gateOutput, LOW);
    gateOutputting = false;
  }
}

void SequencerTrack::setActive(int step, bool active) {
  stepActive[step] = active;
  loopUpdate = true;
}

void SequencerTrack::toggleActive(int step) {
  stepActive[step] = !stepActive[step];
  pixels->setPixelColor(stepToPixel[step], stepActive[step] ? ACTIVE_SEQUENCE_STEP : OFF_SEQUENCE_STEP);
  loopUpdate = true;
}

void SequencerTrack::loop() {
  if (loopUpdate) {
    pixels->show();
    loopUpdate = false;
  }

  if (gateOutputting && (millis() - gateLengthMillis) > lastGate) {
    digitalWrite(gateOutput, LOW);
    gateOutputting = false;
  }
}

bool SequencerTrack::needsLedUpdate() {
  loopUpdate = !loopUpdate;
  return !loopUpdate;
}

void SequencerTrack::resetNeedsLedUpdate() {
  loopUpdate = false;
}

// TODO: Maybe make or use a MIDI library?
void SequencerTrack::noteOn(int cmd, int pitch, int velocity) {
  Serial1.write(cmd);
  Serial1.write(pitch);
  Serial1.write(velocity);
}