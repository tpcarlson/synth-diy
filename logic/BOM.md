# Logic - BOM

This is the bill of materials for the Logic module. I have broken it up into SMT and Through-hole parts, as you'll probably want to solder all of the SMT parts first or have them pre-soldered.

For full kits and assembled boards the SMT parts will already be soldered, and you can just use the list of through-hole parts.

##### SMT Parts

| Type           | Value         | Quantity |
| -------------- | ------------- | -------- |
| MLCC Capacitor | 100nF         | 4        |
| Diode          | 1N4148        | 8        |
| Transistor     | MMBT3904      | 4        |
| Resistor       | 1k            | 16       |
| Resistor       | 2.7k          | 13       |
| Resistor       | 10k           | 1        |
| Resistor       | 100k          | 9        |
| Opamp          | TL074 SOIC-14 | 2        |

##### Through-hole Parts

| Type                                | Value                          | Quantity |
| ----------------------------------- | ------------------------------ | -------- |
| Low profile, electrolytic capacitor | 10uF                           | 2        |
| LED                                 | 3mm, green                     | 18       |
| Schottky Diode                      | 1N5817                         | 2        |
| Mono Audio Jack (Thonkiconn)        | PJ398SM                        | 12       |
| Shrouded IDC Header                 | 2x5                            | 1        |
| Male Pin Header                     | 2.54mm, 24+ pins               | 1        |
| Female Pin Socket                   | 2.54mm, 15+ pins (Or 2x 7 pin) | 1        |
| IC Socket                           | 2.54mm, 14 pins                | 1        |
| IC                                  | CD4xxx                         | 1        |

Depending on which logical operation you want to perform, you will need a different logic chip:

| Logical Operation | IC   |
| ----------------- | ---- |
| NOR               | 4001 |
| NAND              | 4011 |
| XOR               | 4070 |
| OR                | 4071 |
| XNOR              | 4077 |
| AND               | 4081 |