#!/usr/bin/env python3

"""ULX4M-LD Raspberry Pi header layout for the shared pinout generator."""

import sys
from pathlib import Path

from pinout.components.layout import Diagram
from pinout.core import Raw


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from pinout_common import (  # noqa: E402
    escape_svg,
    interpolate_point,
    load_board_data,
    normalized_png_data_uri,
    stylesheet_path,
)


data = load_board_data(__file__)
BOARD_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BOARD_DIR / "cm4-io-base-b-3_3.jpg"

DIAGRAM_WIDTH = 1260
DIAGRAM_HEIGHT = 1170

# The supplied Waveshare image is 800x800 and carries EXIF orientation data.
# Normalize that orientation before embedding it so SVG viewers and PNG export
# tools use the same pixel coordinate system.
SOURCE_WIDTH = 800
SOURCE_HEIGHT = 800

# Crop the upright source image to the carrier while retaining the complete
# Raspberry Pi header and all major carrier features.
PHOTO_CROP_X = 170.0
PHOTO_CROP_Y = 50.0
PHOTO_CROP_WIDTH = 450.0
PHOTO_CROP_HEIGHT = 695.0
PHOTO_SCALE = 1.25
PHOTO_WIDTH = PHOTO_CROP_WIDTH * PHOTO_SCALE
PHOTO_HEIGHT = PHOTO_CROP_HEIGHT * PHOTO_SCALE
PHOTO_X = 200.0
PHOTO_Y = 115.0

# Four calibration points measured on the upright 800x800 source image.
# Odd physical pins are the left column; even pins are the right column.
# Pin 1/2 are at the top and pin 39/40 are at the bottom.
HEADER_ODD_TOP = (572.4, 132.7)
HEADER_ODD_BOTTOM = (572.1, 502.3)
HEADER_EVEN_TOP = (592.7, 132.7)
HEADER_EVEN_BOTTOM = (592.5, 502.3)
HEADER_ROW_COUNT = 20

# Label geometry. Each physical pin gets exactly one horizontal row whose
# vertical center is the calibrated pin center in the carrier image.
PILL_HEIGHT = 22.0
PILL_GAP = 5.0
PILL_TEXT_PADDING = 18.0

# Keep the physical-pin pill close to the corresponding connector column.
# These anchors intentionally overlap the board photograph; there is no label
# background panel, so the carrier remains visible behind the labels.
LEFT_LABEL_RIGHT = 675.0
RIGHT_LABEL_LEFT = 760.0

PILL_MIN_WIDTH = {
    "physical": 66.0,
    "gpio": 76.0,
    "site": 54.0,
    "alias": 68.0,
    "pwr": 58.0,
    "gnd": 58.0,
    "board-note": 100.0,
    "active": 82.0,
    "active-critical": 104.0,
}

# Fixed 3x3 legend below the carrier. Do not flow entries based on text width.
LEGEND_X = 200.0
LEGEND_Y = 1040.0
LEGEND_COL_WIDTH = 195.0
LEGEND_ROW_HEIGHT = 30.0
LEGEND_SWATCH_WIDTH = 26.0
LEGEND_SWATCH_HEIGHT = 17.0
LEGEND_PADDING_X = 16.0
LEGEND_PADDING_Y = 14.0


def text_width(text):
    """Estimate rendered label text width for the configured SVG font."""
    return len(str(text)) * 7.1


def pill_width(text, tag):
    """Return a deterministic width that keeps label text inside its pill."""
    minimum = PILL_MIN_WIDTH.get(tag, 76.0)
    return max(minimum, text_width(text) + PILL_TEXT_PADDING)


def pill(x, center_y, text, tag, width=None):
    """Render one label pill centered on one physical-pin row."""
    width = pill_width(text, tag) if width is None else width
    y = center_y - PILL_HEIGHT / 2.0
    return (
        f'<g class="pill {escape_svg(tag)}">'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" '
        f'height="{PILL_HEIGHT:.1f}" />'
        f'<text x="{x + width / 2.0:.1f}" y="{center_y + 0.5:.1f}">'
        f'{escape_svg(text)}</text>'
        f'</g>'
    )


