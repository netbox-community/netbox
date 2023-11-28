from django.utils.translation import gettext_lazy as _

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
    key = 'Prefix.status'

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_CONTAINER, _('Container'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_RESERVED, _('Reserved'), 'cyan'),
        (STATUS_DEPRECATED, _('Deprecated'), 'red'),
    ]


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):
    key = 'IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_RESERVED, _('Reserved'), 'cyan'),
        (STATUS_DEPRECATED, _('Deprecated'), 'red'),
    ]


#
# IP Addresses
#

class IPAddressStatusChoices(ChoiceSet):
    key = 'IPAddress.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'

    CHOICES = [
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_RESERVED, _('Reserved'), 'cyan'),
        (STATUS_DEPRECATED, _('Deprecated'), 'red'),
        (STATUS_DHCP, _('DHCP'), 'green'),
        (STATUS_SLAAC, _('SLAAC'), 'purple'),
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
        (ROLE_LOOPBACK, _('Loopback'), 'gray'),
        (ROLE_SECONDARY, _('Secondary'), 'blue'),
        (ROLE_ANYCAST, _('Anycast'), 'yellow'),
        (ROLE_VIP, 'VIP', 'purple'),
        (ROLE_VRRP, 'VRRP', 'green'),
        (ROLE_HSRP, 'HSRP', 'green'),
        (ROLE_GLBP, 'GLBP', 'green'),
        (ROLE_CARP, 'CARP', 'green'),
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
    PROTOCOL_CLUSTERXL = 'clusterxl'
    PROTOCOL_OTHER = 'other'

    CHOICES = (
        (_('Standard'), (
            (PROTOCOL_VRRP2, 'VRRPv2'),
            (PROTOCOL_VRRP3, 'VRRPv3'),
            (PROTOCOL_CARP, 'CARP'),
        )),
        (_('CheckPoint'), (
            (PROTOCOL_CLUSTERXL, 'ClusterXL'),
        )),
        (_('Cisco'), (
            (PROTOCOL_HSRP, 'HSRP'),
            (PROTOCOL_GLBP, 'GLBP'),
        )),
        (PROTOCOL_OTHER, 'Other'),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        (AUTHENTICATION_PLAINTEXT, _('Plaintext')),
        (AUTHENTICATION_MD5, 'MD5'),
    )


#
# VLANs
#

class VLANStatusChoices(ChoiceSet):
    key = 'VLAN.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_RESERVED, _('Reserved'), 'cyan'),
        (STATUS_DEPRECATED, _('Deprecated'), 'red'),
    ]


#
# Services
#

class ServiceProtocolChoices(ChoiceSet):

    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_SCTP = 'sctp'

    CHOICES = (
        (PROTOCOL_TCP, 'TCP'),
        (PROTOCOL_UDP, 'UDP'),
        (PROTOCOL_SCTP, 'SCTP'),
    )
