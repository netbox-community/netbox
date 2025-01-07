from enum import Enum
import strawberry

__all__ = [
    'IPAddressFamilyEnum',
    'PrefixStatusEnum',
    'IPRangeStatusEnum',
    'IPAddressStatusEnum',
    'IPAddressRoleEnum',
    'FHRPGroupProtocolEnum',
    'FHRPGroupAuthTypeEnum',
    'VLANStatusEnum',
    'VLANQinQRoleEnum',
    'ServiceProtocolEnum',
]


@strawberry.enum
class IPAddressFamilyEnum(Enum):
    FAMILY_4 = 4
    FAMILY_6 = 6


#
# Prefixes
#


@strawberry.enum
class PrefixStatusEnum(Enum):
    key = 'Prefix.status'

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'


#
# IP Ranges
#


@strawberry.enum
class IPRangeStatusEnum(Enum):
    key = 'IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'


#
# IP Addresses
#


@strawberry.enum
class IPAddressStatusEnum(Enum):
    key = 'IPAddress.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'


@strawberry.enum
class IPAddressRoleEnum(Enum):
    ROLE_LOOPBACK = 'loopback'
    ROLE_SECONDARY = 'secondary'
    ROLE_ANYCAST = 'anycast'
    ROLE_VIP = 'vip'
    ROLE_VRRP = 'vrrp'
    ROLE_HSRP = 'hsrp'
    ROLE_GLBP = 'glbp'
    ROLE_CARP = 'carp'


#
# FHRP
#


@strawberry.enum
class FHRPGroupProtocolEnum(Enum):
    PROTOCOL_VRRP2 = 'vrrp2'
    PROTOCOL_VRRP3 = 'vrrp3'
    PROTOCOL_HSRP = 'hsrp'
    PROTOCOL_GLBP = 'glbp'
    PROTOCOL_CARP = 'carp'
    PROTOCOL_CLUSTERXL = 'clusterxl'
    PROTOCOL_OTHER = 'other'


@strawberry.enum
class FHRPGroupAuthTypeEnum(Enum):
    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'


#
# VLANs
#


@strawberry.enum
class VLANStatusEnum(Enum):
    key = 'VLAN.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'


@strawberry.enum
class VLANQinQRoleEnum(Enum):
    ROLE_SERVICE = 'svlan'
    ROLE_CUSTOMER = 'cvlan'


#
# Services
#


@strawberry.enum
class ServiceProtocolEnum(Enum):
    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_SCTP = 'sctp'
