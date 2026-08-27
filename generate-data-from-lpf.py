#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path


EXPECTED_INDICES = set(range(28))
DIFF_INDICES = set(range(8, 22))

# Optional user-defined labels that are not part of the LPF.
USER_LABELS = {
    "GP0": [("UART Rx", "comms")],
    "GP1": [("UART Tx", "comms")],
}

BASE_LEGEND = [
    ("GP single-ended", "gpsingle"),
    ("GN single-ended", "gnsingle"),
    ("GP differential (+)", "gpdiff"),
    ("GN differential (-)", "gndiff"),
    ("FPGA site", "site"),
    ("Analog", "analog"),
    ("Communication", "comms"),
    ("Ground", "gnd"),
    ("GPIO", "gpio"),
    ("Touch", "touch"),
    ("Power", "pwr"),
    ("PWM", "pwm"),
]

INCLUDE_FIELDS = (
    "aliases",
    "connector",
    "flags",
    "iobuf",
    "pullmode",
    "io_type",
    "drive",
    "frequency",
    "comment",
)

# J1/J2 connector structure is not encoded by FPGA LOCATE constraints.
# These templates describe the physical 2x20 headers used by the diagram.
#
# Physical numbering is for the female 90-degree angled header on top.
# A male vertical header viewed from the opposite side changes the apparent
# odd/even orientation and must be checked before wiring.
J1_EVEN = [
    (2, "pwr", "2.5/3.3V"),
    (4, "gnd", "GND"),
    (6, "gp", 0),
    (8, "gp", 1),
    (10, "gp", 2),
    (12, "gp", 3),
    (14, "gp", 4),
    (16, "gp", 5),
    (18, "gp", 6),
    (20, "pwr", "2.5/3.3V"),
    (22, "gnd", "GND"),
    (24, "gp", 7),
    (26, "gp", 8),
    (28, "gp", 9),
    (30, "gp", 10),
    (32, "gp", 11),
    (34, "gp", 12),
    (36, "gp", 13),
    (38, "gnd", "GND"),
    (40, "pwr", "2.5/3.3V"),
]

J1_ODD = [
    (1, "pwr", "2.5/3.3V"),
    (3, "gnd", "GND"),
    (5, "gn", 0),
    (7, "gn", 1),
    (9, "gn", 2),
    (11, "gn", 3),
    (13, "gn", 4),
    (15, "gn", 5),
    (17, "gn", 6),
    (19, "pwr", "2.5/3.3V"),
    (21, "gnd", "GND"),
    (23, "gn", 7),
    (25, "gn", 8),
    (27, "gn", 9),
    (29, "gn", 10),
    (31, "gn", 11),
    (33, "gn", 12),
    (35, "gn", 13),
    (37, "gnd", "GND"),
    (39, "pwr", "2.5/3.3V"),
]

# J2 is emitted in top-to-bottom rendering order to match the board image.
J2_ODD = [
    (39, "pwr", "5V IN"),
    (37, "gnd", "GND"),
    (35, "gn", 27),
    (33, "gn", 26),
    (31, "gn", 25),
    (29, "gn", 24),
    (27, "gn", 23),
    (25, "gn", 22),
    (23, "gn", 21),
    (21, "gnd", "GND"),
    (19, "pwr", "3.3V"),
    (17, "gn", 20),
    (15, "gn", 19),
    (13, "gn", 18),
    (11, "gn", 17),
    (9, "gn", 16),
    (7, "gn", 15),
    (5, "gn", 14),
    (3, "gnd", "GND"),
    (1, "pwr", "3.3V"),
]

J2_EVEN = [
    (40, "pwr", "5V OUT"),
    (38, "gnd", "GND"),
    (36, "gp", 27),
    (34, "gp", 26),
    (32, "gp", 25),
    (30, "gp", 24),
    (28, "gp", 23),
    (26, "gp", 22),
    (24, "gp", 21),
    (22, "gnd", "GND"),
    (20, "pwr", "3.3V"),
    (18, "gp", 20),
    (16, "gp", 19),
    (14, "gp", 18),
    (12, "gp", 17),
    (10, "gp", 16),
    (8, "gp", 15),
    (6, "gp", 14),
    (4, "gnd", "GND"),
    (2, "pwr", "3.3V"),
]