def label_items(pin):
    """Return all visible labels for one physical header pin."""
    items = [(f"Pin {pin['physical']}", "physical")]

    if pin["kind"] == "pwr":
        items.append((pin["signal"], "pwr"))
        return items
    if pin["kind"] == "gnd":
        items.append((pin["signal"], "gnd"))
        return items

    items.append((pin["signal"], "gpio"))
    for alias in pin["aliases"]:
        items.append((alias, "alias"))
    if pin["site"]:
        items.append((pin["site"], "site"))
    for note in pin["board_notes"]:
        items.append((note, "board-note"))
    for use in pin["lpf_uses"]:
        signal = use["signal"]
        tag = "active-critical" if signal.startswith("ddram_") else "active"
        items.append((signal, tag))

    return items


def source_to_diagram(source_x, source_y):
    """Map an upright source-image point into diagram coordinates."""
    x = PHOTO_X + (source_x - PHOTO_CROP_X) * PHOTO_SCALE
    y = PHOTO_Y + (source_y - PHOTO_CROP_Y) * PHOTO_SCALE
    return x, y


def pin_target(pin_number):
    """Return the diagram coordinate for one physical header pin center."""
    row_index = (pin_number - 1) // 2
    if pin_number % 2:
        point = interpolate_point(
            HEADER_ODD_TOP,
            HEADER_ODD_BOTTOM,
            row_index,
            HEADER_ROW_COUNT,
        )
    else:
        point = interpolate_point(
            HEADER_EVEN_TOP,
            HEADER_EVEN_BOTTOM,
            row_index,
            HEADER_ROW_COUNT,
        )
    return source_to_diagram(*point)


def render_left_row(pin, target_x, target_y):
    """Render an odd-pin row immediately to the left of the connector."""
    items = label_items(pin)
    output = []

    # Pin number stays nearest the carrier. Remaining semantic labels extend
    # outward to the left, mirroring the even-pin rows.
    cursor_x = LEFT_LABEL_RIGHT
    for text, tag in items:
        width = pill_width(text, tag)
        cursor_x -= width
        output.append(pill(cursor_x, target_y, text, tag, width))
        cursor_x -= PILL_GAP

    output.append(
        f'<line class="leader" x1="{LEFT_LABEL_RIGHT + 2.0:.1f}" '
        f'y1="{target_y:.1f}" x2="{target_x:.1f}" y2="{target_y:.1f}" />'
    )
    output.append(
        f'<circle class="leader-dot" cx="{target_x:.1f}" '
        f'cy="{target_y:.1f}" r="3.7" />'
    )
    return "\n".join(output)


def render_right_row(pin, target_x, target_y):
    """Render an even-pin row immediately to the right of the connector."""
    items = label_items(pin)
    output = []
    cursor_x = RIGHT_LABEL_LEFT

    for text, tag in items:
        width = pill_width(text, tag)
        output.append(pill(cursor_x, target_y, text, tag, width))
        cursor_x += width + PILL_GAP

    output.append(
        f'<line class="leader" x1="{target_x:.1f}" y1="{target_y:.1f}" '
        f'x2="{RIGHT_LABEL_LEFT - 2.0:.1f}" y2="{target_y:.1f}" />'
    )
    output.append(
        f'<circle class="leader-dot" cx="{target_x:.1f}" '
        f'cy="{target_y:.1f}" r="3.7" />'
    )
    return "\n".join(output)


def render_labels(pins):
    """Render all 40 labels as 20 pin-aligned horizontal row pairs."""
    output = []

    for pin in pins:
        target_x, target_y = pin_target(pin["physical"])
        if pin["physical"] % 2:
            output.append(render_left_row(pin, target_x, target_y))
        else:
            output.append(render_right_row(pin, target_x, target_y))

    return "\n".join(output)


def legend_entry(x, y, label, tag):
    """Render one entry inside the fixed legend grid."""
    swatch_y = y + (LEGEND_ROW_HEIGHT - LEGEND_SWATCH_HEIGHT) / 2.0
    return (
        f'<g class="pill {escape_svg(tag)}">'
        f'<rect x="{x:.1f}" y="{swatch_y:.1f}" '
        f'width="{LEGEND_SWATCH_WIDTH:.1f}" '
        f'height="{LEGEND_SWATCH_HEIGHT:.1f}" />'
        f'</g>'
        f'<text class="legend-label" x="{x + LEGEND_SWATCH_WIDTH + 9.0:.1f}" '
        f'y="{y + LEGEND_ROW_HEIGHT / 2.0 + 0.5:.1f}">{escape_svg(label)}</text>'
    )


