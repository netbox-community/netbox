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
    ENCAP_IPSEC_TRANSPORT = 'ipsec-transport'
    ENCAP_IPSEC_TUNNEL = 'ipsec-tunnel'
    ENCAP_IP_IP = 'ip-ip'
    ENCAP_L2TP = 'l2tp'
    ENCAP_OPENVPN = 'openvpn'
    ENCAP_PPTP = 'pptp'
    ENCAP_WIREGUARD = 'wireguard'

    CHOICES = [
        (ENCAP_IPSEC_TRANSPORT, _('IPsec - Transport')),
        (ENCAP_IPSEC_TUNNEL, _('IPsec - Tunnel')),
        (ENCAP_IP_IP, _('IP-in-IP')),
        (ENCAP_GRE, _('GRE')),
        (ENCAP_WIREGUARD, _('WireGuard')),
        (ENCAP_OPENVPN, _('OpenVPN')),
        (ENCAP_L2TP, _('L2TP')),
        (ENCAP_PPTP, _('PPTP')),
    ]


class TunnelTerminationTypeChoices(ChoiceSet):
    # For TunnelCreateForm
    TYPE_DEVICE = 'dcim.device'
    TYPE_VIRTUALMACHINE = 'virtualization.virtualmachine'

    CHOICES = (
        (TYPE_DEVICE, _('Device')),
        (TYPE_VIRTUALMACHINE, _('Virtual Machine')),
    )


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
# Crypto
#

class IKEVersionChoices(ChoiceSet):
    VERSION_1 = 1
    VERSION_2 = 2

    CHOICES = (
        (VERSION_1, 'IKEv1'),
        (VERSION_2, 'IKEv2'),
    )


class IKEModeChoices(ChoiceSet):
    AGGRESSIVE = 'aggressive'
    MAIN = 'main'

    CHOICES = (
        (AGGRESSIVE, _('Aggressive')),
        (MAIN, _('Main')),
    )


class AuthenticationMethodChoices(ChoiceSet):
    PRESHARED_KEYS = 'preshared-keys'
    CERTIFICATES = 'certificates'
    RSA_SIGNATURES = 'rsa-signatures'
    DSA_SIGNATURES = 'dsa-signatures'

    CHOICES = (
        (PRESHARED_KEYS, _('Pre-shared keys')),
        (CERTIFICATES, _('Certificates')),
        (RSA_SIGNATURES, _('RSA signatures')),
        (DSA_SIGNATURES, _('DSA signatures')),
    )


class IPSecModeChoices(ChoiceSet):
    ESP = 'esp'
    AH = 'ah'

    CHOICES = (
        (ESP, 'ESP'),
        (AH, 'AH'),
    )


class EncryptionAlgorithmChoices(ChoiceSet):
    ENCRYPTION_AES128_CBC = 'aes-128-cbc'
    ENCRYPTION_AES128_GCM = 'aes-128-gcm'
    ENCRYPTION_AES192_CBC = 'aes-192-cbc'
    ENCRYPTION_AES192_GCM = 'aes-192-gcm'
    ENCRYPTION_AES256_CBC = 'aes-256-cbc'
    ENCRYPTION_AES256_GCM = 'aes-256-gcm'
    ENCRYPTION_3DES = '3des-cbc'
    ENCRYPTION_DES = 'des-cbc'

    CHOICES = (
        (ENCRYPTION_AES128_CBC, '128-bit AES (CBC)'),
        (ENCRYPTION_AES128_GCM, '128-bit AES (GCM)'),
        (ENCRYPTION_AES192_CBC, '192-bit AES (CBC)'),
        (ENCRYPTION_AES192_GCM, '192-bit AES (GCM)'),
        (ENCRYPTION_AES256_CBC, '256-bit AES (CBC)'),
        (ENCRYPTION_AES256_GCM, '256-bit AES (GCM)'),
        (ENCRYPTION_3DES, '3DES'),
        (ENCRYPTION_DES, 'DES'),
    )


class AuthenticationAlgorithmChoices(ChoiceSet):
    AUTH_HMAC_SHA1 = 'hmac-sha1'
    AUTH_HMAC_SHA256 = 'hmac-sha256'
    AUTH_HMAC_SHA384 = 'hmac-sha384'
    AUTH_HMAC_SHA512 = 'hmac-sha512'
    AUTH_HMAC_MD5 = 'hmac-md5'

    CHOICES = (
        (AUTH_HMAC_SHA1, 'SHA-1 HMAC'),
        (AUTH_HMAC_SHA256, 'SHA-256 HMAC'),
        (AUTH_HMAC_SHA384, 'SHA-384 HMAC'),
        (AUTH_HMAC_SHA512, 'SHA-512 HMAC'),
        (AUTH_HMAC_MD5, 'MD5 HMAC'),
    )


