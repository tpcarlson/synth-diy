#include <MIDI.h>

// MIDI setup
MIDI_CREATE_INSTANCE(HardwareSerial, Serial1, MIDI);
const int MIDI_CHANNEL = 10;

// Constants
const int KICK = 36;
const int KICK_C = 48;
const int SNARE1 = 37;
const int SNARE1_C = 49;
const int SNARE2 = 38;
const int SNARE2_C = 50;
const int TOMH = 39;
const int TOMH_C = 51;
const int TOML = 40;
const int TOML_C = 52;
const int CYMB = 41;
const int CYMB_C = 53;
const int COWBELL = 42;
const int HATC = 43;
const int HATC_C = 55;
const int HATO = 44;
const int HATO_C = 56;
const int FMDRUM = 45;
const int FMDRUM_C = 57;

// Pin allocations:
const int IN_1_LEFT = 23;
const int IN_2_LEFT = 22;
const int IN_3_LEFT = 21;
const int IN_4_LEFT = 20;
const int IN_5_LEFT = 19;
const int IN_6_LEFT = 18;
const int IN_7_LEFT = 17;
const int IN_8_LEFT = 16;
const int IN_9_LEFT = 15;
const int IN_10_LEFT = 12;

const int IN_1_RIGHT = 2;
const int IN_2_RIGHT = 3;
const int IN_3_RIGHT = 4;
const int IN_4_RIGHT = 5;
const int IN_5_RIGHT = 6;
const int IN_6_RIGHT = 7;
const int IN_7_RIGHT = 8;
const int IN_8_RIGHT = 9;
const int IN_9_RIGHT = 10;
// No pin 10 right, that's the midi socket

const int MIDI_LED = 11;
unsigned long lastMidi;

struct Drum {
  int note;
  int pin;
  int value; // Previous value
};

struct Drum drums[19];

void setup(int drumNote, int drumPin, int index) {
  drums[index].note = drumNote;
  drums[index].pin = drumPin;
  pinMode(drumPin, INPUT);
}

void setup() {
  MIDI.begin();

  setup(KICK, IN_1_LEFT, 0);
  setup(KICK_C, IN_1_RIGHT, 1);

  setup(SNARE1, IN_2_LEFT, 2);
  setup(SNARE1_C, IN_2_RIGHT, 3);
  setup(SNARE2, IN_3_LEFT, 4);
  setup(SNARE2_C, IN_3_RIGHT, 5);

  setup(TOMH, IN_4_LEFT, 6);
  setup(TOMH_C, IN_4_RIGHT, 7);
  setup(TOML, IN_5_LEFT, 8);
  setup(TOML_C, IN_5_RIGHT, 9);

  setup(CYMB, IN_6_LEFT, 10);
  setup(CYMB, IN_6_RIGHT, 11);
  setup(HATC, IN_7_LEFT, 12);
  setup(HATC, IN_7_RIGHT, 13);
  setup(HATO, IN_8_LEFT, 14);
  setup(HATO, IN_8_RIGHT, 15);

  setup(FMDRUM, IN_9_LEFT, 16);
  setup(FMDRUM_C, IN_9_RIGHT, 17);

  setup(COWBELL, IN_10_LEFT, 18);

  pinMode(MIDI_LED, OUTPUT);
}

void sendMidi(Drum drum) {
  MIDI.sendNoteOn(drum.note, 64, MIDI_CHANNEL);
  lastMidi = millis();
}

void loop() {
  // Send midi notes for anything newly high
  for (int i = 0; i < 19; i++) {
    int value = digitalRead(drums[i].pin);
    if (drums[i].value == 0 && value == 1) {
      sendMidi(drums[i]);
    }

    drums[i].value = value;
  }

  // Update the MIDI LED. If there's no midi for 250ms
  // the LED just turns off.
  double currentTime = millis();
  if (lastMidi + 250 > currentTime) {
    digitalWrite(MIDI_LED, 1);
  } else {
    digitalWrite(MIDI_LED, 0);
  }
}
