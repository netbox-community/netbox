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
# Cables
#

CABLE_CONNECTOR_MIN = 1
CABLE_CONNECTOR_MAX = 256

CABLE_POSITION_MIN = 1
CABLE_POSITION_MAX = 1024


#
# RearPorts
#

PORT_POSITION_MIN = 1
PORT_POSITION_MAX = 1024


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
    InterfaceTypeChoices.TYPE_GSM,
    InterfaceTypeChoices.TYPE_CDMA,
    InterfaceTypeChoices.TYPE_LTE,
    InterfaceTypeChoices.TYPE_4G,
    InterfaceTypeChoices.TYPE_5G,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES


#
# Device components
#

MODULE_TOKEN = '{module}'
MODULE_TOKEN_SEPARATOR = '/'


def resolve_module_token(text, positions):
    """
    Substitute {module} tokens in text with position values.

    Args:
        text: String potentially containing {module} tokens
        positions: List of position strings from the module tree (root to leaf)

    Returns:
        Text with {module} tokens replaced according to these rules:
        - Single token: replaced with full path (positions joined by MODULE_TOKEN_SEPARATOR)
        - Multiple tokens: replaced level-by-level (first token gets first position, etc.)

    This centralizes the substitution logic used by both ModuleCommonForm.clean()
    and ModularComponentTemplateModel.resolve_*() methods.
    """
    if not text or MODULE_TOKEN not in text:
        return text

    token_count = text.count(MODULE_TOKEN)

    if token_count == 1:
        # Single token: substitute with full path (e.g., "1/1" for depth 2)
        full_path = MODULE_TOKEN_SEPARATOR.join(positions)
        return text.replace(MODULE_TOKEN, full_path, 1)
    else:
        # Multiple tokens: substitute level-by-level (existing behavior)
        result = text
        for pos in positions:
            result = result.replace(MODULE_TOKEN, pos, 1)
        return result


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

# Models which can serve to scope an object by location
LOCATION_SCOPE_TYPES = (
    'region', 'sitegroup', 'site', 'location',
)


#
# MAC addresses
#

MACADDRESS_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='interface') |
    Q(app_label='virtualization', model='vminterface')
)
