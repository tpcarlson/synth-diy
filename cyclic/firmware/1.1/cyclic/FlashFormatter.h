#ifndef FLASH_FORMATTER_H
#define FLASH_FORMATTER_H                                                                                                    
#include <Arduino.h>
#include "SdFat_Adafruit_Fork.h"
#include "Adafruit_SPIFlash.h"

#define DISK_LABEL "CYCLIC"

extern FatVolume fatfs;
extern Adafruit_SPIFlash flash;

void format_fat12();
void check_fat12();
bool format_filesystem_if_needed();

#endif