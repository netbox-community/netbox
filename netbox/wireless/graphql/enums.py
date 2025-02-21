import strawberry

from wireless.choices import *

__all__ = (
    'WirelessAuthCipherEnum',
    'WirelessAuthTypeEnum',
    'WirelessChannelEnum',
    'WirelessLANStatusEnum',
    'WirelessRoleEnum',
)

WirelessAuthCipherEnum = strawberry.enum(WirelessAuthCipherChoices.as_enum())
WirelessAuthTypeEnum = strawberry.enum(WirelessAuthTypeChoices.as_enum())
WirelessChannelEnum = strawberry.enum(WirelessChannelChoices.as_enum())
WirelessLANStatusEnum = strawberry.enum(WirelessLANStatusChoices.as_enum())
WirelessRoleEnum = strawberry.enum(WirelessRoleChoices.as_enum())
