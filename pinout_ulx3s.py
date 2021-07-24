###########################################
#
# ULX3S based on example script to build a
# pinout diagram. Includes basic
# features and convenience classes.
#
###########################################

from pinout.core import Group, Image
from pinout.components.layout import Diagram, Panel
from pinout.components.pinlabel import PinLabelGroup, PinLabel
from pinout.components.text import TextBlock
from pinout.components import leaderline as lline
from pinout.components.legend import Legend


# Import data for the diagram
import data

# Create a new diagram
diagram = Diagram(2200, 1700, "diagram")

# Add a stylesheet
diagram.add_stylesheet("styles.css", True)

# Create a layout
content = diagram.add(
    Panel(
        width=1852,
        height=1214,
        inset=(2, 2, 2, 2),
    )
)
panel_main = content.add(
    Panel(
        width=content.inset_width,
        height=742,
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
graphic = panel_main.add(Group(1, 1))

# Add and embed an image
graphic.add(Image("./ulx3s.png", width=1372, height=742, embed=True))

# Create a single pin label
graphic.add(
    PinLabel(
        content=(content.inset_height - graphic.height) / 2,
        x=100,
        y=1,
        tag="pwr",
        body={"x": 200, "y": 20, "width": 200, "height": 20},
        leaderline={"direction": "vh"},
    )
)
#
## Create pinlabels on the right header
#graphic.add(
#    PinLabelGroup(
#        x=1372,
#        y=742,
#        pin_pitch=(0, 30),
#        label_start=(60, 0),
#        label_pitch=(0, 30),
#        labels=data.right_header,
#    )
#)
#
# Create pinlabels on the left header
graphic.add(
    PinLabelGroup(
        x=280,
        y=145,
        body={"height": 20},
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(-1, 1),
        labels=data.left_header_even,
    )
)

graphic.add(
    PinLabelGroup(
        x=304,
        y=145,
        body={"height": 20},
        pin_pitch=(0, 22.5),
        label_start=(30, 0),
        label_pitch=(0, 22.5),
        scale=(1, 1),
        labels=data.left_header_odd,
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
        x=340,
        y=8,
        max_height=132,
    )
)
#
# Export the diagram via commandline:
# >>> py -m pinout.manager --export pinout_diagram diagram.svg