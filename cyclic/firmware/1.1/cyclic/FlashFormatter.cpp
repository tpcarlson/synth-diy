#include "FlashFormatter.h"
// Since SdFat doesn't fully support FAT12 such as format a new flash
// We will use Elm Cham's fatfs f_mkfs() to format
#include "ff.h"
#include "diskio.h"

#define DISK_LABEL "CYCLIC"

void format_fat12() {
  uint8_t workbuf[4096];

  FATFS elmchamFatfs;

  FRESULT r = f_mkfs("", FM_FAT, 0, workbuf, sizeof(workbuf));
  if (r != FR_OK) {
    Serial.print(F("Error, f_mkfs failed with error code: "));
    Serial.println(r, DEC);
    while (1) yield();
  }

  r = f_mount(&elmchamFatfs, "0:", 1);
  if (r != FR_OK) {
    Serial.print(F("Error, f_mount failed with error code: "));
    Serial.println(r, DEC);
    while (1) yield();
  }

  Serial.println(F("Setting disk label to: " DISK_LABEL));
  r = f_setlabel(DISK_LABEL);
  if (r != FR_OK) {
    Serial.print(F("Error, f_setlabel failed with error code: "));
    Serial.println(r, DEC);
    while (1) yield();
  }

  f_unmount("0:");
  flash.syncBlocks();
  Serial.println(F("Formatted flash!"));
}

void check_fat12() {
  if (!fatfs.begin(&flash)) {
    Serial.println(F("Error, failed to mount newly formatted filesystem!"));
    while (1) delay(1);
  }
}

bool format_filesystem_if_needed() {
  if (!fatfs.begin(&flash)) {
    Serial.println(F("Creating and formatting FAT filesystem..."));

    format_fat12();
    check_fat12();

    Serial.println(F("Flash chip successfully formatted with new empty filesystem!"));
  }
  return true;
}