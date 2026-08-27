# ULX3S Pinout

Generated pinout diagram for the ULX3S FPGA development board.

The diagram overlays connector labels on a ULX3S board image. The current
pinout data covers all 40 physical pins on both GPIO headers:

- J1: GP/GN 0 through 13, power, and ground
- J2: GP/GN 14 through 27, power, ground, 5V input, and 5V output

GPIO labels include the physical connector pin number, ULX3S GP/GN signal
name, and ECP5 FPGA package site.

> WARNING: This project is under development. Always verify connector power,
> FPGA site, and board-revision-specific details against the ULX3S schematic,
> manual, and constraint file before connecting external hardware.

![ULX3S pinout](./pinout_ulx3s.svg)

## Quick Start

Once installed and configured (see below) - refresh:

### Generate Data

```bash
python3 generate-data-from-lpf.py  ./constraints/ulx3s_v316.lpf  -o data.py  --include aliases
```

### Generate SVG Image

```bash
python3 -m pinout.manager  --export pinout_ulx3s.py pinout_ulx3s.svg  --overwrite
```

## Header numbering convention

The physical J1 and J2 pin numbers shown by this project follow the ULX3S
constraint-file convention for female angled 90-degree headers mounted on the
top of the board.

The ULX3S constraint file describes the GPIO connectors as:

- female angled 90-degree headers on the top, or
- male vertical headers on the bottom / flat cable

If using a male vertical header, confirm the physical orientation before
wiring. Do not assume that the apparent left/right or odd/even positions are
the same when viewed from the opposite side of the PCB.

## Requirements

