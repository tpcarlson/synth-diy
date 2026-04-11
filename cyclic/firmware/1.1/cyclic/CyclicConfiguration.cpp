#include "CyclicConfiguration.h"
#include <Arduino_JSON.h>

struct CyclicTrackConfig validateChannelConfig(JSONVar channel) {
  CyclicTrackConfig config;
  if (JSON.typeof(channel["note"]) == "number") {
    int note = channel["note"];
    if (note < 0 || note > 127) {
      config.midiNote = 0;
    } else {
      config.midiNote = note;
    }
  } else {
    config.midiNote = 0;
  }

  if (JSON.typeof(channel["channel"]) == "number") {
    int channelNum = channel["channel"];
    if (channelNum < 1 || channelNum > 16) {
      config.midiChannel = 10;
    } else {
      config.midiChannel = channelNum;
    }
  } else {
    config.midiChannel = 10;
  }

  if (JSON.typeof(channel["velocity"]) == "number") {
    int velocity = channel["velocity"];
    if (velocity < 0 || velocity > 127) {
      config.velocity = 127;
    } else {
      config.velocity = velocity;
    }
  } else {
    config.velocity = 127;
  }

  if (JSON.typeof(channel["length"]) == "number") {
    int length = channel["length"];
    if (length < 0) {
      config.gateDurationMs = 100;
    } else {
      config.gateDurationMs = length;
    }
  } else {
    config.gateDurationMs = 100;
  }

  return config;
}

struct CyclicTrackConfig* getTrackConfigurations(String trackData) {
    JSONVar json = JSON.parse(trackData);
    JSONVar channels = json["channels"];
    int numChannels = channels.length();
    CyclicTrackConfig* configs = new CyclicTrackConfig[8];
    // Fill configs with default values, if the JSON is incomplete (Or worse, empty) there should
    // still be some configuration present.
    for (int i = 0; i < 8; i++) {
      configs[i] = defaultTrackConfigs[i];
    }

    for (int i = 0; i < numChannels; i++) {
      JSONVar channel = channels[i];
      if (JSON.typeof(channel["input"]) == "number") {
        int inputNumber = channel["input"];
        if (inputNumber < 1 || inputNumber > 8) {
          Serial.println("Input number must be 1-8");
          continue;
        }
      } else {
        Serial.println("Must specify an input number (1-8)");
        continue;
      }

      CyclicTrackConfig validatedConfig = validateChannelConfig(channel);
      int inputNumber = channel["input"];
      configs[inputNumber-1] = validatedConfig;

      Serial.print("Channel: ");
      Serial.print(inputNumber);
      Serial.print(", Midi Note: ");
      Serial.print(validatedConfig.midiNote);
      Serial.print(", Midi Channel: ");                                                                                                 
      Serial.print(validatedConfig.midiChannel);
      Serial.print(", Velocity: ");                                                                                                    
      Serial.print(validatedConfig.velocity);
      Serial.print(", Gate Duration: ");
      Serial.print(validatedConfig.gateDurationMs);
      if (JSON.typeof(channel["description"]) == "string") {
        Serial.print("(");
        Serial.print(channel["description"]);
        Serial.print(")");
      }
    }
    return configs;
}