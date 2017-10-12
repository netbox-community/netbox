from __future__ import unicode_literals


# Models which support custom fields
CUSTOMFIELD_MODELS = (
    'provider', 'circuit',                                  # Circuits
    'site', 'rack', 'devicetype', 'device',                 # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf',      # IPAM
    'tenant',                                               # Tenancy
    'cluster', 'virtualmachine',                            # Virtualization
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
    'consoleport', 'powerport', 'interfaceconnection',                              # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan',                                     # IPAM
    'tenant',                                                                       # Tenancy
    'cluster', 'virtualmachine',                                                    # Virtualization
]

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