The main diagram generator is Python based and uses the
[pinout](https://pinout.readthedocs.io/) package.

For Ubuntu or WSL:

```bash
sudo apt update
sudo apt install python3-pip inotify-tools

python3 -m pip install --user --upgrade pinout cairosvg
```

`inotify-tools` is only required for the automatic file-watching development
script. It is not required for one-shot SVG generation.

The current generator uses the local `ulx3s.png` board image and embeds it in
the generated SVG. Network access is therefore not required to render the
board image after the repository has been cloned.

## Clone the repository

```bash
cd /mnt/c/workspace
git clone https://github.com/ulx3s/ulx3s-pinout.git
cd ulx3s-pinout
```

Run all generation commands from the repository root. Several source files are
referenced by relative path.

## Generate the SVG

For a normal one-shot build:

```bash
python3 -m pinout.manager \
    --export pinout_ulx3s.py pinout_ulx3s.svg \
    --overwrite
```

A successful build creates or replaces:

```text
pinout_ulx3s.svg
```

Check that it exists:

```bash
ls -lh pinout_ulx3s.svg
```

The SVG can be opened directly in a modern web browser.

The `.py` suffix in `pinout_ulx3s.py` is required. Passing only
`pinout_ulx3s` can cause Python module loading to fail with an error similar to:

```text
AttributeError: 'NoneType' object has no attribute 'loader'
```

## Automatic regeneration while editing

`pinout-update.sh` is a development convenience that waits for source changes
and regenerates `pinout_ulx3s.svg`.

Make it executable once if necessary:

```bash
chmod +x pinout-update.sh
```

Then run:

```bash
./pinout-update.sh
```

You can also run it without relying on the executable bit:

```bash
bash ./pinout-update.sh
```

The script requires `inotifywait`, provided by the Ubuntu/WSL
`inotify-tools` package.

If it is not installed:

```bash
sudo apt install inotify-tools
```

The watcher currently monitors:

```text
styles.css
pinout_ulx3s.py
data.py
```

If `ulx3s.png` is changed, run the one-shot generation command manually unless
the watcher is also updated to monitor that file.

Stop the watcher with `Ctrl-C`.

## Editing the pinout

Most pinout changes only require editing one of three files.

### Change a pin name, connector pin, or FPGA site

Edit:

```text
data.py
```

This is the pinout data source. J1 and J2 entries contain the physical header
pin number, GP/GN signal name, FPGA site, power label, or ground label.

After editing, regenerate the SVG.

### Change where labels or leader lines are placed

Edit:

```text
pinout_ulx3s.py
```

This file defines the diagram dimensions, board-image placement, J1/J2 label
group locations, label width/height, spacing, direction, and other rendering
geometry.

### Change pin-label pill appearance

The pill corner radius and border are parameterized in `pinout_ulx3s.py`:

```python
PIN_LABEL_CORNER_RADIUS = 5
PIN_LABEL_BORDER_COLOR = "rgb(54, 54, 54)"
PIN_LABEL_BORDER_WIDTH = 1.5
```

`PIN_LABEL_CORNER_RADIUS` controls the SVG rounded-rectangle corner radius in
pixels. Increase it for rounder pills or decrease it for squarer labels. The
configured label height is 20 pixels, so values around 4 through 7 provide
moderate rounding without turning short labels into fully rounded capsules.

`PIN_LABEL_BORDER_COLOR` accepts any SVG/CSS color value, for example:

```python
PIN_LABEL_BORDER_COLOR = "#363636"
PIN_LABEL_BORDER_COLOR = "rgb(54, 54, 54)"
```

`PIN_LABEL_BORDER_WIDTH` is the border stroke thickness in SVG pixels:

```python
PIN_LABEL_BORDER_WIDTH = 1.5
```

The renderer injects these Python values as an inline SVG style after
`styles.css`. This keeps the border parameters in the same source file as the
label geometry and ensures they override any generic `.pinlabel__body` border
setting in the stylesheet.

Every generated J1/J2 label also receives:

```python
body.setdefault("corner_radius", PIN_LABEL_CORNER_RADIUS)
```

so the same corner-radius setting applies consistently to physical pin
numbers, GP/GN names, FPGA sites, user labels, aliases, connector labels, and
LPF metadata labels.

### Change pin-label box widths

J1/J2 label boxes are sized by semantic type in `pinout_ulx3s.py`. This keeps
short labels compact while reserving more room for aliases and metadata.

The current width parameters are:

```python
PIN_NUMBER_LABEL_WIDTH = 40
GPIO_SIGNAL_LABEL_WIDTH = 58
FPGA_SITE_LABEL_WIDTH = 54
POWER_LABEL_WIDTH = 88
GROUND_LABEL_WIDTH = 54
USER_LABEL_WIDTH = 96
ALIAS_LABEL_WIDTH = 116
CONNECTOR_LABEL_WIDTH = 76
METADATA_LABEL_WIDTH = 132
ANALOG_LABEL_WIDTH = 76
PWM_LABEL_WIDTH = 72
TOUCH_LABEL_WIDTH = 76
DEFAULT_LABEL_WIDTH = 96
```

All J1/J2 boxes share:

```python
PIN_LABEL_HEIGHT = 20
```

The renderer chooses widths automatically. Physical connector pin numbers are
recognized by numeric content first, so pins such as `2`, `19`, and `40` use
`PIN_NUMBER_LABEL_WIDTH` even though their functional tag may be `pwr`, `gnd`,
or `gpio`.

Non-numeric labels use their CSS/data tag:

```python
LABEL_WIDTH_BY_TAG = {
    "gpsingle": GPIO_SIGNAL_LABEL_WIDTH,
    "gnsingle": GPIO_SIGNAL_LABEL_WIDTH,
    "gpdiff": GPIO_SIGNAL_LABEL_WIDTH,
    "gndiff": GPIO_SIGNAL_LABEL_WIDTH,
    "site": FPGA_SITE_LABEL_WIDTH,
    "pwr": POWER_LABEL_WIDTH,
    "gnd": GROUND_LABEL_WIDTH,
    "comms": USER_LABEL_WIDTH,
    "alias": ALIAS_LABEL_WIDTH,
    "connector": CONNECTOR_LABEL_WIDTH,
    "meta": METADATA_LABEL_WIDTH,
    ...
}
```

Examples:

```text
"28"          -> PIN_NUMBER_LABEL_WIDTH
"GP23"        -> GPIO_SIGNAL_LABEL_WIDTH
"B17"         -> FPGA_SITE_LABEL_WIDTH
"2.5/3.3V"    -> POWER_LABEL_WIDTH
"UART Rx"     -> USER_LABEL_WIDTH
"wifi_gpio36" -> ALIAS_LABEL_WIDTH
"J2_27+"      -> CONNECTOR_LABEL_WIDTH
"PULL=UP"     -> METADATA_LABEL_WIDTH
```

The width policy is a rendering concern, so generated `data.py` remains simple
and does not contain layout widths. `labels_with_dimensions()` adds the
per-label body settings when `pinout_ulx3s.py` builds each `PinLabelGroup`.

If a new label tag is added, either add it to `LABEL_WIDTH_BY_TAG` or let it
use `DEFAULT_LABEL_WIDTH`.

Wider labels increase the total horizontal extent of rows containing several
labels. If those rows approach or cross the outer frame, increase
`EXTRA_LABEL_SPACE_PER_SIDE` as well.

### Increase space for additional user labels

The black outer frame is created by the top-level `Panel` in
`pinout_ulx3s.py`. The related frame and centering dimensions are derived from
layout variables near the top of that file rather than being repeated as
hard-coded values.

For normal editing, the main setting is:

```python
EXTRA_LABEL_SPACE_PER_SIDE = 100
```

This value is the additional horizontal space, in SVG pixels, reserved on
each side of the original layout. The diagram width, content-panel width,
board position, and legend position are derived automatically:

```python
DIAGRAM_WIDTH = BASE_DIAGRAM_WIDTH + (2 * EXTRA_LABEL_SPACE_PER_SIDE)
CONTENT_WIDTH = BASE_CONTENT_WIDTH + (2 * EXTRA_LABEL_SPACE_PER_SIDE)
GRAPHIC_X = BASE_GRAPHIC_X + EXTRA_LABEL_SPACE_PER_SIDE + BOARD_X_ADJUST
LEGEND_X = BASE_LEGEND_X + EXTRA_LABEL_SPACE_PER_SIDE
```

For example, if user labels need 50 more pixels on both sides, change only:

```python
EXTRA_LABEL_SPACE_PER_SIDE = 150
```

The output becomes 100 pixels wider in total and the ULX3S remains centered.

User labels are additional entries in a pin's list in `data.py`. For example,
GP0 currently includes an extra UART label:

```python
[
    ("6", "gpio"),
    ("GP0", "gpsingle"),
    ("UART Rx", "comms"),
    ("B11", "site"),
],
```

Each additional entry extends farther outward from the connector. Increase
`EXTRA_LABEL_SPACE_PER_SIDE` when several labels are added on both J1 and J2.

For an asymmetric layout, use:

```python
BOARD_X_ADJUST = 0
```

A positive value shifts the ULX3S and all pin labels to the right. A negative
value shifts them to the left. This is useful when one side has substantially
more or longer user labels than the other.

The base values are also grouped near the top of `pinout_ulx3s.py`:

```python
BASE_DIAGRAM_WIDTH = 1600
BASE_CONTENT_WIDTH = 1560
BASE_GRAPHIC_X = 95
BASE_LEGEND_X = 280
```

These normally do not need to change. They describe the original layout;
`EXTRA_LABEL_SPACE_PER_SIDE` provides the normal user-editable margin.

### Change colors, fonts, or visual styling

Edit:

```text
styles.css
```

Pin categories such as GP, GN, differential pairs, FPGA sites, power, ground,
and GPIO get their visual appearance from this stylesheet.

## Pin data organization

`data.py` separates the two physical rows of each 2x20 connector so that each
header pin can be connected to its own label group.

The main connector data sets are:

```text
left_header_even     J1 even-numbered physical pins
left_header_odd      J1 odd-numbered physical pins
right_header_even    J2 even-numbered physical pins
right_header_odd     J2 odd-numbered physical pins
```

Together, the J1 lists must contain physical pins 1 through 40 exactly once.
The J2 lists must also contain physical pins 1 through 40 exactly once.

The GPIO signal range is:

```text
J1: GP0..GP13 and GN0..GN13
J2: GP14..GP27 and GN14..GN27
```

When changing this data, verify the FPGA package sites against
`ulx3s_v20.lpf` rather than inferring a site from neighboring pins.

## File and directory purpose

### Main generator files

| Path | Purpose |
| --- | --- |
| `README.md` | Project usage, generation, maintenance, and file-layout documentation. |
| `data.py` | Pin-label data, legend entries, J1/J2 physical pin numbers, GP/GN names, power/ground labels, and FPGA package sites. This is the primary file to edit when changing pin assignments or label content. |
| `pinout_ulx3s.py` | Main Python diagram definition. Loads `data.py`, embeds `ulx3s.png`, creates J1/J2 label groups, and defines their geometry. |
| `styles.css` | SVG/CSS styling for label bodies, leader lines, text, legend entries, power, ground, GP/GN, differential pairs, and FPGA sites. |
| `ulx3s.png` | Source board image used as the background of the generated pinout diagram. It is embedded into the SVG by `pinout_ulx3s.py`. |
| `pinout_ulx3s.svg` | Primary generated output. This file is regenerated from the Python/data/CSS sources. Do not treat manual SVG edits as source changes. |
| `pinout_ulx3s.png` | Rasterized pinout image/preview when a PNG form of the generated SVG is desired. |
| `pinout-update.sh` | Linux/WSL development watcher. Uses `inotifywait` and regenerates `pinout_ulx3s.svg` when selected source files change. |
| `generate-data-from-lpf.py` | Generates `data.py` from ULX3S LPF `gp`/`gn` FPGA site constraints, validates all 56 GPIO mappings, and preserves the connector/power/user-label structure maintained by the pinout project. |
| `custom_components.py` | Legacy custom `PNG_from_web` component that downloaded and embedded an image from a URL. The current main generator uses `pinout.core.Image` with the local `ulx3s.png`, so this file is not required by the normal generation path. |
| `.gitignore` | Git ignore rules for generated, temporary, or development-specific files. |
| `ulx3s-pinout.sln` | Visual Studio solution for the C# helper utilities included in this repository. It is not required for the Python SVG-generation path. |

### Helper utility directories

The helper utilities are separate from the normal Python generation workflow.

| Path | Purpose |
| --- | --- |
| `fpga2pinout/` | C# helper that reads an FPGA constraint file and extracts `LOCATE COMP ... SITE ...` mappings into an intermediate text form useful when preparing pin data. |
| `svg2png/` | C# helper that uses SVG.NET to render an SVG file to a PNG file. |
| `png2base64/` | Legacy C# Base64 helper. Its current implementation reads the input as text and writes a `.Base64` file. It is not needed by the current embedded-image workflow. |

Each C# helper directory contains its own `Program.cs` and Visual Studio/MSBuild
project file. These tools are optional and are not needed to build
`pinout_ulx3s.svg`.

## Generated versus source files

The normal source-to-output relationship is:

```text
data.py -----------+
styles.css --------+--> pinout_ulx3s.py --> pinout_ulx3s.svg
ulx3s.png ----------+
```

Edit the source files and regenerate the SVG rather than making permanent
changes directly to `pinout_ulx3s.svg`.

Because the board PNG is embedded, the resulting SVG is self-contained for
normal viewing.

## Generate `data.py` from an ULX3S LPF

`generate-data-from-lpf.py` makes the FPGA site labels reproducible from an
authoritative ULX3S constraint file instead of maintaining those package sites
by hand.

Base pinout only:

```bash
python3 generate-data-from-lpf.py \\
    /path/to/ulx3s_v20.lpf \\
    -o data.py
```

The base output contains the existing physical pin number, GP/GN name, optional
project `USER_LABELS`, and FPGA package site. LPF aliases and metadata are
opt-in so the normal diagram does not become excessively wide.

### Optional LPF labels

Use `--include` with one or more comma-separated fields:

```text
aliases
connector
flags
iobuf
pullmode
io_type
drive
frequency
comment
all
```

Examples:

```bash
# Revision-specific aliases only.
python3 generate-data-from-lpf.py \\
    ulx3s_v316.lpf \\
    -o data.py \\
    --include aliases
```

```bash
# Useful electrical metadata without the raw LPF comment.
python3 generate-data-from-lpf.py \\
    ulx3s_v316.lpf \\
    -o data.py \\
    --include aliases,connector,flags,pullmode,io_type,drive,frequency
```

```bash
# Every parsed IOBUF key/value, including future keys not known today.
python3 generate-data-from-lpf.py \\
    ulx3s_v316.lpf \\
    -o data.py \\
    --include iobuf
```

A specific arbitrary IOBUF key can also be requested:

```bash
python3 generate-data-from-lpf.py \\
    board.lpf \\
    -o data.py \\
    --iobuf-key SLEWRATE
```

`--include aliases` combines two sources:

1. recognized aliases in the GP/GN inline comment, including `wifi_gpioN`,
   `sensor_*`, and `ADC AINn`; and
2. other active `LOCATE COMP` signal names that use the same FPGA site.

Duplicate aliases are emitted only once.

`--include connector` emits labels such as `J1_5+`, `J1_5-`, `J2_35+`, and
`J2_35-`. When an LPF provides an explicit connector token in the GP/GN
comment, the generator verifies it against the physical connector template.

`--include flags` extracts the useful GP/GN comment flags `DIFF`, `PCLK`, and
`GR_PCLK`.

`--include iobuf` emits every parsed IOBUF `KEY=VALUE` pair. The narrower
`pullmode`, `io_type`, and `drive` fields can be selected individually.

`--include frequency` emits `FREQUENCY PORT` metadata when present.

`--include comment` emits the complete GP/GN inline comment. This can produce
very wide labels and is mainly useful for auditing or development.

`--include all` enables every field above, including the raw comment.

The added label classes are `alias`, `connector`, and `meta`; `styles.css`
contains their default colors.

### Vector and scalar GPIO definitions

Some ULX3S LPFs contain both:

```text
gp[0]..gp[27] / gn[0]..gn[27]
```

and:

```text
gp0..gp27 / gn0..gn27
```

The generator always verifies that the two forms use the same FPGA `SITE`.

For aliases and electrical metadata, the forms are not blindly merged.
`--gpio-form auto` is the default and prefers the complete vector form.
Choose a form explicitly when needed:

```bash
--gpio-form vector
--gpio-form scalar
```

This matters for files such as `ulx3s_v316.lpf`, where the vector and scalar
definitions of GN12 have different IOBUF/FREQUENCY metadata. The generator
prints a warning for such differences. Use `--strict-form-metadata` if those
differences should be fatal.

### User labels

The example UART labels remain independent of LPF metadata:

```python
USER_LABELS = {
    "GP0": [("UART Rx", "comms")],
    "GP1": [("UART Tx", "comms")],
}
```

Suppress them with:

```bash
--no-user-labels
```

### Output format

Generated `data.py` deliberately uses double-quoted strings to match the
existing repository style. The generator does not use Python `repr()` for
label strings.

## Troubleshooting

### `inotifywait: command not found`

Install the watcher dependency:

```bash
sudo apt install inotify-tools
```

For a one-shot build, you can skip `pinout-update.sh` entirely and invoke
`pinout.manager` directly.

### `Permission denied` when running `pinout-update.sh`

Either set the executable bit:

```bash
chmod +x pinout-update.sh
./pinout-update.sh
```

or invoke it explicitly with Bash:

```bash
bash ./pinout-update.sh
```

### `AttributeError: 'NoneType' object has no attribute 'loader'`

Make sure the export command specifies the Python source filename, including
the `.py` suffix:

```bash
python3 -m pinout.manager \
    --export pinout_ulx3s.py pinout_ulx3s.svg \
    --overwrite
```

### Labels appear but the ULX3S board image is missing

Confirm that the source board image exists:

```bash
ls -lh ulx3s.png
```

The current `pinout_ulx3s.py` should import `Image` from `pinout.core` and use
the local image with embedding enabled:

```python
from pinout.core import Group, Image

graphic.add(Image("ulx3s.png", width=1372, height=742, embed=True))
```

After correcting the source, regenerate the SVG.

You can confirm that an embedded PNG is present in the generated SVG with:

```bash
grep -o 'data:image/png;base64' pinout_ulx3s.svg | head
```

### Browser still shows an older diagram

The browser may have the previous local SVG cached. Reload the file or close
and reopen the browser tab after regenerating it.

## Validation checklist

Before committing pinout changes:

1. Generate `pinout_ulx3s.svg` without Python exceptions.
2. Open the SVG and confirm the ULX3S board image is visible.
3. Confirm J1 and J2 labels align with the intended physical header holes.
4. Confirm every J1 physical pin 1 through 40 appears exactly once.
5. Confirm every J2 physical pin 1 through 40 appears exactly once.
6. Confirm GP0..GP27 and GN0..GN27 appear exactly once.
7. Verify FPGA package sites against the authoritative constraint file.
8. Verify power and ground pins against the schematic/manual for the intended board revision.
9. Check `git diff` for unintended generated or formatting changes.

## References

- [ULX3S FPGA constraint file - ulx3s_v20.lpf](https://github.com/emard/ulx3s/blob/master/doc/constraints/ulx3s_v20.lpf)
- [ULX3S manual](https://github.com/emard/ulx3s/blob/master/doc/MANUAL.md)
- [pinout documentation](https://pinout.readthedocs.io/)
- [ULX3S project](https://radiona.org/ulx3s/)
