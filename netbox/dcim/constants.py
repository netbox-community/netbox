from django.db.models import Q

from .choices import InterfaceTypeChoices


#
# Rack elevation rendering
#

RACK_ELEVATION_UNIT_WIDTH_DEFAULT = 230
RACK_ELEVATION_UNIT_HEIGHT_DEFAULT = 20


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


#
# Cabling and connections
#

# TODO: Replace with CableStatusChoices?
# Console/power/interface connection statuses
CONNECTION_STATUS_PLANNED = False
CONNECTION_STATUS_CONNECTED = True
CONNECTION_STATUS_CHOICES = [
    [CONNECTION_STATUS_PLANNED, 'Planned'],
    [CONNECTION_STATUS_CONNECTED, 'Connected'],
]

# Cable endpoint types
CABLE_TERMINATION_MODELS = Q(
    Q(app_label='circuits', model__in=(
        'circuittermination',
    )) |
    Q(app_label='dcim', model__in=(
        'consoleport',
        'consoleserverport',
        'frontport',
        'interface',
        'powerfeed',
        'poweroutlet',
        'powerport',
        'rearport',
    ))
)

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
