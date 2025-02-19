import strawberry

from vpn.choices import *

__all__ = (
    'AuthenticationAlgorithmEnum',
    'AuthenticationMethodEnum',
    'DHGroupEnum',
    'EncryptionAlgorithmEnum',
    'IKEModeEnum',
    'IKEVersionEnum',
    'IPSecModeEnum',
    'L2VPNTypeEnum',
    'TunnelEncapsulationEnum',
    'TunnelStatusEnum',
    'TunnelTerminationRoleEnum',
    'TunnelTerminationTypeEnum',
)

AuthenticationAlgorithmEnum = strawberry.enum(AuthenticationAlgorithmChoices.as_enum())
AuthenticationMethodEnum = strawberry.enum(AuthenticationMethodChoices.as_enum())
DHGroupEnum = strawberry.enum(DHGroupChoices.as_enum())
EncryptionAlgorithmEnum = strawberry.enum(EncryptionAlgorithmChoices.as_enum())
IKEModeEnum = strawberry.enum(IKEModeChoices.as_enum())
IKEVersionEnum = strawberry.enum(IKEVersionChoices.as_enum())
IPSecModeEnum = strawberry.enum(IPSecModeChoices.as_enum())
L2VPNTypeEnum = strawberry.enum(L2VPNTypeChoices.as_enum())
TunnelEncapsulationEnum = strawberry.enum(TunnelEncapsulationChoices.as_enum())
TunnelStatusEnum = strawberry.enum(TunnelStatusChoices.as_enum())
TunnelTerminationRoleEnum = strawberry.enum(TunnelTerminationRoleChoices.as_enum())
TunnelTerminationTypeEnum = strawberry.enum(TunnelTerminationTypeChoices.as_enum())
