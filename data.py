legend = [
    ("GP single-ended", "gpsingle" ),
    ("GN single-ended", "gnsingle"),
    ("FPGA site","site"),
    ("Analog", "analog"),
    ("Communication", "comms"),
    ("Ground", "gnd"),
    ("GPIO", "gpio"),
    ("Touch", "touch"),
    ("Power", "pwr"),
    ("PWM", "pwm"),
]

# Pinlabels

left_header_even = [
    [
        ("2", "pwr"),
    ],
    [
        ("4", "gnd"),
    ],
    [
        ("6", "gpio"),
        ("GP0", "gpsingle"),
    ],
    [
        ("8", "gpio"),
        ("GP1", "gpsingle"),
    ],
    [
        ("10", "gpio"),
        ("GP2", "gpsingle"),
    ],
    [
        ("12", "gpio"),
        ("GP3", "gpsingle"),
    ],
]


left_header_odd = [
    [
        ("1", "pwr"),
    ],
    [
        ("3", "gnd"),
    ],
    [
        ("5", "gpio"),
        ("GN0", "GP-s"),
    ],
    [
        ("7", "gpio"),
        ("GN1", "GP-s"),
    ],
    [
        ("9", "gpio"),
        ("GN2", "GP-s"),
    ],
    [
        ("11", "gpio"),
        ("GN3", "GP-s"),
        ("B11","site")
    ],
]

lower_header = [
    [
        ("3", "gpio"),
        ("PWM", "pwm"),
    ],
    [
        ("4", "gpio"),
        ("A2", "analog"),
        ("TOUCH", "touch"),
    ],
    [
        ("5", "gpio"),
        ("A3", "analog"),
    ],
]

right_header = [
    [
        ("Vcc", "pwr"),
    ],
    [
        ("GND", "gnd"),
    ],
    [
        ("6", "gpio"),
        ("A4", "analog"),
        ("TOUCH", "touch"),
    ],
]


# Text

title = "<tspan class='h1'>ULX3S Pinout</tspan>"

description = """Created with Python tool kit to assist with 
documentation of electronic hardware. 
More info at <tspan class='italic strong'>pinout.readthedocs.io</tspan>"""
