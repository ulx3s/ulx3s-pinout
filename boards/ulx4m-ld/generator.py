#!/usr/bin/env python3

"""Generate Raspberry Pi 40-pin header data for ULX4M-LD.

The physical Raspberry Pi header definition is static. The FPGA site map is
for ULX4M-LD v2 and is intentionally kept separate from the user design LPF.
The LPF is parsed to show which header-connected FPGA sites are currently used
by the design.
"""

import argparse
import re
from pathlib import Path
from pprint import pformat


VARIANT = "ulx4m-ld-v2"
MAP_SOURCE = (
    "LiteX-Boards litex_boards/platforms/radiona_ulx4m_ld_v2.py "
    "RPI4 J1 connector map"
)

# Raspberry Pi 40-pin header, physical pin numbering.
# GPIO numbers are BCM GPIO numbers.
HEADER = {
    1:  ("pwr", "3V3", None, []),
    2:  ("pwr", "5V", None, []),
    3:  ("gpio", "GPIO2", 2, ["SDA1"]),
    4:  ("pwr", "5V", None, []),
    5:  ("gpio", "GPIO3", 3, ["SCL1"]),
    6:  ("gnd", "GND", None, []),
    7:  ("gpio", "GPIO4", 4, []),
    8:  ("gpio", "GPIO14", 14, ["TXD"]),
    9:  ("gnd", "GND", None, []),
    10: ("gpio", "GPIO15", 15, ["RXD"]),
    11: ("gpio", "GPIO17", 17, []),
    12: ("gpio", "GPIO18", 18, []),
    13: ("gpio", "GPIO27", 27, []),
    14: ("gnd", "GND", None, []),
    15: ("gpio", "GPIO22", 22, []),
    16: ("gpio", "GPIO23", 23, []),
    17: ("pwr", "3V3", None, []),
    18: ("gpio", "GPIO24", 24, []),
    19: ("gpio", "GPIO10", 10, ["MOSI"]),
    20: ("gnd", "GND", None, []),
    21: ("gpio", "GPIO9", 9, ["MISO"]),
    22: ("gpio", "GPIO25", 25, []),
    23: ("gpio", "GPIO11", 11, ["SCLK"]),
    24: ("gpio", "GPIO8", 8, ["CE0"]),
    25: ("gnd", "GND", None, []),
    26: ("gpio", "GPIO7", 7, ["CE1"]),
    27: ("gpio", "GPIO0", 0, ["ID_SD"]),
    28: ("gpio", "GPIO1", 1, ["ID_SC"]),
    29: ("gpio", "GPIO5", 5, []),
    30: ("gnd", "GND", None, []),
    31: ("gpio", "GPIO6", 6, []),
    32: ("gpio", "GPIO12", 12, []),
    33: ("gpio", "GPIO13", 13, []),
    34: ("gnd", "GND", None, []),
    35: ("gpio", "GPIO19", 19, []),
    36: ("gpio", "GPIO16", 16, []),
    37: ("gpio", "GPIO26", 26, []),
    38: ("gpio", "GPIO20", 20, []),
    39: ("gnd", "GND", None, []),
    40: ("gpio", "GPIO21", 21, []),
}

# ULX4M-LD v2 ECP5 sites reached by the CM4 GPIO signals. GPIO0/GPIO1 are the
# Raspberry Pi ID_SD/ID_SC signals in the CM4 connector map.
GPIO_TO_SITE = {
    0: "H1",
    1: "J3",
    2: "B18",
    3: "P17",
    4: "B15",
    5: "N1",
    6: "D7",
    7: "P3",
    8: "P4",
    9: "L5",
    10: "K4",
    11: "N2",
    12: "R11",
    13: "T1",
    14: "P2",
    15: "G1",
    16: "V4",
    17: "H3",
    18: "N5",
    19: "U1",
    20: "T5",
    21: "U5",
    22: "M3",
    23: "N4",
    24: "N3",
    25: "P5",
    26: "V1",
    27: "P1",
}

# Board-level aliases/sharing called out by the current ULX4M-LD LiteX
# platform. These are independent of the design LPF parsed below.
BOARD_NOTES = {
    2:  ["shared SD_DAT1"],
    4:  ["shared SD_DAT0"],
    12: ["JTAG TDI"],
    14: ["shared SD_DAT3"],
    15: ["shared SD_CLK"],
    16: ["JTAG TDO"],
    20: ["JTAG TCK"],
    21: ["JTAG TMS"],
    26: ["ETH PHY ref clk"],
    27: ["shared SD_CMD"],
}

LOCATE_RE = re.compile(
    r'^\s*LOCATE\s+COMP\s+"(?P<name>[^"]+)"\s+'
    r'SITE\s+"(?P<site>[^"]+)"\s*;'
)
IOBUF_RE = re.compile(
    r'^\s*IOBUF\s+PORT\s+"(?P<name>[^"]+)"\s+'
    r'(?P<attrs>[^;]*?)\s*;'
)
FREQUENCY_RE = re.compile(
    r'^\s*FREQUENCY\s+PORT\s+"(?P<name>[^"]+)"\s+'
    r'(?P<value>[^;]+?)\s*;'
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Generate ULX4M-LD Raspberry Pi 40-pin header data from an LPF."
        )
    )
    parser.add_argument(
        "lpf",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parent / "constraints" / "fpga_ulx4m_ld.lpf",
        help="Input ULX4M-LD LPF file (default: boards/ulx4m-ld/constraints/fpga_ulx4m_ld.lpf)",
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        default=Path(__file__).resolve().parent / "data.py",
        help="Output Python data module (default: boards/ulx4m-ld/data.py)",
    )
    parser.add_argument(
        "--markdown", type=Path, default=None,
        help="Also write an audit table in Markdown format",
    )
    return parser.parse_args(argv)


