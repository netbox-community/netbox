from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

#
# Tunnels
#


class TunnelStatusChoices(ChoiceSet):
    key = 'Tunnel.status'

    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'

    CHOICES = [
        Choice(
            STATUS_PLANNED,
            _('Planned'),
            color='cyan',
            description=_('Designated for future use but not yet in service')
        ),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Established and carrying traffic')),
        Choice(STATUS_DISABLED, _('Disabled'), color='red', description=_('Administratively disabled')),
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
        Choice(
            ENCAP_IPSEC_TRANSPORT,
            _('IPsec - Transport'),
            description=_('IPsec encrypting only the packet payload between endpoints')
        ),
        Choice(
            ENCAP_IPSEC_TUNNEL,
            _('IPsec - Tunnel'),
            description=_('IPsec encrypting the entire original IP packet')
        ),
        Choice(ENCAP_IP_IP, _('IP-in-IP'), description=_('Encapsulation of one IP packet within another')),
        Choice(ENCAP_GRE, _('GRE'), description=_('Generic Routing Encapsulation')),
        Choice(ENCAP_WIREGUARD, _('WireGuard')),
        Choice(ENCAP_OPENVPN, _('OpenVPN')),
        Choice(ENCAP_L2TP, _('L2TP'), description=_('Layer 2 Tunneling Protocol')),
        Choice(ENCAP_PPTP, _('PPTP'), description=_('Point-to-Point Tunneling Protocol')),
    ]


class TunnelTerminationTypeChoices(ChoiceSet):
    # For TunnelCreateForm
    TYPE_DEVICE = 'dcim.device'
    TYPE_VIRTUALMACHINE = 'virtualization.virtualmachine'

    CHOICES = (
        Choice(TYPE_DEVICE, _('Device')),
        Choice(TYPE_VIRTUALMACHINE, _('Virtual Machine')),
    )


class TunnelTerminationRoleChoices(ChoiceSet):
    ROLE_PEER = 'peer'
    ROLE_HUB = 'hub'
    ROLE_SPOKE = 'spoke'

    CHOICES = [
        Choice(ROLE_PEER, _('Peer'), color='green', description=_('Symmetric endpoint in a point-to-point tunnel')),
        Choice(ROLE_HUB, _('Hub'), color='blue', description=_('Central endpoint in a hub-and-spoke topology')),
        Choice(ROLE_SPOKE, _('Spoke'), color='orange', description=_('Remote endpoint connecting to a hub')),
    ]


#
# Crypto
#

class IKEVersionChoices(ChoiceSet):
    VERSION_1 = 1
    VERSION_2 = 2

    CHOICES = (
        Choice(VERSION_1, 'IKEv1'),
        Choice(VERSION_2, 'IKEv2'),
    )


class IKEModeChoices(ChoiceSet):
    AGGRESSIVE = 'aggressive'
    MAIN = 'main'

    CHOICES = (
        Choice(AGGRESSIVE, _('Aggressive')),
        Choice(MAIN, _('Main')),
    )


class AuthenticationMethodChoices(ChoiceSet):
    PRESHARED_KEYS = 'preshared-keys'
    CERTIFICATES = 'certificates'
    RSA_SIGNATURES = 'rsa-signatures'
    DSA_SIGNATURES = 'dsa-signatures'

    CHOICES = (
        Choice(PRESHARED_KEYS, _('Pre-shared keys')),
        Choice(CERTIFICATES, _('Certificates')),
        Choice(RSA_SIGNATURES, _('RSA signatures')),
        Choice(DSA_SIGNATURES, _('DSA signatures')),
    )


class IPSecModeChoices(ChoiceSet):
    ESP = 'esp'
    AH = 'ah'

    CHOICES = (
        Choice(ESP, 'ESP'),
        Choice(AH, 'AH'),
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
        Choice(ENCRYPTION_AES128_CBC, '128-bit AES (CBC)'),
        Choice(ENCRYPTION_AES128_GCM, '128-bit AES (GCM)'),
        Choice(ENCRYPTION_AES192_CBC, '192-bit AES (CBC)'),
        Choice(ENCRYPTION_AES192_GCM, '192-bit AES (GCM)'),
        Choice(ENCRYPTION_AES256_CBC, '256-bit AES (CBC)'),
        Choice(ENCRYPTION_AES256_GCM, '256-bit AES (GCM)'),
        Choice(ENCRYPTION_3DES, '3DES'),
        Choice(ENCRYPTION_DES, 'DES'),
    )