LOCATE_RE = re.compile(
    r'^\s*LOCATE\s+COMP\s+"(?P<name>[^"]+)"'
    r'\s+SITE\s+"(?P<site>[^"]+)"\s*;'
    r'\s*(?:#\s*(?P<comment>.*))?$',
    re.IGNORECASE,
)
IOBUF_RE = re.compile(
    r'^\s*IOBUF\s+PORT\s+"(?P<name>[^"]+)"'
    r'\s+(?P<attrs>[^;]*?)\s*;'
    r'\s*(?:#\s*(?P<comment>.*))?$',
    re.IGNORECASE,
)
FREQUENCY_RE = re.compile(
    r'^\s*FREQUENCY\s+PORT\s+"(?P<name>[^"]+)"'
    r'\s+(?P<value>[^;]+?)\s*;'
    r'\s*(?:#\s*(?P<comment>.*))?$',
    re.IGNORECASE,
)
ATTR_RE = re.compile(
    r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)='
    r'(?P<value>"[^"]*"|[^\s]+)'
)
VECTOR_RE = re.compile(r'^(gp|gn)\[(\d+)\]$', re.IGNORECASE)
SCALAR_RE = re.compile(r'^(gp|gn)(\d+)$', re.IGNORECASE)
BOARD_RE = re.compile(r'^\s*##\s*ULX3S\s+(.+?)\s*$')

