# ULX4M-LD Raspberry Pi Header Mapping

- Board map: `ulx4m-ld-v2`
- Design constraint input: `boards/ulx4m-ld/constraints/fpga_ulx4m_ld.lpf`
- FPGA-site map source: LiteX-Boards litex_boards/platforms/radiona_ulx4m_ld_v2.py RPI4 J1 connector map

`Current LPF use` is derived by matching each header-connected FPGA
site against active `LOCATE COMP` statements in the input LPF.
Board notes are wiring/resource notes and do not depend on the LPF.

| Physical | Header signal | Common alias | FPGA site | Board note | Current LPF use |
| ---: | --- | --- | --- | --- | --- |
| 1 | 3V3 | - | - | - | - |
| 2 | 5V | - | - | - | - |
| 3 | GPIO2 | SDA1 | B18 | shared SD_DAT1 | - |
| 4 | 5V | - | - | - | - |
| 5 | GPIO3 | SCL1 | P17 | - | ddram_a[12] |
| 6 | GND | - | - | - | - |
| 7 | GPIO4 | - | B15 | shared SD_DAT0 | sd_miso |
| 8 | GPIO14 | TXD | P2 | shared SD_DAT3 | sd_csn |
| 9 | GND | - | - | - | - |
| 10 | GPIO15 | RXD | G1 | shared SD_CLK | sd_clk |
| 11 | GPIO17 | - | H3 | - | - |
| 12 | GPIO18 | - | N5 | - | - |
| 13 | GPIO27 | - | P1 | shared SD_CMD | sd_mosi |
| 14 | GND | - | - | - | - |
| 15 | GPIO22 | - | M3 | - | - |
| 16 | GPIO23 | - | N4 | - | uart_rx |
| 17 | 3V3 | - | - | - | - |
| 18 | GPIO24 | - | N3 | - | uart_tx |
| 19 | GPIO10 | MOSI | K4 | - | - |
| 20 | GND | - | - | - | - |
| 21 | GPIO9 | MISO | L5 | - | - |
| 22 | GPIO25 | - | P5 | - | - |
| 23 | GPIO11 | SCLK | N2 | - | - |
| 24 | GPIO8 | CE0 | P4 | - | - |
| 25 | GND | - | - | - | - |
| 26 | GPIO7 | CE1 | P3 | - | - |
| 27 | GPIO0 | ID_SD | H1 | - | - |
| 28 | GPIO1 | ID_SC | J3 | - | - |
| 29 | GPIO5 | - | N1 | - | - |
| 30 | GND | - | - | - | - |
| 31 | GPIO6 | - | D7 | - | - |
| 32 | GPIO12 | - | R11 | JTAG TDI | - |
| 33 | GPIO13 | - | T1 | - | - |
| 34 | GND | - | - | - | - |
| 35 | GPIO19 | - | U1 | - | - |
| 36 | GPIO16 | - | V4 | JTAG TDO | - |
| 37 | GPIO26 | - | V1 | ETH PHY ref clk | - |
| 38 | GPIO20 | - | T5 | JTAG TCK | - |
| 39 | GND | - | - | - | - |
| 40 | GPIO21 | - | U5 | JTAG TMS | - |

## Header orientation in the supplied carrier image

With the board viewed exactly as in `cm4-io-base-b-3_3.jpg`, the
40-pin header is vertical on the right side of the carrier. Pins 1/2
are at the top and pins 39/40 are at the bottom. Odd pins are the
left column of the header and even pins are the right column.