class DHGroupChoices(ChoiceSet):
    # https://www.iana.org/assignments/ikev2-parameters/ikev2-parameters.xhtml#ikev2-parameters-8
    GROUP_1 = 1    # 768-bit MODP
    GROUP_2 = 2    # 1024-but MODP
    # Groups 3-4 reserved
    GROUP_5 = 5    # 1536-bit MODP
    # Groups 6-13 unassigned
    GROUP_14 = 14  # 2048-bit MODP
    GROUP_15 = 15  # 3072-bit MODP
    GROUP_16 = 16  # 4096-bit MODP
    GROUP_17 = 17  # 6144-bit MODP
    GROUP_18 = 18  # 8192-bit MODP
    GROUP_19 = 19  # 256-bit random ECP
    GROUP_20 = 20  # 384-bit random ECP
    GROUP_21 = 21  # 521-bit random ECP (521 is not a typo)
    GROUP_22 = 22  # 1024-bit MODP w/160-bit prime
    GROUP_23 = 23  # 2048-bit MODP w/224-bit prime
    GROUP_24 = 24  # 2048-bit MODP w/256-bit prime
    GROUP_25 = 25  # 192-bit ECP
    GROUP_26 = 26  # 224-bit ECP
    GROUP_27 = 27  # brainpoolP224r1
    GROUP_28 = 28  # brainpoolP256r1
    GROUP_29 = 29  # brainpoolP384r1
    GROUP_30 = 30  # brainpoolP512r1
    GROUP_31 = 31  # Curve25519
    GROUP_32 = 32  # Curve448
    GROUP_33 = 33  # GOST3410_2012_256
    GROUP_34 = 34  # GOST3410_2012_512

    CHOICES = (
        # Strings are formatted in this manner to optimize translations
        (GROUP_1, _('Group {n}').format(n=1)),
        (GROUP_2, _('Group {n}').format(n=2)),
        (GROUP_5, _('Group {n}').format(n=5)),
        (GROUP_14, _('Group {n}').format(n=14)),
        (GROUP_15, _('Group {n}').format(n=15)),
        (GROUP_16, _('Group {n}').format(n=16)),
        (GROUP_17, _('Group {n}').format(n=17)),
        (GROUP_18, _('Group {n}').format(n=18)),
        (GROUP_19, _('Group {n}').format(n=19)),
        (GROUP_20, _('Group {n}').format(n=20)),
        (GROUP_21, _('Group {n}').format(n=21)),
        (GROUP_22, _('Group {n}').format(n=22)),
        (GROUP_23, _('Group {n}').format(n=23)),
        (GROUP_24, _('Group {n}').format(n=24)),
        (GROUP_25, _('Group {n}').format(n=25)),
        (GROUP_26, _('Group {n}').format(n=26)),
        (GROUP_27, _('Group {n}').format(n=27)),
        (GROUP_28, _('Group {n}').format(n=28)),
        (GROUP_29, _('Group {n}').format(n=29)),
        (GROUP_30, _('Group {n}').format(n=30)),
        (GROUP_31, _('Group {n}').format(n=31)),
        (GROUP_32, _('Group {n}').format(n=32)),
        (GROUP_33, _('Group {n}').format(n=33)),
        (GROUP_34, _('Group {n}').format(n=34)),
    )


#
# L2VPN
#

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
    TYPE_EVPN_VPWS = 'evpn-vpws'

    CHOICES = (
        ('VPLS', (
            (TYPE_VPWS, 'VPWS'),
            (TYPE_VPLS, 'VPLS'),
        )),
        ('VXLAN', (
            (TYPE_VXLAN, 'VXLAN'),
            (TYPE_VXLAN_EVPN, 'VXLAN-EVPN'),
        )),
        ('L2VPN E-VPN', (
            (TYPE_MPLS_EVPN, 'MPLS EVPN'),
            (TYPE_PBB_EVPN, 'PBB EVPN'),
            (TYPE_EVPN_VPWS, 'EVPN VPWS')
        )),
        ('E-Line', (
            (TYPE_EPL, 'EPL'),
            (TYPE_EVPL, 'EVPL'),
        )),
        ('E-LAN', (
            (TYPE_EPLAN, _('Ethernet Private LAN')),
            (TYPE_EVPLAN, _('Ethernet Virtual Private LAN')),
        )),
        ('E-Tree', (
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
