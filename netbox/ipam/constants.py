from django.db.models import Q

from .choices import FHRPGroupProtocolChoices, IPAddressRoleChoices, PrefixClassificationChoices

#
# VRFs
#

# Per RFC 4364 section 4.2, a route distinguisher may be encoded as one of the following:
#   * Type 0 (16-bit AS number : 32-bit integer)
#   * Type 1 (32-bit IPv4 address : 16-bit integer)
#   * Type 2 (32-bit AS number : 16-bit integer)
# 21 characters are sufficient to convey the longest possible string value (255.255.255.255:65535)
# Also used for RouteTargets
VRF_RD_MAX_LENGTH = 21


#
# Prefixes
#

PREFIX_LENGTH_MIN = 1
PREFIX_LENGTH_MAX = 127  # IPv6

# Address space by classification per the IANA registries. Named classes and public exceptions override the special
# ranges enclosing them, and any change needs a migration which drops and re-adds Prefix.classification.
PREFIX_CLASSIFICATION_NETWORKS = {
    PrefixClassificationChoices.CLASSIFICATION_PRIVATE: (
        '10.0.0.0/8',  # RFC 1918
        '172.16.0.0/12',  # RFC 1918
        '192.168.0.0/16',  # RFC 1918
        'fc00::/7',  # RFC 4193
    ),
    PrefixClassificationChoices.CLASSIFICATION_SHARED: (
        '100.64.0.0/10',  # RFC 6598
    ),
    PrefixClassificationChoices.CLASSIFICATION_LOOPBACK: (
        '127.0.0.0/8',  # RFC 1122
        '::1/128',  # RFC 4291
    ),
    PrefixClassificationChoices.CLASSIFICATION_LINK_LOCAL: (
        '169.254.0.0/16',  # RFC 3927
        'fe80::/10',  # RFC 4291
    ),
    PrefixClassificationChoices.CLASSIFICATION_DOCUMENTATION: (
        '192.0.2.0/24',  # RFC 5737
        '198.51.100.0/24',  # RFC 5737
        '203.0.113.0/24',  # RFC 5737
        '2001:db8::/32',  # RFC 3849
        '3fff::/20',  # RFC 9637
    ),
    PrefixClassificationChoices.CLASSIFICATION_MULTICAST: (
        '224.0.0.0/4',  # RFC 5771
        'ff00::/8',  # RFC 4291
    ),
    PrefixClassificationChoices.CLASSIFICATION_BENCHMARKING: (
        '198.18.0.0/15',  # RFC 2544
        '2001:2::/48',  # RFC 5180
    ),
    PrefixClassificationChoices.CLASSIFICATION_SPECIAL: (
        '0.0.0.0/8',  # RFC 791
        '192.0.0.0/24',  # RFC 6890
        '192.88.99.0/24',  # RFC 7526
        '240.0.0.0/4',  # RFC 1112
        '::/8', '100::/8', '200::/7', '400::/6', '800::/5', '1000::/4',  # Reserved by IETF
        '2001::/23',  # RFC 2928
        '2002::/16',  # RFC 3056
        '4000::/3', '6000::/3', '8000::/3', 'a000::/3', 'c000::/3',  # Reserved by IETF
        'e000::/4', 'f000::/5', 'f800::/6', 'fe00::/9',  # Reserved by IETF
        'fec0::/10',  # RFC 3879
    ),
}

# Globally reachable blocks within special-purpose space
PREFIX_CLASSIFICATION_PUBLIC_EXCEPTIONS = (
    '192.0.0.9/32',  # RFC 7723
    '192.0.0.10/32',  # RFC 8155
    '64:ff9b::/96',  # RFC 6052
    '2001:1::1/128',  # RFC 7723
    '2001:1::2/128',  # RFC 8155
    '2001:1::3/128',  # RFC 9665
    '2001:3::/32',  # RFC 7450
    '2001:4:112::/48',  # RFC 7535
    '2001:20::/28',  # RFC 7343
    '2001:30::/28',  # RFC 9374
)


#
# IPAddresses
#

IPADDRESS_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='interface') |
    Q(app_label='ipam', model='fhrpgroup') |
    Q(app_label='virtualization', model='vminterface')
)

IPADDRESS_MASK_LENGTH_MIN = 1
IPADDRESS_MASK_LENGTH_MAX = 128  # IPv6

IPADDRESS_ROLES_NONUNIQUE = (
    # IPAddress roles which are exempt from unique address enforcement
    IPAddressRoleChoices.ROLE_ANYCAST,
    IPAddressRoleChoices.ROLE_VIP,
    IPAddressRoleChoices.ROLE_VRRP,
    IPAddressRoleChoices.ROLE_HSRP,
    IPAddressRoleChoices.ROLE_GLBP,
    IPAddressRoleChoices.ROLE_CARP,
)


#
# FHRP groups
#

FHRPGROUPASSIGNMENT_PRIORITY_MIN = 0
FHRPGROUPASSIGNMENT_PRIORITY_MAX = 255

FHRP_PROTOCOL_ROLE_MAPPINGS = {
    FHRPGroupProtocolChoices.PROTOCOL_VRRP2: IPAddressRoleChoices.ROLE_VRRP,
    FHRPGroupProtocolChoices.PROTOCOL_VRRP3: IPAddressRoleChoices.ROLE_VRRP,
    FHRPGroupProtocolChoices.PROTOCOL_HSRP: IPAddressRoleChoices.ROLE_HSRP,
    FHRPGroupProtocolChoices.PROTOCOL_GLBP: IPAddressRoleChoices.ROLE_GLBP,
    FHRPGroupProtocolChoices.PROTOCOL_CARP: IPAddressRoleChoices.ROLE_CARP,
    FHRPGroupProtocolChoices.PROTOCOL_OTHER: IPAddressRoleChoices.ROLE_VIP,
}


#
# VLANs
#

# 12-bit VLAN ID (values 0 and 4095 are reserved)
VLAN_VID_MIN = 1
VLAN_VID_MAX = 4094

# models values for ContentTypes which may be VLANGroup scope types
VLANGROUP_SCOPE_TYPES = (
    'region', 'sitegroup', 'site', 'location', 'rackgroup', 'rack', 'clustergroup', 'cluster',
)


#
# Services
#

SERVICE_ASSIGNMENT_MODELS = Q(
    Q(app_label='dcim', model='device') |
    Q(app_label='ipam', model='fhrpgroup') |
    Q(app_label='virtualization', model='virtualmachine')
)

# 16-bit port number
SERVICE_PORT_MIN = 1
SERVICE_PORT_MAX = 65535
