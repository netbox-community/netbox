from django.db.models import Q


# Models which support custom fields
CUSTOMFIELD_MODELS = Q(
    Q(app_label='circuits', model__in=[
        'circuit',
        'provider',
    ]) |
    Q(app_label='dcim', model__in=[
        'device',
        'devicetype',
        'powerfeed',
        'rack',
        'site',
    ]) |
    Q(app_label='ipam', model__in=[
        'aggregate',
        'ipaddress',
        'prefix',
        'service',
        'vlan',
        'vrf',
    ]) |
    Q(app_label='secrets', model__in=[
        'secret',
    ]) |
    Q(app_label='tenancy', model__in=[
        'tenant',
    ]) |
    Q(app_label='virtualization', model__in=[
        'cluster',
        'virtualmachine',
    ])
)

# Custom links
CUSTOMLINK_MODELS = Q(
    Q(app_label='circuits', model__in=[
        'circuit',
        'provider',
    ]) |
    Q(app_label='dcim', model__in=[
        'cable',
        'device',
        'devicetype',
        'powerpanel',
        'powerfeed',
        'rack',
        'site',
    ]) |
    Q(app_label='ipam', model__in=[
        'aggregate',
        'ipaddress',
        'prefix',
        'service',
        'vlan',
        'vrf',
    ]) |
    Q(app_label='secrets', model__in=[
        'secret',
    ]) |
    Q(app_label='tenancy', model__in=[
        'tenant',
    ]) |
    Q(app_label='virtualization', model__in=[
        'cluster',
        'virtualmachine',
    ])
)

# Models which can have Graphs associated with them
GRAPH_MODELS = Q(
    Q(app_label='circuits', model__in=[
        'provider',
    ]) |
    Q(app_label='dcim', model__in=[
        'device',
        'interface',
        'site',
    ])
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
