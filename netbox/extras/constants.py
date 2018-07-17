from __future__ import unicode_literals


# Models which support custom fields
CUSTOMFIELD_MODELS = (
    'provider', 'circuit',                                         # Circuits
    'site', 'rack', 'devicetype', 'device',                        # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service',  # IPAM
    'secret',                                                      # Secrets
    'tenant',                                                      # Tenancy
    'cluster', 'virtualmachine',                                   # Virtualization
)

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

# Graph types
GRAPH_TYPE_INTERFACE = 100
GRAPH_TYPE_PROVIDER = 200
GRAPH_TYPE_SITE = 300
GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_INTERFACE, 'Interface'),
    (GRAPH_TYPE_PROVIDER, 'Provider'),
    (GRAPH_TYPE_SITE, 'Site'),
)

# Models which support export templates
EXPORTTEMPLATE_MODELS = [
    'provider', 'circuit',                                                          # Circuits
    'site', 'region', 'rack', 'rackgroup', 'manufacturer', 'devicetype', 'device',  # DCIM
    'consoleport', 'powerport', 'interfaceconnection', 'virtualchassis',            # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service',                   # IPAM
    'secret',                                                                       # Secrets
    'tenant',                                                                       # Tenancy
    'cluster', 'virtualmachine',                                                    # Virtualization
]

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
WEBHOOK_MODELS = (
    'provider', 'circuit',                                           # Circuits
    'site', 'rack', 'devicetype', 'device', 'virtualchassis',        # DCIM
    'consoleport', 'consoleserverport', 'powerport', 'poweroutlet',
    'interface', 'devicebay', 'inventoryitem',
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service',    # IPAM
    'secret',                                                        # Secrets
    'tenant',                                                        # Tenancy
    'cluster', 'virtualmachine',                                     # Virtualization
)
