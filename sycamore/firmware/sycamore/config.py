import json
import os

class Config:
    """Configuration loading for Sycamore"""
    def __init__(self):
        self.validAuxModes = ["resetClock", "shuffle", "mutate", "transpose"]

    def load(self):
        # Load up values
        with open("settings.txt", "r") as infile:
            config = json.load(infile)
            self.expanders = config.get("expanders")
            self.expanderSettings = config.get("expanderSettings")
            self.auxMode = config.get("auxMode")
            if self.auxMode is None or self.auxMode not in self.validAuxModes:
                print("Aux mode not set, defaulting to mutate CV")
                self.auxMode = "mutate"
            self.dacLUT = config.get("dacLookupTable")
        self.scales = self.loadScales()

    def loadScales(self):
        toReturn = {}
        allScales = os.listdir("scales/")
        for file in allScales:
            try:
                with open("scales/" + file, "r") as scale:
                    scale = json.load(scale)
                    targetScaleFull = []
                    for i in scale.get("notes"):
                        for j in range(5):
                            if j == 0:
                                targetScaleFull.append(i)
                            else:
                                targetScaleFull.append(i + (j*12))

                    toReturn[scale.get("index")] = targetScaleFull
            except ValueError as error:
                print(error)
                print("Invalid JSON syntax. Check the scale configuration for " + file)
            except AttributeError as error:
                print(error)
                print("Invalid JSON syntax. Check the scale configuration for " + file)
        print("Loaded " + str(len(toReturn)) + " scales")
        return toReturn

    def getExpanders(self):
        return self.expanders

    def getAuxMode(self):
        return self.auxMode

    def getDacLUT(self):
        return self.dacLUT

    def getScales(self):
        return self.scales

    def getExpanderSettings(self):
        return self.expanderSettings
