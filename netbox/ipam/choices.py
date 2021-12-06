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

    STATUS_CONTAINER = 'container'
    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_CONTAINER, 'Container'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    CSS_CLASSES = {
        STATUS_CONTAINER: 'secondary',
        STATUS_ACTIVE: 'primary',
        STATUS_RESERVED: 'info',
        STATUS_DEPRECATED: 'danger',
    }


#
# IP Ranges
#

class IPRangeStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    CSS_CLASSES = {
        STATUS_ACTIVE: 'primary',
        STATUS_RESERVED: 'info',
        STATUS_DEPRECATED: 'danger',
    }


#
# IP Addresses
#

class IPAddressStatusChoices(ChoiceSet):

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'
    STATUS_DHCP = 'dhcp'
    STATUS_SLAAC = 'slaac'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
        (STATUS_DHCP, 'DHCP'),
        (STATUS_SLAAC, 'SLAAC'),
    )

    CSS_CLASSES = {
        STATUS_ACTIVE: 'primary',
        STATUS_RESERVED: 'info',
        STATUS_DEPRECATED: 'danger',
        STATUS_DHCP: 'success',
        STATUS_SLAAC: 'success',
    }


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
        (ROLE_LOOPBACK, 'Loopback'),
        (ROLE_SECONDARY, 'Secondary'),
        (ROLE_ANYCAST, 'Anycast'),
        (ROLE_VIP, 'VIP'),
        (ROLE_VRRP, 'VRRP'),
        (ROLE_HSRP, 'HSRP'),
        (ROLE_GLBP, 'GLBP'),
        (ROLE_CARP, 'CARP'),
    )

    CSS_CLASSES = {
        ROLE_LOOPBACK: 'secondary',
        ROLE_SECONDARY: 'primary',
        ROLE_ANYCAST: 'warning',
        ROLE_VIP: 'success',
        ROLE_VRRP: 'success',
        ROLE_HSRP: 'success',
        ROLE_GLBP: 'success',
        ROLE_CARP: 'success',
    }


#
# FHRP
#

class FHRPGroupProtocolChoices(ChoiceSet):

    PROTOCOL_VRRP2 = 'vrrp2'
    PROTOCOL_VRRP3 = 'vrrp3'
    PROTOCOL_HSRP = 'hsrp'
    PROTOCOL_GLBP = 'glbp'
    PROTOCOL_CARP = 'carp'

    CHOICES = (
        (PROTOCOL_VRRP2, 'VRRPv2'),
        (PROTOCOL_VRRP3, 'VRRPv3'),
        (PROTOCOL_HSRP, 'HSRP'),
        (PROTOCOL_GLBP, 'GLBP'),
        (PROTOCOL_CARP, 'CARP'),
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

    STATUS_ACTIVE = 'active'
    STATUS_RESERVED = 'reserved'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    CSS_CLASSES = {
        STATUS_ACTIVE: 'primary',
        STATUS_RESERVED: 'info',
        STATUS_DEPRECATED: 'danger',
    }


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
