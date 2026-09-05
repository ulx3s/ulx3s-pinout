# ULX3S J1/J2 Pin Mapping

- Board scope: `v3.1.6 and v3.1.7`
- Design constraint input: `boards/ulx3s/constraints/ulx3s_v316.lpf`
- GPIO form: `vector`

FPGA sites and LPF metadata come from the selected constraint file.
Power, ground, and physical J1/J2 connector structure are maintained
by the ULX3S board generator because they are not FPGA LOCATE entries.

| Header | Physical | Signal | FPGA site | Connector pair | LPF aliases | IOBUF | Frequency |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| J1 | 1 | 2.5/3.3V | - | - | - | - | - |
| J1 | 2 | 2.5/3.3V | - | - | - | - | - |
| J1 | 3 | GND | - | - | - | - | - |
| J1 | 4 | GND | - | - | - | - | - |
| J1 | 5 | GN0 | C11 | J1_5- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 6 | GP0 | B11 | J1_5+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 7 | GN1 | A11 | J1_7- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 8 | GP1 | A10 | J1_7+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 9 | GN2 | B10 | J1_9- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 10 | GP2 | A9 | J1_9+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 11 | GN3 | C10 | J1_11- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 12 | GP3 | B9 | J1_11+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 13 | GN4 | A8 | J1_13- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 14 | GP4 | A7 | J1_13+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 15 | GN5 | B8 | J1_15- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 16 | GP5 | C8 | J1_15+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 17 | GN6 | C7 | J1_17- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 18 | GP6 | C6 | J1_17+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 19 | 2.5/3.3V | - | - | - | - | - |
| J1 | 20 | 2.5/3.3V | - | - | - | - | - |
| J1 | 21 | GND | - | - | - | - | - |
| J1 | 22 | GND | - | - | - | - | - |
| J1 | 23 | GN7 | B6 | J1_23- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 24 | GP7 | A6 | J1_23+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 25 | GN8 | A5 | J1_25- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 26 | GP8 | A4 | J1_25+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 27 | GN9 | B1 | J1_27- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 28 | GP9 | A2 | J1_27+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 29 | GN10 | B4 | J1_29- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 30 | GP10 | C4 | J1_29+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 31 | GN11 | E3 | J1_31- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 32 | GP11 | F4 | J1_31+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 33 | GN12 | F3 | J1_33- | wifi_gpio32 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 34 | GP12 | G3 | J1_33+ | wifi_gpio33 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 35 | GN13 | G5 | J1_35- | wifi_gpio39, sensor_vn | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 36 | GP13 | H4 | J1_35+ | wifi_gpio36, sensor_vp | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J1 | 37 | GND | - | - | - | - | - |
| J1 | 38 | GND | - | - | - | - | - |
| J1 | 39 | 2.5/3.3V | - | - | - | - | - |
| J1 | 40 | 2.5/3.3V | - | - | - | - | - |
| J2 | 1 | 3.3V | - | - | - | - | - |
| J2 | 2 | 3.3V | - | - | - | - | - |
| J2 | 3 | GND | - | - | - | - | - |
| J2 | 4 | GND | - | - | - | - | - |
| J2 | 5 | GN14 | U17 | J2_5- | ADC AIN0 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 6 | GP14 | U18 | J2_5+ | ADC AIN1 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 7 | GN15 | P16 | J2_7- | ADC AIN2 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 8 | GP15 | N17 | J2_7+ | ADC AIN3 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 9 | GN16 | M17 | J2_9- | ADC AIN4 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 10 | GP16 | N16 | J2_9+ | ADC AIN5 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 11 | GN17 | L17 | J2_11- | ADC AIN6 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 12 | GP17 | L16 | J2_11+ | ADC AIN7 | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 13 | GN18 | H17 | J2_13- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 14 | GP18 | H18 | J2_13+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 15 | GN19 | G18 | J2_15- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 16 | GP19 | F17 | J2_15+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 17 | GN20 | E17 | J2_17- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 18 | GP20 | D18 | J2_17+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 19 | 3.3V | - | - | - | - | - |
| J2 | 20 | 3.3V | - | - | - | - | - |
| J2 | 21 | GND | - | - | - | - | - |
| J2 | 22 | GND | - | - | - | - | - |
| J2 | 23 | GN21 | D17 | J2_23- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 24 | GP21 | C18 | J2_23+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 25 | GN22 | C15 | J2_25- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 26 | GP22 | B15 | J2_25+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 27 | GN23 | C17 | J2_27- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 28 | GP23 | B17 | J2_27+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 29 | GN24 | D16 | J2_29- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 30 | GP24 | C16 | J2_29+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 31 | GN25 | E14 | J2_31- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 32 | GP25 | D14 | J2_31+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 33 | GN26 | C13 | J2_33- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 34 | GP26 | B13 | J2_33+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 35 | GN27 | E13 | J2_35- | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 36 | GP27 | D13 | J2_35+ | - | PULLMODE=UP, IO_TYPE=LVCMOS33, DRIVE=4 | - |
| J2 | 37 | GND | - | - | - | - | - |
| J2 | 38 | GND | - | - | - | - | - |
| J2 | 39 | 5V IN | - | - | - | - | - |
| J2 | 40 | 5V OUT | - | - | - | - | - |

Physical pin numbering is for the female 90-degree angled header.
Confirm orientation before wiring a male vertical header viewed from
the opposite side.
