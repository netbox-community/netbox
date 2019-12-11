from .choices import InterfaceTypeChoices


#
# Interface type groups
#

VIRTUAL_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_VIRTUAL,
    InterfaceTypeChoices.TYPE_LAG,
]

WIRELESS_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_80211A,
    InterfaceTypeChoices.TYPE_80211G,
    InterfaceTypeChoices.TYPE_80211N,
    InterfaceTypeChoices.TYPE_80211AC,
    InterfaceTypeChoices.TYPE_80211AD,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES

# Console/power/interface connection statuses
CONNECTION_STATUS_PLANNED = False
CONNECTION_STATUS_CONNECTED = True
CONNECTION_STATUS_CHOICES = [
    [CONNECTION_STATUS_PLANNED, 'Planned'],
    [CONNECTION_STATUS_CONNECTED, 'Connected'],
]

# Cable endpoint types
CABLE_TERMINATION_TYPES = [
    'consoleport', 'consoleserverport', 'interface', 'poweroutlet', 'powerport', 'frontport', 'rearport',
    'circuittermination',
]

CABLE_TERMINATION_TYPE_CHOICES = {
    # (API endpoint, human-friendly name)
    'consoleport': ('console-ports', 'Console port'),
    'consoleserverport': ('console-server-ports', 'Console server port'),
    'powerport': ('power-ports', 'Power port'),
    'poweroutlet': ('power-outlets', 'Power outlet'),
    'interface': ('interfaces', 'Interface'),
    'frontport': ('front-ports', 'Front panel port'),
    'rearport': ('rear-ports', 'Rear panel port'),
}

COMPATIBLE_TERMINATION_TYPES = {
    'consoleport': ['consoleserverport', 'frontport', 'rearport'],
    'consoleserverport': ['consoleport', 'frontport', 'rearport'],
    'powerport': ['poweroutlet', 'powerfeed'],
    'poweroutlet': ['powerport'],
    'interface': ['interface', 'circuittermination', 'frontport', 'rearport'],
    'frontport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
    'rearport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
    'circuittermination': ['interface', 'frontport', 'rearport'],
}


RACK_ELEVATION_STYLE = """
* {
    font-family: 'Helvetica Neue';
    font-size: 13px;
}
rect {
    box-sizing: border-box;
}
text {
    text-anchor: middle;
    dominant-baseline: middle;
}
.rack {
    background-color: #f0f0f0;
    fill: none;
    stroke: black;
    stroke-width: 3px;
}
.slot {
    fill: #f7f7f7;
    stroke: #a0a0a0;
}
.slot:hover {
    fill: #fff;
}
.slot+.add-device {
    fill: none;
}
.slot:hover+.add-device {
    fill: blue;
}
.reserved {
    fill: url(#reserved);
}
.reserved:hover {
    fill: url(#reserved);
}
.occupied {
    fill: url(#occupied);
}
.occupied:hover {
    fill: url(#occupied);
}
.blocked {
    fill: url(#blocked);
}
.blocked:hover {
    fill: url(#blocked);
}
.blocked:hover+.add-device {
    fill: none;
}
"""


# Rack Elevation SVG Size
RACK_ELEVATION_UNIT_WIDTH_DEFAULT = 230
RACK_ELEVATION_UNIT_HEIGHT_DEFAULT = 20
