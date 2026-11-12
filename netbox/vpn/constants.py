from django.db.models import Q

L2VPN_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='interface') |
    Q(app_label='ipam', model='ipaddress') |
    Q(app_label='ipam', model='vlan') |
    Q(app_label='virtualization', model='vminterface')
)

# Models which may terminate more than one L2VPN (e.g. an IP address which is the far-end PE of several pseudowires)
L2VPN_MULTI_TERMINATION_MODELS = (
    'ipam.ipaddress',
)
