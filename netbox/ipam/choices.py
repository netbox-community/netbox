from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet


class IPAddressFamilyChoices(ChoiceSet):

    FAMILY_4 = 4
    FAMILY_6 = 6

    CHOICES = (
        Choice(FAMILY_4, 'IPv4'),
        Choice(FAMILY_6, 'IPv6'),
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
        Choice(STATUS_CONTAINER, _('Container'), color='gray', description=_('Organizes a set of child prefixes')),
        Choice(STATUS_ACTIVE, _('Active'), color='blue', description=_('Provisioned and in use')),
        Choice(STATUS_RESERVED, _('Reserved'), color='cyan', description=_('Designated for future use')),
        Choice(STATUS_DEPRECATED, _('Deprecated'), color='red', description=_('No longer in use')),
    ]


class PrefixClassificationChoices(ChoiceSet):

    CLASSIFICATION_PUBLIC = 'public'
    CLASSIFICATION_PRIVATE = 'private'
    CLASSIFICATION_SHARED = 'shared'
    CLASSIFICATION_LOOPBACK = 'loopback'
    CLASSIFICATION_LINK_LOCAL = 'link-local'
    CLASSIFICATION_DOCUMENTATION = 'documentation'
    CLASSIFICATION_MULTICAST = 'multicast'
    CLASSIFICATION_BENCHMARKING = 'benchmarking'
    CLASSIFICATION_SPECIAL = 'special'
    CLASSIFICATION_MIXED = 'mixed'

    CHOICES = (
        Choice(
            CLASSIFICATION_PUBLIC,
            _('Public'),
            color='blue',
            description=_('Address space outside the other classifications')
        ),
        Choice(
            CLASSIFICATION_PRIVATE,
            _('Private'),
            color='green',
            description=_('RFC 1918 and unique local address space')
        ),
        Choice(
            CLASSIFICATION_SHARED,
            _('Shared'),
            color='teal',
            description=_('Carrier-grade NAT address space')
        ),
        Choice(
            CLASSIFICATION_LOOPBACK,
            _('Loopback'),
            color='gray',
            description=_('Host loopback addresses')
        ),
        Choice(
            CLASSIFICATION_LINK_LOCAL,
            _('Link-local'),
            color='cyan',
            description=_('Valid only on a single network link')
        ),
        Choice(
            CLASSIFICATION_DOCUMENTATION,
            _('Documentation'),
            color='purple',
            description=_('Reserved for documentation and examples')
        ),
        Choice(
            CLASSIFICATION_MULTICAST,
            _('Multicast'),
            color='indigo',
            description=_('Multicast group addresses')
        ),
        Choice(
            CLASSIFICATION_BENCHMARKING,
            _('Benchmarking'),
            color='pink',
            description=_('Reserved for network benchmark tests')
        ),
        Choice(
            CLASSIFICATION_SPECIAL,
            _('Special-purpose'),
            color='dark',
            description=_('Other reserved or special-purpose space')
        ),
        Choice(
            CLASSIFICATION_MIXED,
            _('Mixed'),
            color='orange',
            description=_('Spans more than one classification')
        ),
    )


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):
    key = 'IPRange.status'

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        Choice(STATUS_ACTIVE, _('Active'), color='blue', description=_('Provisioned and in use')),
        Choice(STATUS_RESERVED, _('Reserved'), color='cyan', description=_('Designated for future use')),
        Choice(STATUS_DEPRECATED, _('Deprecated'), color='red', description=_('No longer in use')),
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
        Choice(STATUS_ACTIVE, _('Active'), color='blue', description=_('Provisioned and in use')),
        Choice(STATUS_RESERVED, _('Reserved'), color='cyan', description=_('Designated for future use')),
        Choice(STATUS_DEPRECATED, _('Deprecated'), color='red', description=_('No longer in use')),
        Choice(STATUS_DHCP, _('DHCP'), color='purple', description=_('Assigned dynamically via DHCP')),
        Choice(
            STATUS_SLAAC,
            _('SLAAC'),
            color='purple',
            description=_('Assigned via IPv6 stateless address autoconfiguration')
        ),
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
        Choice(ROLE_LOOPBACK, _('Loopback'), color='gray', description=_('A loopback interface address')),
        Choice(ROLE_SECONDARY, _('Secondary'), color='blue', description=_('A secondary address on an interface')),
        Choice(ROLE_ANYCAST, _('Anycast'), color='yellow', description=_('An address shared among multiple nodes')),
        Choice(ROLE_VIP, 'VIP', color='purple', description=_('A virtual IP address')),
        Choice(ROLE_VRRP, 'VRRP', color='green', description=_('A virtual address managed by VRRP')),
        Choice(ROLE_HSRP, 'HSRP', color='green', description=_('A virtual address managed by HSRP')),
        Choice(ROLE_GLBP, 'GLBP', color='green', description=_('A virtual address managed by GLBP')),
        Choice(ROLE_CARP, 'CARP', color='green', description=_('A virtual address managed by CARP')),
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
            Choice(PROTOCOL_VRRP2, 'VRRPv2', description=_('Virtual Router Redundancy Protocol version 2')),
            Choice(PROTOCOL_VRRP3, 'VRRPv3', description=_('Virtual Router Redundancy Protocol version 3')),
            Choice(PROTOCOL_CARP, 'CARP', description=_('Common Address Redundancy Protocol')),
        )),
        (_('CheckPoint'), (
            Choice(PROTOCOL_CLUSTERXL, 'ClusterXL', description=_('Check Point ClusterXL high-availability protocol')),
        )),
        (_('Cisco'), (
            Choice(PROTOCOL_HSRP, 'HSRP', description=_('Hot Standby Router Protocol')),
            Choice(PROTOCOL_GLBP, 'GLBP', description=_('Gateway Load Balancing Protocol')),
        )),
        Choice(PROTOCOL_OTHER, 'Other'),
    )


class FHRPGroupAuthTypeChoices(ChoiceSet):

    AUTHENTICATION_PLAINTEXT = 'plaintext'
    AUTHENTICATION_MD5 = 'md5'

    CHOICES = (
        Choice(AUTHENTICATION_PLAINTEXT, _('Plaintext'), description=_('Authentication using a cleartext password')),
        Choice(AUTHENTICATION_MD5, 'MD5', description=_('Authentication using an MD5 hash')),
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
        Choice(STATUS_ACTIVE, _('Active'), color='blue', description=_('Provisioned and in use')),
        Choice(STATUS_RESERVED, _('Reserved'), color='cyan', description=_('Designated for future use')),
        Choice(STATUS_DEPRECATED, _('Deprecated'), color='red', description=_('No longer in use')),
    ]


class VLANQinQRoleChoices(ChoiceSet):

    ROLE_SERVICE = 'svlan'
    ROLE_CUSTOMER = 'cvlan'

    CHOICES = [
        Choice(ROLE_SERVICE, _('Service'), color='blue', description=_('An outer service VLAN (S-VLAN)')),
        Choice(ROLE_CUSTOMER, _('Customer'), color='orange', description=_('An inner customer VLAN (C-VLAN)')),
    ]


#
# Services
#

class ServiceProtocolChoices(ChoiceSet):

    PROTOCOL_TCP = 'tcp'
    PROTOCOL_UDP = 'udp'
    PROTOCOL_SCTP = 'sctp'

    CHOICES = (
        Choice(PROTOCOL_TCP, 'TCP'),
        Choice(PROTOCOL_UDP, 'UDP'),
        Choice(PROTOCOL_SCTP, 'SCTP'),
    )
