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
    'dcim.inventoryitem',
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
