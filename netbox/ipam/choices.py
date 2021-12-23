from utilities.choices import ChoiceSet


class IPAddressFamilyChoices(ChoiceSet):

    FAMILY_4 = 4
    FAMILY_6 = 6

    CHOICES = (
        (FAMILY_4, 'IPv4'),
        (FAMILY_6, 'IPv6'),
    )


#
# Prefixes
#

class PrefixStatusChoices(ChoiceSet):
    key = 'ipam.Prefix.status'

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_CONTAINER, 'Container', 'secondary'),
        (STATUS_ACTIVE, 'Active', 'primary'),
        (STATUS_RESERVED, 'Reserved', 'info'),
        (STATUS_DEPRECATED, 'Deprecated', 'danger'),
    ]


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):
    key = 'ipam.IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, 'Active', 'primary'),
        (STATUS_RESERVED, 'Reserved', 'info'),
        (STATUS_DEPRECATED, 'Deprecated', 'danger'),
    ]


#
# IP Addresses
#

class IPAddressStatusChoices(ChoiceSet):
    key = 'ipam.IPAddress.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'

    CHOICES = [
        (STATUS_ACTIVE, 'Active', 'primary'),
        (STATUS_RESERVED, 'Reserved', 'info'),
        (STATUS_DEPRECATED, 'Deprecated', 'danger'),
        (STATUS_DHCP, 'DHCP', 'success'),
        (STATUS_SLAAC, 'SLAAC', 'success'),
    ]


class IPAddressRoleChoices(ChoiceSet):

    ROLE_LOOPBACK = 'loopback'
    ROLE_SECONDARY = 'secondary'
    ROLE_ANYCAST = 'anycast'
    ROLE_VIP = 'vip'
    ROLE_VRRP = 'vrrp'
    ROLE_HSRP = 'hsrp'
    ROLE_GLBP = 'glbp'
    ROLE_CARP = 'carp'

    CHOICES = (
        (ROLE_LOOPBACK, 'Loopback', 'secondary'),
        (ROLE_SECONDARY, 'Secondary', 'primary'),
        (ROLE_ANYCAST, 'Anycast', 'warning'),
        (ROLE_VIP, 'VIP'),
        (ROLE_VRRP, 'VRRP', 'success'),
        (ROLE_HSRP, 'HSRP', 'success'),
        (ROLE_GLBP, 'GLBP', 'success'),
        (ROLE_CARP, 'CARP'), 'success',
    )


#
# FHRP
#

class FHRPGroupProtocolChoices(ChoiceSet):

    PROTOCOL_VRRP2 = 'vrrp2'
    PROTOCOL_VRRP3 = 'vrrp3'
    PROTOCOL_HSRP = 'hsrp'
    PROTOCOL_GLBP = 'glbp'
    PROTOCOL_CARP = 'carp'
    PROTOCOL_OTHER = 'other'

    CHOICES = (
        (PROTOCOL_VRRP2, 'VRRPv2'),
        (PROTOCOL_VRRP3, 'VRRPv3'),
        (PROTOCOL_HSRP, 'HSRP'),
        (PROTOCOL_GLBP, 'GLBP'),
        (PROTOCOL_CARP, 'CARP'),
        (PROTOCOL_OTHER, 'Other'),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        (AUTHENTICATION_PLAINTEXT, 'Plaintext'),
        (AUTHENTICATION_MD5, 'MD5'),
    )


#
# VLANs
#

class VLANStatusChoices(ChoiceSet):
    key = 'ipam.VLAN.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, 'Active', 'primary'),
        (STATUS_RESERVED, 'Reserved', 'info'),
        (STATUS_DEPRECATED, 'Deprecated', 'danger'),
    ]


#
# Services
#

class ServiceProtocolChoices(ChoiceSet):

    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'

    CHOICES = (
        (PROTOCOL_TCP, 'TCP'),
        (PROTOCOL_UDP, 'UDP'),
    )
