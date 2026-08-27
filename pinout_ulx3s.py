###########################################
#
# ULX3S based on example script to build a
# pinout diagram. Includes basic
# features and convenience classes.
#
###########################################

from pinout.core import Group, Image, Raw
from pinout.components.layout import Diagram, Panel
from pinout.components.pinlabel import PinLabelGroup, PinLabel
from pinout.components.text import TextBlock
from pinout.components import leaderline as lline
from pinout.components.legend import Legend

from custom_components import PNG_from_web

# Import data for the diagram
import data

# Layout settings
#
# EXTRA_LABEL_SPACE_PER_SIDE is the main setting to change when user labels
# extend beyond the left or right side of the frame.  Increasing it adds the
# same amount of space to both sides while keeping the ULX3S centered.
#
# BOARD_X_ADJUST can be used for an asymmetric layout.  Positive values move
# the board and all pin labels right; negative values move them left.
EXTRA_LABEL_SPACE_PER_SIDE = 100
BOARD_X_ADJUST = 0

# Pin-label body dimensions.
#
# Each semantic label type has an independent width.  Physical connector pin
# numbers are detected by numeric content first, because their CSS tag may be
# "gpio", "pwr", or "gnd" depending on the pin function.
PIN_LABEL_HEIGHT = 20
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

# Pin-label pill appearance.
#
# The upstream pinout default corner radius is 3.  Use a slightly larger
# radius here for a softer pill shape.  Border styling is injected into the
# generated SVG from these variables so all pill appearance settings remain
# together in this file.
PIN_LABEL_CORNER_RADIUS = 5
PIN_LABEL_BORDER_COLOR = "rgb(54, 54, 54)"
PIN_LABEL_BORDER_WIDTH = 1.5

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
    "analog": ANALOG_LABEL_WIDTH,
    "pwm": PWM_LABEL_WIDTH,
    "touch": TOUCH_LABEL_WIDTH,
}

BASE_DIAGRAM_WIDTH = 1600
BASE_CONTENT_WIDTH = 1560
BASE_GRAPHIC_X = 95
BASE_LEGEND_X = 280

DIAGRAM_HEIGHT = 900
CONTENT_HEIGHT = 880
MAIN_PANEL_HEIGHT = 758
GRAPHIC_Y = 8
LEGEND_Y = 10
LEGEND_MAX_HEIGHT = 96

DIAGRAM_WIDTH = BASE_DIAGRAM_WIDTH + (2 * EXTRA_LABEL_SPACE_PER_SIDE)
CONTENT_WIDTH = BASE_CONTENT_WIDTH + (2 * EXTRA_LABEL_SPACE_PER_SIDE)
GRAPHIC_X = BASE_GRAPHIC_X + EXTRA_LABEL_SPACE_PER_SIDE + BOARD_X_ADJUST
LEGEND_X = BASE_LEGEND_X + EXTRA_LABEL_SPACE_PER_SIDE


def label_width(content, tag):
    """Return the configured body width for one pin label."""
    if str(content).isdigit():
        return PIN_NUMBER_LABEL_WIDTH

    return LABEL_WIDTH_BY_TAG.get(tag, DEFAULT_LABEL_WIDTH)


def pin_label_border_style():
    """Return an inline SVG stylesheet for the configured pill border."""
    return (
        '<style type="text/css">\n'
        '.pinlabel__body {\n'
        f'    stroke: {PIN_LABEL_BORDER_COLOR};\n'
        f'    stroke-width: {PIN_LABEL_BORDER_WIDTH};\n'
        '    stroke-linejoin: round;\n'
        '}\n'
        '</style>\n'
    )


def labels_with_dimensions(rows):
    """Add per-label body dimensions without changing data.py."""
    result = []

    for row in rows:
        output_row = []

        for label in row:
            content, tag, *args = label
            attrs = dict(args[0]) if args else {}
            body = dict(attrs.get("body", {}))

            body.setdefault("width", label_width(content, tag))
            body.setdefault("height", PIN_LABEL_HEIGHT)
            body.setdefault("corner_radius", PIN_LABEL_CORNER_RADIUS)
            attrs["body"] = body

            output_row.append((content, tag, attrs))

        result.append(output_row)

    return result


# Create a new diagram
diagram = Diagram(DIAGRAM_WIDTH, DIAGRAM_HEIGHT, "diagram")

# Add a stylesheet
diagram.add_stylesheet("styles.css", True)

# Add variable-driven pin-label border styling after styles.css so these
# settings override any generic .pinlabel__body border declarations.
diagram.add(Raw(pin_label_border_style()))

# Create a layout
content = diagram.add(
    Panel(
        width=CONTENT_WIDTH,
        height=CONTENT_HEIGHT,
        inset=(2, 2, 2, 2),
    )
)
panel_main = content.add(
    Panel(
        width=content.inset_width,
        height=MAIN_PANEL_HEIGHT,
        inset=(2, 2, 2, 2),
        tag="panel--main",
    )
)
panel_info = content.add(
    Panel(
        x=0,
        y=panel_main.height,
        width=panel_main.width,
        height=content.inset_height - panel_main.height,
        inset=(2, 2, 2, 2),
        tag="panel--info",
    )
)

# Create a group to hold the pinout-diagram components.
graphic = panel_main.add(Group(GRAPHIC_X, GRAPHIC_Y))

# Add and embed an image
graphic.add(Image("ulx3s.png", width=1372, height=742, embed=True))

# Create pinlabels on J1.
graphic.add(
    PinLabelGroup(
        x=280,
        y=145,
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(-1, 1),
        labels=labels_with_dimensions(data.left_header_even),
    )
)
graphic.add(
    PinLabelGroup(
        x=304,
        y=145,
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(1, 1),
        labels=labels_with_dimensions(data.left_header_odd),
    )
)

# Create pinlabels on J2.  J2 is physically mirrored relative to J1.
graphic.add(
    PinLabelGroup(
        x=1068,
        y=145,
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(-1, 1),
        labels=labels_with_dimensions(data.right_header_odd),
    )
)
graphic.add(
    PinLabelGroup(
        x=1092,
        y=145,
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(1, 1),
        labels=labels_with_dimensions(data.right_header_even),
    )
)
#
## Create pinlabels on the lower header
#graphic.add(
#    PinLabelGroup(
#        x=65,
#        y=244,
#        scale=(-1, 1),
#        pin_pitch=(30, 0),
#        label_start=(110, 30),
#        label_pitch=(0, 30),
#        labels=data.lower_header,
#        leaderline=lline.Curved(direction="vh"),
#    )
#)
#
## Create a title and a text-block
#title_block = panel_info.add(
#    TextBlock(
#        data.title,
#        x=20,
#        y=30,
#        line_height=18,
#        tag="panel title_block",
#    )
#)
#panel_info.add(
#    TextBlock(
#        data.description,
#        x=20,
#        y=60,
#        width=title_block.width,
#        height=panel_info.height - title_block.height,
#        line_height=18,
#        tag="panel text_block",
#    )
#)
#
# Create a legend
legend = panel_info.add(
    Legend(
        data.legend,
        x=LEGEND_X,
        y=LEGEND_Y,
        max_height=LEGEND_MAX_HEIGHT,
    )
)
#
# Export the diagram via commandline:
# >>> python3 -m pinout.manager --export pinout_ulx3s.py pinout_ulx3s.svg --overwrite
