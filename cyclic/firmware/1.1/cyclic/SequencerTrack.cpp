#include "SequencerTrack.h"

#define ACTIVE_SEQUENCE_STEP pixels->Color(100,0,0)
#define CLOCKED_ACTIVE_SEQUENCE_STEP pixels->Color(0,100,0)
#define OFF_SEQUENCE_STEP pixels->Color(0,0,100)
#define CLOCKED_OFF_SEQUENCE_STEP pixels->Color(100,100,100)

const unsigned long gateLengthMillis = 100;

SequencerTrack::SequencerTrack(Adafruit_NeoPixel* pixels, int (&stepToPixel)[16], int gateOutput)
   : pixels(pixels), currentStep(0), stepToPixel(stepToPixel), gateOutput(gateOutput) {
}

void SequencerTrack::clockSequencer() {
  pixels->setPixelColor(stepToPixel[currentStep], stepActive[currentStep] ? ACTIVE_SEQUENCE_STEP : OFF_SEQUENCE_STEP);
  currentStep = (currentStep+1) % 16;
  pixels->setPixelColor(stepToPixel[currentStep], stepActive[currentStep] ? CLOCKED_ACTIVE_SEQUENCE_STEP : CLOCKED_OFF_SEQUENCE_STEP);
  loopUpdate = true;

  // Gate outputs are tied to a duration in configuration (Default 100ms).
  // This is because the clock inputs to the sequencer are clock -> advance
  // sequence, so we can't do duty cycle. If Cyclic clocked itself, then it
  // would be possible to add duty cycles in. An alternative could be to
  // guess the BPM to derive a duration, but with the kind of uneven clocks that
  // I want to use with Cyclic, this won't work very well.
  if (stepActive[currentStep]) {
    noteOn(0x90 | config->midiChannel-1, config->midiNote, config->velocity);
    digitalWrite(gateOutput, HIGH);
    lastGate = millis();
    gateOutputting = true;
  } else {
    noteOn(0x80 | config->midiChannel-1, config->midiNote, 0);
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

  if (gateOutputting && (millis() - config->gateDurationMs) > lastGate) {
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

void SequencerTrack::updateConfig(CyclicTrackConfig* newConfig) {
  config = newConfig;
}