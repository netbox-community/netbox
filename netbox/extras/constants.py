from __future__ import unicode_literals


# Models which support custom fields
CUSTOMFIELD_MODELS = (
    'site', 'rack', 'devicetype', 'device',                 # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf',      # IPAM
    'provider', 'circuit',                                  # Circuits
    'tenant',                                               # Tenants
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
    'site', 'region', 'rack', 'device',                                             # DCIM
    'consoleport', 'powerport', 'interfaceconnection',                              # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan',                                     # IPAM
    'provider', 'circuit',                                                          # Circuits
    'tenant',                                                                       # Tenants
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