CONNECTOR_RE = re.compile(r'\b(J[12]_\d+[+-])\b', re.IGNORECASE)
WIFI_ALIAS_RE = re.compile(r'\bwifi_gpio\d+\b', re.IGNORECASE)
SENSOR_ALIAS_RE = re.compile(r'\bsensor_[A-Za-z0-9_]+\b', re.IGNORECASE)
ADC_ALIAS_RE = re.compile(r'\bADC\s+AIN\d+\b', re.IGNORECASE)
FLAG_RE = re.compile(r'\b(GR_PCLK|PCLK|DIFF)\b', re.IGNORECASE)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate ULX3S pinout data.py from GP/GN LOCATE constraints, "
            "with optional LPF aliases and metadata labels."
        )
    )
    parser.add_argument("lpf", type=Path, help="Input ULX3S .lpf file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("data.py"),
        help="Output Python file (default: data.py)",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="FIELD[,FIELD...]",
        help=(
            "Optional labels to add. Fields: "
            + ", ".join(INCLUDE_FIELDS)
            + ", all. May be repeated."
        ),
    )
    parser.add_argument(
        "--iobuf-key",
        action="append",
        default=[],
        metavar="KEY",
        help=(
            "Include a specific IOBUF key not covered by --include. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--gpio-form",
        choices=("auto", "vector", "scalar"),
        default="auto",
        help=(
            "GPIO definition form used for comments/IOBUF/frequency metadata. "
            "auto prefers a complete vector gp[n]/gn[n] set."
        ),
    )
    parser.add_argument(
        "--strict-form-metadata",
        action="store_true",
        help=(
            "Fail instead of warning if vector and scalar aliases have "
            "different IOBUF or FREQUENCY metadata."
        ),
    )
    parser.add_argument(
        "--no-user-labels",
        action="store_true",
        help="Do not emit USER_LABELS such as the GP0/GP1 UART examples.",
    )
    parser.add_argument(
        "--list-fields",
        action="store_true",
        help="List values accepted by --include and exit.",
    )
    return parser.parse_args()


def double_quote(value):
    value = str(value)
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    value = value.replace("\t", "\\t")
    return '"' + value + '"'


def normalize_signal(name):
    match = VECTOR_RE.fullmatch(name)
    if match:
        return match.group(1).lower(), int(match.group(2)), "vector"

    match = SCALAR_RE.fullmatch(name)
    if match:
        return match.group(1).lower(), int(match.group(2)), "scalar"

    return None


def parse_include_fields(values):
    result = []
    for value in values:
        for item in value.split(","):
            item = item.strip().lower()
            if not item:
                continue
            if item == "all":
                for field in INCLUDE_FIELDS:
                    if field not in result:
                        result.append(field)
                continue
            if item not in INCLUDE_FIELDS:
                raise ValueError(
                    f"unknown --include field {item!r}; valid fields: "
                    + ", ".join(INCLUDE_FIELDS)
                    + ", all"
                )
            if item not in result:
                result.append(item)
    return result


def parse_iobuf_attrs(text):
    attrs = []
    for match in ATTR_RE.finditer(text):
        key = match.group("key").upper()
        value = match.group("value")
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        attrs.append((key, value))
    return attrs


def make_record(name, site=None, comment=""):
    return {
        "name": name,
        "site": site,
        "comment": comment.strip(),
        "iobuf": [],
        "frequency": None,
    }


def parse_lpf(path):
    text = path.read_text(encoding="utf-8", errors="replace")

    board = "unknown"
    for line in text.splitlines():
        match = BOARD_RE.match(line)
        if match:
            board = match.group(1).strip()
            break

    all_locates = []
    records = {}

    for line_number, line in enumerate(text.splitlines(), start=1):
        locate = LOCATE_RE.match(line)
        if locate:
            name = locate.group("name")
            site = locate.group("site").upper()
            comment = locate.group("comment") or ""
            all_locates.append((name, site))

            normalized = normalize_signal(name)
            if normalized is not None:
                key = normalized
                previous = records.get(key)
                if previous is not None and previous["site"] != site:
                    raise ValueError(
                        f"{path}:{line_number}: conflicting SITE for {name}: "
                        f"{previous['site']} vs {site}"
                    )
                if previous is None:
                    records[key] = make_record(name, site, comment)
                elif comment and not previous["comment"]:
                    previous["comment"] = comment.strip()
            continue

        iobuf = IOBUF_RE.match(line)
        if iobuf:
            normalized = normalize_signal(iobuf.group("name"))
            if normalized is not None:
                record = records.setdefault(
                    normalized,
                    make_record(iobuf.group("name")),
                )
                attrs = parse_iobuf_attrs(iobuf.group("attrs"))
                if attrs:
                    record["iobuf"] = attrs
            continue

        frequency = FREQUENCY_RE.match(line)
        if frequency:
            normalized = normalize_signal(frequency.group("name"))
            if normalized is not None:
                record = records.setdefault(
                    normalized,
                    make_record(frequency.group("name")),
                )
                record["frequency"] = " ".join(
                    frequency.group("value").split()
                )
            continue

    return board, records, all_locates


def form_complete(records, form):
    for kind in ("gp", "gn"):
        for index in EXPECTED_INDICES:
            record = records.get((kind, index, form))
            if record is None or record["site"] is None:
                return False
    return True


def choose_gpio_form(records, requested):
    vector_complete = form_complete(records, "vector")
    scalar_complete = form_complete(records, "scalar")

    if requested == "vector":
        if not vector_complete:
            raise ValueError(
                "--gpio-form vector requested but GP0..GP27/GN0..GN27 "
                "vector LOCATE entries are incomplete"
            )
        return "vector"

    if requested == "scalar":
        if not scalar_complete:
            raise ValueError(
                "--gpio-form scalar requested but GP0..GP27/GN0..GN27 "
                "scalar LOCATE entries are incomplete"
            )
        return "scalar"

    if vector_complete:
        return "vector"
    if scalar_complete:
        return "scalar"

    raise ValueError(
        "neither vector gp[n]/gn[n] nor scalar gpN/gnN contains a complete "
        "GP0..GP27/GN0..GN27 LOCATE set"
    )


def validate_site_consistency(records):
    conflicts = []
    for kind in ("gp", "gn"):
        for index in range(28):
            vector = records.get((kind, index, "vector"))
            scalar = records.get((kind, index, "scalar"))
            if (
                vector is not None
                and scalar is not None
                and vector["site"] is not None
                and scalar["site"] is not None
                and vector["site"] != scalar["site"]
            ):
                conflicts.append(
                    f"{kind.upper()}{index}: vector SITE {vector['site']} "
                    f"!= scalar SITE {scalar['site']}"
                )
    if conflicts:
        raise ValueError(
            "vector/scalar SITE conflicts:\n  " + "\n  ".join(conflicts)
        )


def metadata_signature(record):
    if record is None:
        return (), None
    return tuple(record["iobuf"]), record["frequency"]


def find_form_metadata_conflicts(records):
    conflicts = []
    for kind in ("gp", "gn"):
        for index in range(28):
            vector = records.get((kind, index, "vector"))
            scalar = records.get((kind, index, "scalar"))
            if (
                vector is None
                or scalar is None
                or vector["site"] is None
                or scalar["site"] is None
            ):
                continue
            if metadata_signature(vector) != metadata_signature(scalar):
                conflicts.append(
                    (
                        f"{kind.upper()}{index}",
                        vector["iobuf"],
                        vector["frequency"],
                        scalar["iobuf"],
                        scalar["frequency"],
                    )
                )
    return conflicts


def build_site_aliases(all_locates):
    by_site = {}
    for name, site in all_locates:
        if normalize_signal(name) is not None:
            continue
        names = by_site.setdefault(site, [])
        if name not in names:
            names.append(name)
    return by_site


def unique_extend(target, values):
    for value in values:
        if value and value not in target:
            target.append(value)


def comment_aliases(comment):
    aliases = []
    unique_extend(aliases, WIFI_ALIAS_RE.findall(comment))
    unique_extend(aliases, SENSOR_ALIAS_RE.findall(comment))
    unique_extend(
        aliases,
        [" ".join(value.upper().split()) for value in ADC_ALIAS_RE.findall(comment)],
    )
    return aliases


def comment_connector(comment):
    match = CONNECTOR_RE.search(comment)
    return match.group(1).upper() if match else None



def connector_name(header, pin, row_type):
    if row_type not in ("gp", "gn"):
        return None
    pair_pin = pin - 1 if row_type == "gp" else pin
    polarity = "+" if row_type == "gp" else "-"
    return f"{header}_{pair_pin}{polarity}"


def comment_flags(comment):
    flags = []
    for match in FLAG_RE.finditer(comment):
        flag = match.group(1).upper()
        if flag not in flags:
            flags.append(flag)
    return flags


def signal_tag(kind, index):
    if kind == "gp":
        return "gpdiff" if index in DIFF_INDICES else "gpsingle"
    return "gndiff" if index in DIFF_INDICES else "gnsingle"


def metadata_label(key, value):
    key = key.upper()
    if key == "PULLMODE":
        return f"PULL={value}"
    if key == "IO_TYPE":
        return f"IO={value}"
    if key == "DRIVE":
        return f"DRIVE={value}"
    return f"{key}={value}"


def included_iobuf_keys(include_fields, explicit_keys, record):
    keys = []
    explicit = {value.upper() for value in explicit_keys}

    if "iobuf" in include_fields:
        for key, _value in record["iobuf"]:
            if key not in keys:
                keys.append(key)

    field_to_key = {
        "pullmode": "PULLMODE",
        "io_type": "IO_TYPE",
        "drive": "DRIVE",
    }
    for field, key in field_to_key.items():
        if field in include_fields and key not in keys:
            keys.append(key)

    for key in explicit:
        if key not in keys:
            keys.append(key)

    return keys


def row_items(
    header,
    pin,
    row_type,
    value,
    records,
    selected_form,
    site_aliases,
    include_fields,
    explicit_iobuf_keys,
    include_user_labels,
):
    if row_type == "pwr":
        return [(str(pin), "pwr"), (str(value), "pwr")]

    if row_type == "gnd":
        return [(str(pin), "gnd"), ("GND", "gnd")]

    index = int(value)
    signal = f"{row_type.upper()}{index}"
    record = records[(row_type, index, selected_form)]

    items = [
        (str(pin), "gpio"),
        (signal, signal_tag(row_type, index)),
    ]

    if include_user_labels:
        items.extend(USER_LABELS.get(signal, []))

    if "aliases" in include_fields:
        aliases = []
        unique_extend(aliases, comment_aliases(record["comment"]))
        unique_extend(aliases, site_aliases.get(record["site"], []))
        for alias in aliases:
            items.append((alias, "alias"))

    if "connector" in include_fields:
        connector = connector_name(header, pin, row_type)
        parsed_connector = comment_connector(record["comment"])
        if parsed_connector is not None and parsed_connector != connector:
            raise ValueError(
                f"{signal}: LPF connector comment {parsed_connector} "
                f"does not match expected {connector}"
            )
        items.append((connector, "connector"))

    if "flags" in include_fields:
        for flag in comment_flags(record["comment"]):
            items.append((flag, "meta"))

    wanted_iobuf = included_iobuf_keys(
        include_fields,
        explicit_iobuf_keys,
        record,
    )
    values = dict(record["iobuf"])
    for key in wanted_iobuf:
        if key in values:
            items.append((metadata_label(key, values[key]), "meta"))

    if "frequency" in include_fields and record["frequency"]:
        items.append((f"FREQ={record['frequency']}", "meta"))

    if "comment" in include_fields and record["comment"]:
        items.append((f"COMMENT: {record['comment']}", "meta"))

    items.append((record["site"], "site"))
    return items


def build_rows(
    header,
    template,
    records,
    selected_form,
    site_aliases,
    include_fields,
    explicit_iobuf_keys,
    include_user_labels,
):
    return [
        row_items(
            header,
            pin,
            row_type,
            value,
            records,
            selected_form,
            site_aliases,
            include_fields,
            explicit_iobuf_keys,
            include_user_labels,
        )
        for pin, row_type, value in template
    ]


def format_rows(name, rows):
    lines = [f"{name} = ["]
    for row in rows:
        lines.append("    [")
        for text, tag in row:
            lines.append(
                f"        ({double_quote(text)}, {double_quote(tag)}),"
            )
        lines.append("    ],")
    lines.append("]")
    return "\n".join(lines)


def format_string_list(name, values):
    lines = [f"{name} = ["]
    for value in values:
        lines.append(f"    {double_quote(value)},")
    lines.append("]")
    return "\n".join(lines)


def format_legend(include_fields, explicit_iobuf_keys):
    legend = list(BASE_LEGEND)
    if "aliases" in include_fields:
        legend.append(("LPF alias", "alias"))
    if "connector" in include_fields:
        legend.append(("Connector position", "connector"))
    if (
        any(
            field in include_fields
            for field in (
                "flags",
                "iobuf",
                "pullmode",
                "io_type",
                "drive",
                "frequency",
                "comment",
            )
        )
        or explicit_iobuf_keys
    ):
        legend.append(("LPF metadata", "meta"))

    lines = ["legend = ["]
    for text, tag in legend:
        lines.append(
            f"    ({double_quote(text)}, {double_quote(tag)}),"
        )
    lines.append("]")
    return "\n".join(lines)


def validate_generated_text(text):
    namespace = {}
    exec(compile(text, "generated-data.py", "exec"), namespace)

    for name in (
        "left_header_even",
        "left_header_odd",
        "right_header_even",
        "right_header_odd",
    ):
        if len(namespace[name]) != 20:
            raise RuntimeError(f"{name} does not contain 20 physical pins")

    j1_pins = sorted(
        int(row[0][0])
        for name in ("left_header_even", "left_header_odd")
        for row in namespace[name]
    )
    j2_pins = sorted(
        int(row[0][0])
        for name in ("right_header_even", "right_header_odd")
        for row in namespace[name]
    )

    if j1_pins != list(range(1, 41)):
        raise RuntimeError("J1 does not contain physical pins 1..40 exactly once")
    if j2_pins != list(range(1, 41)):
        raise RuntimeError("J2 does not contain physical pins 1..40 exactly once")


def generate_data(
    source,
    board,
    records,
    selected_form,
    all_locates,
    include_fields,
    explicit_iobuf_keys,
    include_user_labels,
):
    site_aliases = build_site_aliases(all_locates)

    sections = [
        "# This file is generated by generate-data-from-lpf.py.",
        "# FPGA GP/GN sites and optional LPF metadata come from the LPF input.",
        "# J1/J2 power, ground, physical connector layout, and USER_LABELS are",
        "# maintained by the generator because they are not FPGA LOCATE entries.",
        "",
        f"lpf_source = {double_quote(source.name)}",
        f"lpf_board = {double_quote(board)}",
        f"lpf_gpio_form = {double_quote(selected_form)}",
        format_string_list("lpf_included_fields", include_fields),
        "",
        format_legend(include_fields, explicit_iobuf_keys),
        "",
        "# Pinlabels",
        "#",
        "# Physical pin numbering is for the female 90-degree angled header.",
        "# For a male vertical header, confirm orientation before wiring.",
        "",
        format_rows(
            "left_header_even",
            build_rows(
                "J1",
                J1_EVEN,
                records,
                selected_form,
                site_aliases,
                include_fields,
                explicit_iobuf_keys,
                include_user_labels,
            ),
        ),
        "",
        "",
        format_rows(
            "left_header_odd",
            build_rows(
                "J1",
                J1_ODD,
                records,
                selected_form,
                site_aliases,
                include_fields,
                explicit_iobuf_keys,
                include_user_labels,
            ),
        ),
        "",
        "",
        format_rows(
            "right_header_odd",
            build_rows(
                "J2",
                J2_ODD,
                records,
                selected_form,
                site_aliases,
                include_fields,
                explicit_iobuf_keys,
                include_user_labels,
            ),
        ),
        "",
        "",
        format_rows(
            "right_header_even",
            build_rows(
                "J2",
                J2_EVEN,
                records,
                selected_form,
                site_aliases,
                include_fields,
                explicit_iobuf_keys,
                include_user_labels,
            ),
        ),
        "",
        "",
        "lower_header = [",
        "    [",
        '        ("3", "gpio"),',
        '        ("PWM", "pwm"),',
        "    ],",
        "    [",
        '        ("4", "gpio"),',
        '        ("A2", "analog"),',
        '        ("TOUCH", "touch"),',
        "    ],",
        "    [",
        '        ("5", "gpio"),',
        '        ("A3", "analog"),',
        "    ],",
        "]",
        "",
        "",
        "# Text",
        "",
        'title = "<tspan class=\'h1\'>ULX3S Pinout</tspan>"',
        "",
        'description = """Created with Python tool kit to assist with',
        "documentation of electronic hardware.",
        "More info at <tspan class='italic strong'>pinout.readthedocs.io</tspan>\"\"\"",
        "",
    ]
    text = "\n".join(sections)
    validate_generated_text(text)
    return text


def print_metadata_conflicts(conflicts):
    for signal, vector_iobuf, vector_freq, scalar_iobuf, scalar_freq in conflicts:
        print(
            f"WARNING: {signal} vector/scalar metadata differs:",
            file=sys.stderr,
        )
        print(
            f"  vector: IOBUF={vector_iobuf!r} FREQUENCY={vector_freq!r}",
            file=sys.stderr,
        )
        print(
            f"  scalar: IOBUF={scalar_iobuf!r} FREQUENCY={scalar_freq!r}",
            file=sys.stderr,
        )


def main():
    args = parse_args()

    if args.list_fields:
        print("Valid --include fields:")
        for field in INCLUDE_FIELDS:
            print(f"  {field}")
        print("  all")
        return 0

    if not args.lpf.is_file():
        print(f"ERROR: LPF file not found: {args.lpf}", file=sys.stderr)
        return 1

    try:
        include_fields = parse_include_fields(args.include)
        board, records, all_locates = parse_lpf(args.lpf)
        validate_site_consistency(records)
        selected_form = choose_gpio_form(records, args.gpio_form)
        metadata_conflicts = find_form_metadata_conflicts(records)
        if metadata_conflicts:
            print_metadata_conflicts(metadata_conflicts)
            if args.strict_form_metadata:
                print(
                    "ERROR: vector/scalar metadata differs and "
                    "--strict-form-metadata was requested",
                    file=sys.stderr,
                )
                return 1

        text = generate_data(
            args.lpf,
            board,
            records,
            selected_form,
            all_locates,
            include_fields,
            args.iobuf_key,
            include_user_labels=not args.no_user_labels,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="\n")

    print(f"LPF: {args.lpf}")
    print(f"Board: {board}")
    print(f"GPIO form: {selected_form}")
    if include_fields:
        print("Included labels: " + ", ".join(include_fields))
    else:
        print("Included labels: none (base pinout only)")
    if args.iobuf_key:
        print("Additional IOBUF keys: " + ", ".join(args.iobuf_key))
    print("Validated: GP0..GP27 and GN0..GN27")
    print("Validated: J1 and J2 physical pins 1..40 exactly once")
    print(f"Wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