def parse_lpf(path):
    site_to_signals = {}
    iobuf = {}
    frequency = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        match = LOCATE_RE.match(line)
        if match:
            name = match.group("name")
            site = match.group("site")
            site_to_signals.setdefault(site, []).append(name)
            continue

        match = IOBUF_RE.match(line)
        if match:
            iobuf[match.group("name")] = " ".join(
                match.group("attrs").split()
            )
            continue

        match = FREQUENCY_RE.match(line)
        if match:
            frequency[match.group("name")] = " ".join(
                match.group("value").split()
            )

    return site_to_signals, iobuf, frequency


def build_pins(site_to_signals, iobuf, frequency):
    pins = []
    for physical in range(1, 41):
        kind, signal, gpio, aliases = HEADER[physical]
        site = GPIO_TO_SITE.get(gpio) if gpio is not None else None
        uses = list(site_to_signals.get(site, [])) if site else []
        use_details = []
        for use in uses:
            detail = {"signal": use}
            if use in iobuf:
                detail["iobuf"] = iobuf[use]
            if use in frequency:
                detail["frequency"] = frequency[use]
            use_details.append(detail)

        pins.append({
            "physical": physical,
            "kind": kind,
            "signal": signal,
            "gpio": gpio,
            "aliases": list(aliases),
            "site": site,
            "board_notes": list(BOARD_NOTES.get(gpio, [])),
            "lpf_uses": use_details,
        })

    return pins



def display_path(path):
    """Return a stable repo-relative path when the LPF is inside this repo."""
    path = Path(path)
    repo_root = Path(__file__).resolve().parents[2]
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def write_data(path, source_lpf, pins):
    text = "\n".join([
        "# Generated by generate-data-from-lpf.py. Do not edit by hand.",
        "",
        f"board_variant = {VARIANT!r}",
        f"map_source = {MAP_SOURCE!r}",
        f"source_lpf = {display_path(source_lpf)!r}",
        "",
        "pins = " + pformat(pins, sort_dicts=False, width=100),
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def markdown_cell(value):
    return str(value).replace("|", "\\|")


def write_markdown(path, source_lpf, pins):
    lines = [
        "# ULX4M-LD Raspberry Pi Header Mapping",
        "",
        f"- Board map: `{VARIANT}`",
        f"- Design constraint input: `{display_path(source_lpf)}`",
        f"- FPGA-site map source: {MAP_SOURCE}",
        "",
        "`Current LPF use` is derived by matching each header-connected FPGA",
        "site against active `LOCATE COMP` statements in the input LPF.",
        "Board notes are wiring/resource notes and do not depend on the LPF.",
        "",
        "| Physical | Header signal | Common alias | FPGA site | Board note | Current LPF use |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]

    for pin in pins:
        aliases = ", ".join(pin["aliases"]) or "-"
        site = pin["site"] or "-"
        notes = ", ".join(pin["board_notes"]) or "-"
        uses = ", ".join(item["signal"] for item in pin["lpf_uses"]) or "-"
        lines.append(
            "| {physical} | {signal} | {aliases} | {site} | {notes} | {uses} |".format(
                physical=pin["physical"],
                signal=markdown_cell(pin["signal"]),
                aliases=markdown_cell(aliases),
                site=markdown_cell(site),
                notes=markdown_cell(notes),
                uses=markdown_cell(uses),
            )
        )

    lines.extend([
        "",
        "## Header orientation in the supplied carrier image",
        "",
        "With the board viewed exactly as in `cm4-io-base-b-3_3.jpg`, the",
        "40-pin header is vertical on the right side of the carrier. Pins 1/2",
        "are at the top and pins 39/40 are at the bottom. Odd pins are the",
        "left column of the header and even pins are the right column.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def validate(pins):
    physical = [pin["physical"] for pin in pins]
    if physical != list(range(1, 41)):
        raise ValueError("physical header pins are not exactly 1 through 40")

    gpio_sites = [pin["site"] for pin in pins if pin["gpio"] is not None]
    if len(gpio_sites) != 28 or any(site is None for site in gpio_sites):
        raise ValueError("expected all BCM GPIO0 through GPIO27 header sites")

    if len(set(gpio_sites)) != len(gpio_sites):
        raise ValueError("duplicate ECP5 sites in GPIO header map")


def main(argv=None):
    args = parse_args(argv)
    if not args.lpf.is_file():
        raise SystemExit(f"LPF not found: {args.lpf}")

    site_to_signals, iobuf, frequency = parse_lpf(args.lpf)
    pins = build_pins(site_to_signals, iobuf, frequency)
    validate(pins)
    write_data(args.output, args.lpf, pins)
    print(f"Wrote {args.output}")

    if args.markdown:
        write_markdown(args.markdown, args.lpf, pins)
        print(f"Wrote {args.markdown}")

    occupied = [pin for pin in pins if pin["lpf_uses"]]
    if occupied:
        print("Header-connected FPGA sites used by this LPF:")
        for pin in occupied:
            uses = ", ".join(item["signal"] for item in pin["lpf_uses"])
            print(
                f"  pin {pin['physical']:2d} {pin['signal']:<6} "
                f"site {pin['site']:<3}: {uses}"
            )


if __name__ == "__main__":
    main()
