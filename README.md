# apcOSC2MIDI
Mapper to use the full potential of AKAI APC mini mk2 with QLC+, it uses the OSC protocol for QLC+ comunication.

## QLC Configuration
Set OSC protocol as input and feedback, and listen at 127.0.0.1 at port 7700
## Peripheral buttons
The peripheral, supports 3 states:
- 0 -> OFF
- from 1 to 254 -> Blink
- 255 -> On

## RGB Pad Table
Here follows a color table of usable color for reference, each color has two value, one for static and one for the blink state

[PDF](docs/APC%20mini%20mk2%20color%20table.pdf)