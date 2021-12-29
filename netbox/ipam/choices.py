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
        (STATUS_CONTAINER, 'Container', 'gray'),
        (STATUS_ACTIVE, 'Active', 'blue'),
        (STATUS_RESERVED, 'Reserved', 'cyan'),
        (STATUS_DEPRECATED, 'Deprecated', 'red'),
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
        (STATUS_ACTIVE, 'Active', 'blue'),
        (STATUS_RESERVED, 'Reserved', 'cyan'),
        (STATUS_DEPRECATED, 'Deprecated', 'red'),
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
        (STATUS_ACTIVE, 'Active', 'blue'),
        (STATUS_RESERVED, 'Reserved', 'cyan'),
        (STATUS_DEPRECATED, 'Deprecated', 'red'),
        (STATUS_DHCP, 'DHCP', 'green'),
        (STATUS_SLAAC, 'SLAAC', 'purple'),
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
        (ROLE_LOOPBACK, 'Loopback', 'gray'),
        (ROLE_SECONDARY, 'Secondary', 'blue'),
        (ROLE_ANYCAST, 'Anycast', 'yellow'),
        (ROLE_VIP, 'VIP', 'purple'),
        (ROLE_VRRP, 'VRRP', 'green'),
        (ROLE_HSRP, 'HSRP', 'green'),
        (ROLE_GLBP, 'GLBP', 'green'),
        (ROLE_CARP, 'CARP'), 'green',
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
        (STATUS_ACTIVE, 'Active', 'blue'),
        (STATUS_RESERVED, 'Reserved', 'cyan'),
        (STATUS_DEPRECATED, 'Deprecated', 'red'),
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
