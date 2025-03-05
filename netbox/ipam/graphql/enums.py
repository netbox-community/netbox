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

FHRPGroupAuthTypeEnum = strawberry.enum(FHRPGroupAuthTypeChoices.as_enum())
FHRPGroupProtocolEnum = strawberry.enum(FHRPGroupProtocolChoices.as_enum())
IPAddressFamilyEnum = strawberry.enum(IPAddressFamilyChoices.as_enum())
IPAddressRoleEnum = strawberry.enum(IPAddressRoleChoices.as_enum())
IPAddressStatusEnum = strawberry.enum(IPAddressStatusChoices.as_enum())
IPRangeStatusEnum = strawberry.enum(IPRangeStatusChoices.as_enum())
PrefixStatusEnum = strawberry.enum(PrefixStatusChoices.as_enum())
ServiceProtocolEnum = strawberry.enum(ServiceProtocolChoices.as_enum())
VLANStatusEnum = strawberry.enum(VLANStatusChoices.as_enum())
VLANQinQRoleEnum = strawberry.enum(VLANQinQRoleChoices.as_enum())
