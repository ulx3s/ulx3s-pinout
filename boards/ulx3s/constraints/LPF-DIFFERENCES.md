# ULX3S LPF comparison for J1/J2 pinout generation

The `generate-data-from-lpf.py` script uses the LPF as the authoritative source
for the ECP5 package `SITE` assigned to `gp[0..27]` and `gn[0..27]`.

## Result

For the three LPFs checked here, all 56 GP/GN FPGA site mappings are identical:

- `doc/constraints/ulx3s_v20.lpf`
- `doc/constraints/prototype/ulx3s_v314.lpf`
- `doc/constraints/prototype/ulx3s_v316.lpf`

Therefore the rendered J1/J2 GP/GN signal-to-FPGA-site pinout is the same for
these revisions.

The generated `data_v20.py`, `data_v314.py`, and `data_v316.py` files differ in
source metadata, but their four J1/J2 pin-label lists are intentionally
identical.

## Relevant LPF differences

| LPF | Board scope | GPIO form | J1/J2-related notes |
| --- | --- | --- | --- |
| `ulx3s_v20.lpf` | ULX3S v2.x.x and v3.0.x | Vector `gp[n]`/`gn[n]` plus repeated scalar `gpN`/`gnN` aliases | Includes top/bottom header-orientation comments. `gn[12]` has `PULLMODE=NONE` and a 50 MHz `FREQUENCY` constraint. |
| `ulx3s_v314.lpf` | ULX3S v3.1.4 | Vector `gp[n]`/`gn[n]` only | GPIO comments explicitly identify J1/J2 pair positions such as `J1_5+` and `J2_35-`. `gn[12]` uses `PULLMODE=UP`. |
| `ulx3s_v316.lpf` | ULX3S v3.1.6 and v3.1.7 | Vector `gp[n]`/`gn[n]` plus repeated scalar aliases | Restores the top/bottom header-orientation comments. `gn[12]` uses `PULLMODE=UP`. |

The v20 comments around GP/GN11-13 also use older WiFi GPIO annotations, while
the v3.1.x files use newer ESP32 GPIO annotations. These comment differences
do not change the FPGA package sites used for J1/J2.

The complete LPF files contain many other board-revision-specific peripheral
differences. The pinout generator intentionally ignores unrelated signals and
only parses GP/GN `LOCATE COMP ... SITE ...` statements.

## What cannot be generated from an LPF

LPF files constrain FPGA signals to FPGA package sites. They do not define the
entire physical connector, so the following remain explicit structural data
inside the generator:

- J1/J2 physical pins 1 through 40
- power pins
- ground pins
- J2 5V IN and 5V OUT labels
- display orientation/order
- user labels such as `UART Rx` and `UART Tx`

This separation prevents the script from pretending that power or connector
mechanical information came from the FPGA constraint file.

## Usage

Generate the normal `data.py`:

```bash
./generate-data-from-lpf.py ulx3s \
    /path/to/ulx3s_v20.lpf \
    -o boards/ulx3s/data.py
```

For v3.1.4:

```bash
./generate-data-from-lpf.py ulx3s \
    /path/to/ulx3s_v314.lpf \
    -o boards/ulx3s/data.py
```

For v3.1.6/v3.1.7:

```bash
./generate-data-from-lpf.py ulx3s \
    /path/to/ulx3s_v316.lpf \
    -o boards/ulx3s/data.py
```

The generator accepts either vector names (`gp[0]`) or scalar aliases (`gp0`).
If both are present, they must resolve to the same FPGA site or generation
fails.

The generator also fails if any GP0..GP27 or GN0..GN27 mapping is missing.

To omit the example UART user labels:

```bash
./generate-data-from-lpf.py ulx3s \
    /path/to/ulx3s_v20.lpf \
    -o boards/ulx3s/data.py \
    --no-user-labels
```

User-defined labels are maintained in `USER_LABELS` near the top of the
generator rather than in the generated `data.py`.


## Optional alias and metadata generation

The generator can expose revision differences directly in the diagram without
changing the base GP/GN/site pinout.

For example:

```bash
./generate-data-from-lpf.py ulx3s ./boards/ulx3s/constraints/ulx3s_v20.lpf \
    -o data_v20_meta.py \
    --include aliases,connector,flags,pullmode,io_type,drive,frequency

./generate-data-from-lpf.py ulx3s ./boards/ulx3s/constraints/ulx3s_v314.lpf \
    -o data_v314_meta.py \
    --include aliases,connector,flags,pullmode,io_type,drive,frequency

./generate-data-from-lpf.py ulx3s boards/ulx3s/constraints/ulx3s_v316.lpf \
    -o data_v316_meta.py \
    --include aliases,connector,flags,pullmode,io_type,drive,frequency
```

This makes differences such as the v20 WiFi aliases versus the newer v3.1.x
aliases visible while leaving the canonical GP/GN and FPGA `SITE` labels
unchanged.

`ulx3s_v314.lpf` is especially useful for connector auditing because its GP/GN
comments contain explicit `J1_*` and `J2_*` connector-position tokens.

For v3.1.6/v3.1.7, use the default vector GPIO form for the primary metadata.
The generator warns that the duplicate scalar GN12 definition carries
different electrical metadata.
