import strawberry

from wireless.choices import *

__all__ = (
    'WirelessAuthCipherEnum',
    'WirelessAuthTypeEnum',
    'WirelessChannelEnum',
    'WirelessLANStatusEnum',
    'WirelessRoleEnum',
)

WirelessAuthCipherEnum = strawberry.enum(WirelessAuthCipherChoices.as_enum(prefix='cipher'))
WirelessAuthTypeEnum = strawberry.enum(WirelessAuthTypeChoices.as_enum(prefix='type'))
WirelessChannelEnum = strawberry.enum(WirelessChannelChoices.as_enum(prefix='channel'))
WirelessLANStatusEnum = strawberry.enum(WirelessLANStatusChoices.as_enum(prefix='status'))
WirelessRoleEnum = strawberry.enum(WirelessRoleChoices.as_enum(prefix='role'))
