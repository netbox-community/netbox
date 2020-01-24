from .choices import IPAddressRoleChoices

# BGP ASN bounds
BGP_ASN_MIN = 1
BGP_ASN_MAX = 2**32 - 1


#
# VRFs
#

VRF_RD_MAX_LENGTH = 21


#
# Prefixes
#

PREFIX_LENGTH_MIN = 1
PREFIX_LENGTH_MAX = 127  # IPv6


#
# IPAddresses
#

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
# VLANs
#

VLAN_VID_MIN = 1
VLAN_VID_MAX = 4094


#
# Services
#

SERVICE_PORT_MIN = 1
SERVICE_PORT_MAX = 65535
