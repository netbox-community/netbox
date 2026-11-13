import strawberry

from ipam.choices import *

__all__ = (
    'FHRPGroupAuthTypeEnum',
    'FHRPGroupProtocolEnum',
    'IPAddressFamilyEnum',
    'IPAddressRoleEnum',
    'IPAddressStatusEnum',
    'IPRangeStatusEnum',
    'PrefixClassificationEnum',
    'PrefixStatusEnum',
    'ServiceProtocolEnum',
    'VLANQinQRoleEnum',
    'VLANStatusEnum',
)

FHRPGroupAuthTypeEnum = strawberry.enum(FHRPGroupAuthTypeChoices.as_enum(prefix='authentication'))
FHRPGroupProtocolEnum = strawberry.enum(FHRPGroupProtocolChoices.as_enum(prefix='protocol'))
IPAddressFamilyEnum = strawberry.enum(IPAddressFamilyChoices.as_enum(prefix='family'))
IPAddressRoleEnum = strawberry.enum(IPAddressRoleChoices.as_enum(prefix='role'))
IPAddressStatusEnum = strawberry.enum(IPAddressStatusChoices.as_enum(prefix='status'))
IPRangeStatusEnum = strawberry.enum(IPRangeStatusChoices.as_enum(prefix='status'))
PrefixClassificationEnum = strawberry.enum(PrefixClassificationChoices.as_enum(prefix='classification'))
PrefixStatusEnum = strawberry.enum(PrefixStatusChoices.as_enum(prefix='status'))
ServiceProtocolEnum = strawberry.enum(ServiceProtocolChoices.as_enum())
VLANStatusEnum = strawberry.enum(VLANStatusChoices.as_enum(prefix='status'))
VLANQinQRoleEnum = strawberry.enum(VLANQinQRoleChoices.as_enum(prefix='role'))
