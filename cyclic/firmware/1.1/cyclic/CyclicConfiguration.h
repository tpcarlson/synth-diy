#ifndef CYCLIC_CONFIG
#define CYCLIC_CONFIG

#include <Arduino.h>

struct CyclicTrackConfig {
  int velocity;
  int midiNote;
  int midiChannel;
  int gateDurationMs;
};

struct CyclicTrackConfig* getTrackConfigurations(String trackData);

// Provided by cyclic.ino
extern CyclicTrackConfig defaultTrackConfigs[8];

#endif