def render_legend():
    """Render a stable 3x3 legend with equal column and row spacing."""
    entries = [
        ("Physical pin", "physical"),
        ("Raspberry Pi GPIO", "gpio"),
        ("FPGA site", "site"),
        ("Common alias", "alias"),
        ("Board/shared resource", "board-note"),
        ("Current LPF use", "active"),
        ("Current LPF critical use", "active-critical"),
        ("Power", "pwr"),
        ("Ground", "gnd"),
    ]

    frame_width = 3 * LEGEND_COL_WIDTH + 2 * LEGEND_PADDING_X
    frame_height = 3 * LEGEND_ROW_HEIGHT + 2 * LEGEND_PADDING_Y
    output = [
        f'<rect class="legend-frame" x="{LEGEND_X:.1f}" y="{LEGEND_Y:.1f}" '
        f'width="{frame_width:.1f}" height="{frame_height:.1f}" rx="8" ry="8" />'
    ]

    for index, (label, tag) in enumerate(entries):
        row = index // 3
        column = index % 3
        x = LEGEND_X + LEGEND_PADDING_X + column * LEGEND_COL_WIDTH
        y = LEGEND_Y + LEGEND_PADDING_Y + row * LEGEND_ROW_HEIGHT
        output.append(legend_entry(x, y, label, tag))

    return "\n".join(output)


def render_content():
    """Render SVG child markup for the module-level Diagram instance."""
    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(f"carrier image not found: {IMAGE_PATH}")

    image_uri = normalized_png_data_uri(
        IMAGE_PATH,
        expected_size=(SOURCE_WIDTH, SOURCE_HEIGHT),
    )
    image_x = PHOTO_X - PHOTO_CROP_X * PHOTO_SCALE
    image_y = PHOTO_Y - PHOTO_CROP_Y * PHOTO_SCALE
    image_width = SOURCE_WIDTH * PHOTO_SCALE
    image_height = SOURCE_HEIGHT * PHOTO_SCALE

    labels = render_labels(data.pins)
    legend = render_legend()

    return f'''
<g class="ulx4m">
<rect class="background" x="0" y="0" width="100%" height="100%" />
<text class="title" x="{DIAGRAM_WIDTH / 2.0}" y="26" text-anchor="middle">
ULX4M-LD on Waveshare CM4-IO-BASE-B - Raspberry Pi 40-pin header
</text>
<text class="subtitle" x="{DIAGRAM_WIDTH / 2.0}" y="49" text-anchor="middle">
Pin 1/2 at top; odd pins left, even pins right. Current LPF overlay: {escape_svg(data.source_lpf)}
</text>

<defs>
  <clipPath id="photoClip">
    <rect x="{PHOTO_X:.1f}" y="{PHOTO_Y:.1f}"
          width="{PHOTO_WIDTH:.1f}" height="{PHOTO_HEIGHT:.1f}" />
  </clipPath>
</defs>

<rect class="board-frame" x="{PHOTO_X - 3.0:.1f}" y="{PHOTO_Y - 3.0:.1f}"
      width="{PHOTO_WIDTH + 6.0:.1f}" height="{PHOTO_HEIGHT + 6.0:.1f}"
      rx="8" ry="8" />
<g clip-path="url(#photoClip)">
  <image x="{image_x:.2f}" y="{image_y:.2f}"
         width="{image_width:.2f}" height="{image_height:.2f}"
         href="{image_uri}" />
</g>

{labels}

<text class="warning" x="210" y="1018">
Pin 5 / GPIO3 / site P17 is currently ddram_a[12]; it is not a free HAT GPIO in this LPF.
</text>

{legend}
</g>
'''


# pinout.manager imports this module and looks for an object named "diagram".
diagram = Diagram(DIAGRAM_WIDTH, DIAGRAM_HEIGHT, "diagram")
diagram.add_stylesheet(str(stylesheet_path()), True)
diagram.add(Raw(render_content()))
