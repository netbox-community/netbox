from django.db.models import Q

L2VPN_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='interface') |
    Q(app_label='ipam', model='vlan') |
    Q(app_label='virtualization', model='vminterface')
)