class AuthenticationAlgorithmChoices(ChoiceSet):
    AUTH_HMAC_SHA1 = 'hmac-sha1'
    AUTH_HMAC_SHA256 = 'hmac-sha256'
    AUTH_HMAC_SHA384 = 'hmac-sha384'
    AUTH_HMAC_SHA512 = 'hmac-sha512'
    AUTH_HMAC_MD5 = 'hmac-md5'

    CHOICES = (
        Choice(AUTH_HMAC_SHA1, 'SHA-1 HMAC'),
        Choice(AUTH_HMAC_SHA256, 'SHA-256 HMAC'),
        Choice(AUTH_HMAC_SHA384, 'SHA-384 HMAC'),
        Choice(AUTH_HMAC_SHA512, 'SHA-512 HMAC'),
        Choice(AUTH_HMAC_MD5, 'MD5 HMAC'),
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
        Choice(GROUP_1, _('Group {n}').format(n=1)),
        Choice(GROUP_2, _('Group {n}').format(n=2)),
        Choice(GROUP_5, _('Group {n}').format(n=5)),
        Choice(GROUP_14, _('Group {n}').format(n=14)),
        Choice(GROUP_15, _('Group {n}').format(n=15)),
        Choice(GROUP_16, _('Group {n}').format(n=16)),
        Choice(GROUP_17, _('Group {n}').format(n=17)),
        Choice(GROUP_18, _('Group {n}').format(n=18)),
        Choice(GROUP_19, _('Group {n}').format(n=19)),
        Choice(GROUP_20, _('Group {n}').format(n=20)),
        Choice(GROUP_21, _('Group {n}').format(n=21)),
        Choice(GROUP_22, _('Group {n}').format(n=22)),
        Choice(GROUP_23, _('Group {n}').format(n=23)),
        Choice(GROUP_24, _('Group {n}').format(n=24)),
        Choice(GROUP_25, _('Group {n}').format(n=25)),
        Choice(GROUP_26, _('Group {n}').format(n=26)),
        Choice(GROUP_27, _('Group {n}').format(n=27)),
        Choice(GROUP_28, _('Group {n}').format(n=28)),
        Choice(GROUP_29, _('Group {n}').format(n=29)),
        Choice(GROUP_30, _('Group {n}').format(n=30)),
        Choice(GROUP_31, _('Group {n}').format(n=31)),
        Choice(GROUP_32, _('Group {n}').format(n=32)),
        Choice(GROUP_33, _('Group {n}').format(n=33)),
        Choice(GROUP_34, _('Group {n}').format(n=34)),
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
    TYPE_SPB = 'spb'

    CHOICES = (
        ('VPLS', (
            Choice(
                TYPE_VPWS,
                'VPWS',
                description=_('Virtual Private Wire Service: point-to-point Layer 2 connectivity')
            ),
            Choice(
                TYPE_VPLS,
                'VPLS',
                description=_('Virtual Private LAN Service: multipoint Layer 2 connectivity')
            ),
        )),
        ('VXLAN', (
            Choice(TYPE_VXLAN, 'VXLAN', description=_('Virtual Extensible LAN overlay')),
            Choice(TYPE_VXLAN_EVPN, 'VXLAN-EVPN', description=_('VXLAN with EVPN control plane')),
        )),
        ('L2VPN E-VPN', (
            Choice(TYPE_MPLS_EVPN, 'MPLS EVPN', description=_('Ethernet VPN over an MPLS transport')),
            Choice(TYPE_PBB_EVPN, 'PBB EVPN', description=_('Provider Backbone Bridging with EVPN')),
            Choice(TYPE_EVPN_VPWS, 'EVPN VPWS', description=_('Point-to-point service using an EVPN control plane'))
        )),
        ('E-Line', (
            Choice(TYPE_EPL, 'EPL', description=_('Ethernet Private Line: dedicated point-to-point service')),
            Choice(
                TYPE_EVPL,
                'EVPL',
                description=_('Ethernet Virtual Private Line: multiplexed point-to-point service')
            ),
        )),
        ('E-LAN', (
            Choice(TYPE_EPLAN, _('Ethernet Private LAN'), description=_('Dedicated multipoint-to-multipoint service')),
            Choice(
                TYPE_EVPLAN,
                _('Ethernet Virtual Private LAN'),
                description=_('Multiplexed multipoint-to-multipoint service')
            ),
        )),
        ('E-Tree', (
            Choice(TYPE_EPTREE, _('Ethernet Private Tree'), description=_('Dedicated rooted multipoint service')),
            Choice(
                TYPE_EVPTREE,
                _('Ethernet Virtual Private Tree'),
                description=_('Multiplexed rooted multipoint service')
            ),
        )),
        ('Other', (
            Choice(TYPE_SPB, _('SPB'), description=_('Shortest Path Bridging')),
        )),
    )

    P2P = (
        TYPE_VPWS,
        TYPE_EPL,
        TYPE_EPLAN,
        TYPE_EPTREE
    )


class L2VPNStatusChoices(ChoiceSet):
    key = 'L2VPN.status'

    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Established and carrying traffic')),
        Choice(
            STATUS_PLANNED,
            _('Planned'),
            color='cyan',
            description=_('Designated for future use but not yet in service')
        ),
        Choice(STATUS_DECOMMISSIONING, _('Decommissioning'), color='red', description=_('Being retired from service')),
    ]
