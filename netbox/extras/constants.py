
# Models which support custom fields
CUSTOMFIELD_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.device',
    'dcim.devicetype',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.site',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

# Custom field types
CF_TYPE_TEXT = 100
CF_TYPE_INTEGER = 200
CF_TYPE_BOOLEAN = 300
CF_TYPE_DATE = 400
CF_TYPE_URL = 500
CF_TYPE_SELECT = 600
CUSTOMFIELD_TYPE_CHOICES = (
    (CF_TYPE_TEXT, 'Text'),
    (CF_TYPE_INTEGER, 'Integer'),
    (CF_TYPE_BOOLEAN, 'Boolean (true/false)'),
    (CF_TYPE_DATE, 'Date'),
    (CF_TYPE_URL, 'URL'),
    (CF_TYPE_SELECT, 'Selection'),
)

# Custom field filter logic choices
CF_FILTER_DISABLED = 0
CF_FILTER_LOOSE = 1
CF_FILTER_EXACT = 2
CF_FILTER_CHOICES = (
    (CF_FILTER_DISABLED, 'Disabled'),
    (CF_FILTER_LOOSE, 'Loose'),
    (CF_FILTER_EXACT, 'Exact'),
)

# Custom links
CUSTOMLINK_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.device',
    'dcim.devicetype',
    'dcim.powerpanel',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.site',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

BUTTON_CLASS_DEFAULT = 'default'
BUTTON_CLASS_PRIMARY = 'primary'
BUTTON_CLASS_SUCCESS = 'success'
BUTTON_CLASS_INFO = 'info'
BUTTON_CLASS_WARNING = 'warning'
BUTTON_CLASS_DANGER = 'danger'
BUTTON_CLASS_LINK = 'link'
BUTTON_CLASS_CHOICES = (
    (BUTTON_CLASS_DEFAULT, 'Default'),
    (BUTTON_CLASS_PRIMARY, 'Primary (blue)'),
    (BUTTON_CLASS_SUCCESS, 'Success (green)'),
    (BUTTON_CLASS_INFO, 'Info (aqua)'),
    (BUTTON_CLASS_WARNING, 'Warning (orange)'),
    (BUTTON_CLASS_DANGER, 'Danger (red)'),
    (BUTTON_CLASS_LINK, 'None (link)'),
)

# Graph types
GRAPH_TYPE_INTERFACE = 100
GRAPH_TYPE_DEVICE = 150
GRAPH_TYPE_PROVIDER = 200
GRAPH_TYPE_SITE = 300
GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_INTERFACE, 'Interface'),
    (GRAPH_TYPE_DEVICE, 'Device'),
    (GRAPH_TYPE_PROVIDER, 'Provider'),
    (GRAPH_TYPE_SITE, 'Site'),
)

# Models which support export templates
EXPORTTEMPLATE_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.consoleport',
    'dcim.device',
    'dcim.devicetype',
    'dcim.interface',
    'dcim.manufacturer',
    'dcim.powerpanel',
    'dcim.powerport',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.rackgroup',
    'dcim.region',
    'dcim.site',
    'dcim.virtualchassis',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

# ExportTemplate language choices
TEMPLATE_LANGUAGE_DJANGO = 10
TEMPLATE_LANGUAGE_JINJA2 = 20
TEMPLATE_LANGUAGE_CHOICES = (
    (TEMPLATE_LANGUAGE_DJANGO, 'Django'),
    (TEMPLATE_LANGUAGE_JINJA2, 'Jinja2'),
)

# Topology map types
TOPOLOGYMAP_TYPE_NETWORK = 1
TOPOLOGYMAP_TYPE_CONSOLE = 2
TOPOLOGYMAP_TYPE_POWER = 3
TOPOLOGYMAP_TYPE_CHOICES = (
    (TOPOLOGYMAP_TYPE_NETWORK, 'Network'),
    (TOPOLOGYMAP_TYPE_CONSOLE, 'Console'),
    (TOPOLOGYMAP_TYPE_POWER, 'Power'),
)

# Change log actions
OBJECTCHANGE_ACTION_CREATE = 1
OBJECTCHANGE_ACTION_UPDATE = 2
OBJECTCHANGE_ACTION_DELETE = 3
OBJECTCHANGE_ACTION_CHOICES = (
    (OBJECTCHANGE_ACTION_CREATE, 'Created'),
    (OBJECTCHANGE_ACTION_UPDATE, 'Updated'),
    (OBJECTCHANGE_ACTION_DELETE, 'Deleted'),
)

# User action types
ACTION_CREATE = 1
ACTION_IMPORT = 2
ACTION_EDIT = 3
ACTION_BULK_EDIT = 4
ACTION_DELETE = 5
ACTION_BULK_DELETE = 6
ACTION_BULK_CREATE = 7
ACTION_CHOICES = (
    (ACTION_CREATE, 'created'),
    (ACTION_BULK_CREATE, 'bulk created'),
    (ACTION_IMPORT, 'imported'),
    (ACTION_EDIT, 'modified'),
    (ACTION_BULK_EDIT, 'bulk edited'),
    (ACTION_DELETE, 'deleted'),
    (ACTION_BULK_DELETE, 'bulk deleted'),
)

# Report logging levels
LOG_DEFAULT = 0
LOG_SUCCESS = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_FAILURE = 40
LOG_LEVEL_CODES = {
    LOG_DEFAULT: 'default',
    LOG_SUCCESS: 'success',
    LOG_INFO: 'info',
    LOG_WARNING: 'warning',
    LOG_FAILURE: 'failure',
}

# webhook content types
WEBHOOK_CT_JSON = 1
WEBHOOK_CT_X_WWW_FORM_ENCODED = 2
WEBHOOK_CT_CHOICES = (
    (WEBHOOK_CT_JSON, 'application/json'),
    (WEBHOOK_CT_X_WWW_FORM_ENCODED, 'application/x-www-form-urlencoded'),
)

# Models which support registered webhooks
WEBHOOK_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.consoleport',
    'dcim.consoleserverport',
    'dcim.device',
    'dcim.devicebay',
    'dcim.devicetype',
    'dcim.interface',
    'dcim.inventoryitem',
    'dcim.frontport',
    'dcim.manufacturer',
    'dcim.poweroutlet',
    'dcim.powerpanel',
    'dcim.powerport',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.rearport',
    'dcim.region',
    'dcim.site',
    'dcim.virtualchassis',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]
