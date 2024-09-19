from django.db.models import Q

from .choices import InterfaceTypeChoices

# Exclude SVG images (unsupported by PIL)
DEVICETYPE_IMAGE_FORMATS = 'image/bmp,image/gif,image/jpeg,image/png,image/tiff,image/webp'


#
# Racks
#

RACK_U_HEIGHT_DEFAULT = 42
RACK_U_HEIGHT_MAX = 100

RACK_ELEVATION_BORDER_WIDTH = 2
RACK_ELEVATION_DEFAULT_LEGEND_WIDTH = 30
RACK_ELEVATION_DEFAULT_MARGIN_WIDTH = 15

RACK_STARTING_UNIT_DEFAULT = 1


#
# RearPorts
#

REARPORT_POSITIONS_MIN = 1
REARPORT_POSITIONS_MAX = 1024


#
# Interfaces
#

INTERFACE_MTU_MIN = 1
INTERFACE_MTU_MAX = 65536

VIRTUAL_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_VIRTUAL,
    InterfaceTypeChoices.TYPE_LAG,
    InterfaceTypeChoices.TYPE_BRIDGE,
]

WIRELESS_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_80211A,
    InterfaceTypeChoices.TYPE_80211G,
    InterfaceTypeChoices.TYPE_80211N,
    InterfaceTypeChoices.TYPE_80211AC,
    InterfaceTypeChoices.TYPE_80211AD,
    InterfaceTypeChoices.TYPE_80211AX,
    InterfaceTypeChoices.TYPE_80211AY,
    InterfaceTypeChoices.TYPE_80211BE,
    InterfaceTypeChoices.TYPE_802151,
    InterfaceTypeChoices.TYPE_802154,
    InterfaceTypeChoices.TYPE_OTHER_WIRELESS,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES


#
# Device components
#

MODULE_TOKEN = '{module}'

MODULAR_COMPONENT_TEMPLATE_MODELS = Q(
    app_label='dcim',
    model__in=(
        'consoleporttemplate',
        'consoleserverporttemplate',
        'frontporttemplate',
        'interfacetemplate',
        'poweroutlettemplate',
        'powerporttemplate',
        'rearporttemplate',
    ))

MODULAR_COMPONENT_MODELS = Q(
    app_label='dcim',
    model__in=(
        'consoleport',
        'consoleserverport',
        'frontport',
        'interface',
        'poweroutlet',
        'powerport',
        'rearport',
    ))


#
# Cabling and connections
#

CABLE_TRACE_SVG_DEFAULT_WIDTH = 400

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
    'circuittermination': ['interface', 'frontport', 'rearport', 'circuittermination'],
    'consoleport': ['consoleserverport', 'frontport', 'rearport'],
    'consoleserverport': ['consoleport', 'frontport', 'rearport'],
    'interface': ['interface', 'circuittermination', 'frontport', 'rearport'],
    'frontport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
    'powerfeed': ['powerport'],
    'poweroutlet': ['powerport'],
    'powerport': ['poweroutlet', 'powerfeed'],
    'rearport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
}
