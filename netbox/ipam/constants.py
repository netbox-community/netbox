# IP address families
AF_CHOICES = (
    (4, 'IPv4'),
    (6, 'IPv6'),
)

# VLAN statuses
VLAN_STATUS_ACTIVE = 1
VLAN_STATUS_RESERVED = 2
VLAN_STATUS_DEPRECATED = 3
VLAN_STATUS_CHOICES = (
    (VLAN_STATUS_ACTIVE, 'Active'),
    (VLAN_STATUS_RESERVED, 'Reserved'),
    (VLAN_STATUS_DEPRECATED, 'Deprecated')
)

# Bootstrap CSS classes
STATUS_CHOICE_CLASSES = {
    0: 'default',
    1: 'primary',
    2: 'info',
    3: 'danger',
    4: 'warning',
    5: 'success',
}


# IP protocols (for services)
IP_PROTOCOL_TCP = 6
IP_PROTOCOL_UDP = 17
IP_PROTOCOL_CHOICES = (
    (IP_PROTOCOL_TCP, 'TCP'),
    (IP_PROTOCOL_UDP, 'UDP'),
)
