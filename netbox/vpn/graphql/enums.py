from enum import Enum
import strawberry

__all__ = [
    'TunnelStatusEnum',
    'TunnelEncapsulationEnum',
    'TunnelTerminationTypeEnum',
    'TunnelTerminationRoleEnum',
    'IKEVersionEnum',
    'IKEModeEnum',
    'AuthenticationMethodEnum',
    'IPSecModeEnum',
    'EncryptionAlgorithmEnum',
    'AuthenticationAlgorithmEnum',
    'DHGroupEnum',
    'L2VPNTypeEnum',
]

#
# Tunnels
#


@strawberry.enum
class TunnelStatusEnum(Enum):
    key = 'Tunnel.status'

    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DISABLED = 'disabled'


@strawberry.enum
class TunnelEncapsulationEnum(Enum):
    ENCAP_GRE = 'gre'
    ENCAP_IPSEC_TRANSPORT = 'ipsec-transport'
    ENCAP_IPSEC_TUNNEL = 'ipsec-tunnel'
    ENCAP_IP_IP = 'ip-ip'
    ENCAP_L2TP = 'l2tp'
    ENCAP_OPENVPN = 'openvpn'
    ENCAP_PPTP = 'pptp'
    ENCAP_WIREGUARD = 'wireguard'


@strawberry.enum
class TunnelTerminationTypeEnum(Enum):
    # For TunnelCreateForm
    TYPE_DEVICE = 'dcim.device'
    TYPE_VIRTUALMACHINE = 'virtualization.virtualmachine'


@strawberry.enum
class TunnelTerminationRoleEnum(Enum):
    ROLE_PEER = 'peer'
    ROLE_HUB = 'hub'
    ROLE_SPOKE = 'spoke'


#
# Crypto
#


@strawberry.enum
class IKEVersionEnum(Enum):
    VERSION_1 = 1
    VERSION_2 = 2


@strawberry.enum
class IKEModeEnum(Enum):
    AGGRESSIVE = 'aggressive'
    MAIN = 'main'


@strawberry.enum
class AuthenticationMethodEnum(Enum):
    PRESHARED_KEYS = 'preshared-keys'
    CERTIFICATES = 'certificates'
    RSA_SIGNATURES = 'rsa-signatures'
    DSA_SIGNATURES = 'dsa-signatures'


@strawberry.enum
class IPSecModeEnum(Enum):
    ESP = 'esp'
    AH = 'ah'


@strawberry.enum
class EncryptionAlgorithmEnum(Enum):
    ENCRYPTION_AES128_CBC = 'aes-128-cbc'
    ENCRYPTION_AES128_GCM = 'aes-128-gcm'
    ENCRYPTION_AES192_CBC = 'aes-192-cbc'
    ENCRYPTION_AES192_GCM = 'aes-192-gcm'
    ENCRYPTION_AES256_CBC = 'aes-256-cbc'
    ENCRYPTION_AES256_GCM = 'aes-256-gcm'
    ENCRYPTION_3DES = '3des-cbc'
    ENCRYPTION_DES = 'des-cbc'


@strawberry.enum
class AuthenticationAlgorithmEnum(Enum):
    AUTH_HMAC_SHA1 = 'hmac-sha1'
    AUTH_HMAC_SHA256 = 'hmac-sha256'
    AUTH_HMAC_SHA384 = 'hmac-sha384'
    AUTH_HMAC_SHA512 = 'hmac-sha512'
    AUTH_HMAC_MD5 = 'hmac-md5'


@strawberry.enum
class DHGroupEnum(Enum):
    # https://www.iana.org/assignments/ikev2-parameters/ikev2-parameters.xhtml#ikev2-parameters-8
    GROUP_1 = 1  # 768-bit MODP
    GROUP_2 = 2  # 1024-but MODP
    # Groups 3-4 reserved
    GROUP_5 = 5  # 1536-bit MODP
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


#
# L2VPN
#


@strawberry.enum
class L2VPNTypeEnum(Enum):
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
