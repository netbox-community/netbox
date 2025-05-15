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

AuthenticationAlgorithmEnum = strawberry.enum(AuthenticationAlgorithmChoices.as_enum(prefix='auth'))
AuthenticationMethodEnum = strawberry.enum(AuthenticationMethodChoices.as_enum())
DHGroupEnum = strawberry.enum(DHGroupChoices.as_enum(prefix='group'))
EncryptionAlgorithmEnum = strawberry.enum(EncryptionAlgorithmChoices.as_enum(prefix='encryption'))
IKEModeEnum = strawberry.enum(IKEModeChoices.as_enum())
IKEVersionEnum = strawberry.enum(IKEVersionChoices.as_enum(prefix='version'))
IPSecModeEnum = strawberry.enum(IPSecModeChoices.as_enum())
L2VPNTypeEnum = strawberry.enum(L2VPNTypeChoices.as_enum(prefix='type'))
TunnelEncapsulationEnum = strawberry.enum(TunnelEncapsulationChoices.as_enum(prefix='encap'))
TunnelStatusEnum = strawberry.enum(TunnelStatusChoices.as_enum(prefix='status'))
TunnelTerminationRoleEnum = strawberry.enum(TunnelTerminationRoleChoices.as_enum(prefix='role'))
TunnelTerminationTypeEnum = strawberry.enum(TunnelTerminationTypeChoices.as_enum(prefix='type'))
