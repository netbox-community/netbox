from django.utils.translation import gettext_lazy as _
from utilities.choices import ChoiceSet


class IPAddressFamilyChoices(ChoiceSet):

    FAMILY_4 = 4
    FAMILY_6 = 6

    CHOICES = (
        (FAMILY_4, _('IPv4')),
        (FAMILY_6, _('IPv6')),
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
        (ROLE_VIP, _('VIP'), 'purple'),
        (ROLE_VRRP, _('VRRP'), 'green'),
        (ROLE_HSRP, _('HSRP'), 'green'),
        (ROLE_GLBP, _('GLBP'), 'green'),
        (ROLE_CARP, _('CARP'), 'green'),
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
            (PROTOCOL_VRRP2, _('VRRPv2')),
            (PROTOCOL_VRRP3, _('VRRPv3')),
            (PROTOCOL_CARP, _('CARP')),
        )),
        (_('CheckPoint'), (
            (PROTOCOL_CLUSTERXL, _('ClusterXL')),
        )),
        (_('Cisco'), (
            (PROTOCOL_HSRP, _('HSRP')),
            (PROTOCOL_GLBP, _('GLBP')),
        )),
        (PROTOCOL_OTHER, _('Other')),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        (AUTHENTICATION_PLAINTEXT, _('Plaintext')),
        (AUTHENTICATION_MD5, _('MD5')),
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
        (PROTOCOL_TCP, _('TCP')),
        (PROTOCOL_UDP, _('UDP')),
        (PROTOCOL_SCTP, _('SCTP')),
    )


class L2VPNTypeChoices(ChoiceSet):
    TYPE_VPLS = 'vpls'
    TYPE_VPWS = 'vpws'
    TYPE_EPL = 'epl'
    TYPE_EVPL = 'evpl'
    TYPE_EPLAN = 'ep-lan'
    TYPE_EVPLAN = 'evp-lan'
    TYPE_EPTREE = 'ep-tree'
    TYPE_EVPTREE = 'evp-tree'
    TYPE_VXLAN = 'vxlan'
    TYPE_VXLAN_EVPN = 'vxlan-evpn'
    TYPE_MPLS_EVPN = 'mpls-evpn'
    TYPE_PBB_EVPN = 'pbb-evpn'

    CHOICES = (
        (_('VPLS'), (
            (TYPE_VPWS, _('VPWS')),
            (TYPE_VPLS, _('VPLS')),
        )),
        (_('VXLAN'), (
            (TYPE_VXLAN, _('VXLAN')),
            (TYPE_VXLAN_EVPN, _('VXLAN-EVPN')),
        )),
        (_('L2VPN E-VPN'), (
            (TYPE_MPLS_EVPN, _('MPLS EVPN')),
            (TYPE_PBB_EVPN, _('PBB EVPN')),
        )),
        (_('E-Line'), (
            (TYPE_EPL, _('EPL')),
            (TYPE_EVPL, _('EVPL')),
        )),
        (_('E-LAN'), (
            (TYPE_EPLAN, _('Ethernet Private LAN')),
            (TYPE_EVPLAN, _('Ethernet Virtual Private LAN')),
        )),
        (_('E-Tree'), (
            (TYPE_EPTREE, _('Ethernet Private Tree')),
            (TYPE_EVPTREE, _('Ethernet Virtual Private Tree')),
        )),
    )

    P2P = (
        TYPE_VPWS,
        TYPE_EPL,
        TYPE_EPLAN,
        TYPE_EPTREE
    )
