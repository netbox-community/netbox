from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


#
# Tunnels
#

class TunnelStatusChoices(ChoiceSet):
    key = 'Tunnel.status'

    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'

    CHOICES = [
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_DISABLED, _('Disabled'), 'red'),
    ]


class TunnelEncapsulationChoices(ChoiceSet):
    ENCAP_GRE = 'gre'
    ENCAP_IP_IP = 'ip-ip'
    ENCAP_IPSEC_TRANSPORT = 'ipsec-transport'
    ENCAP_IPSEC_TUNNEL = 'ipsec-tunnel'

    CHOICES = [
        (ENCAP_IPSEC_TRANSPORT, _('IPsec - Transport')),
        (ENCAP_IPSEC_TUNNEL, _('IPsec - Tunnel')),
        (ENCAP_IP_IP, _('IP-in-IP')),
        (ENCAP_GRE, _('GRE')),
    ]


class TunnelTerminationRoleChoices(ChoiceSet):
    ROLE_PEER = 'peer'
    ROLE_HUB = 'hub'
    ROLE_SPOKE = 'spoke'

    CHOICES = [
        (ROLE_PEER, _('Peer'), 'green'),
        (ROLE_HUB, _('Hub'), 'blue'),
        (ROLE_SPOKE, _('Spoke'), 'orange'),
    ]


#
# IKE
#

class IPSecProtocolChoices(ChoiceSet):
    PROTOCOL_ESP = 'esp'
    PROTOCOL_AH = 'ah'

    CHOICES = (
        (PROTOCOL_ESP, 'ESP'),
        (PROTOCOL_AH, 'AH'),
    )


class IKEVersionChoices(ChoiceSet):
    VERSION_1 = 1
    VERSION_2 = 2

    CHOICES = (
        (VERSION_1, 'IKEv1'),
        (VERSION_2, 'IKEv2'),
    )


class EncryptionChoices(ChoiceSet):
    ENCRYPTION_AES128 = 'aes-128'
    ENCRYPTION_AES192 = 'aes-192'
    ENCRYPTION_AES256 = 'aes-256'
    ENCRYPTION_3DES = '3des'

    CHOICES = (
        (ENCRYPTION_AES128, 'AES (128-bit)'),
        (ENCRYPTION_AES192, 'AES (192-bit)'),
        (ENCRYPTION_AES256, 'AES (256-bit)'),
        (ENCRYPTION_3DES, '3DES'),
    )


class AuthenticationChoices(ChoiceSet):
    AUTH_SHA1 = 'SHA-1'
    AUTH_MD5 = 'MD5'

    CHOICES = (
        (AUTH_SHA1, 'SHA-1'),
        (AUTH_MD5, 'MD5'),
    )


class DHGroupChoices(ChoiceSet):
    # TODO: Add all the groups & annotate their attributes
    GROUP_1 = 1
    GROUP_2 = 2
    GROUP_5 = 5
    GROUP_7 = 7

    CHOICES = (
        (GROUP_1, _('Group {n}').format(n=1)),
        (GROUP_2, _('Group {n}').format(n=2)),
        (GROUP_5, _('Group {n}').format(n=5)),
        (GROUP_7, _('Group {n}').format(n=7)),
    )
