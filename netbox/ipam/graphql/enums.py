import strawberry

from ipam.choices import *

__all__ = (
    'FHRPGroupAuthTypeEnum',
    'FHRPGroupProtocolEnum',
    'IPAddressFamilyEnum',
    'IPAddressRoleEnum',
    'IPAddressStatusEnum',
    'IPRangeStatusEnum',
    'PrefixStatusEnum',
    'ServiceProtocolEnum',
    'VLANStatusEnum',
    'VLANQinQRoleEnum',
)

FHRPGroupAuthTypeEnum = strawberry.enum(FHRPGroupAuthTypeChoices.as_enum(prefix='authentication'))
FHRPGroupProtocolEnum = strawberry.enum(FHRPGroupProtocolChoices.as_enum(prefix='protocol'))
IPAddressFamilyEnum = strawberry.enum(IPAddressFamilyChoices.as_enum(prefix='family'))
IPAddressRoleEnum = strawberry.enum(IPAddressRoleChoices.as_enum(prefix='role'))
IPAddressStatusEnum = strawberry.enum(IPAddressStatusChoices.as_enum(prefix='status'))
IPRangeStatusEnum = strawberry.enum(IPRangeStatusChoices.as_enum(prefix='status'))
PrefixStatusEnum = strawberry.enum(PrefixStatusChoices.as_enum(prefix='status'))
ServiceProtocolEnum = strawberry.enum(ServiceProtocolChoices.as_enum(prefix='role'))
VLANStatusEnum = strawberry.enum(VLANStatusChoices.as_enum(prefix='status'))
VLANQinQRoleEnum = strawberry.enum(VLANQinQRoleChoices.as_enum(prefix='role'))
