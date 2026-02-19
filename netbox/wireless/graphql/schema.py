import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class WirelessQuery:
    wireless_lan: WirelessLANType = strawberry_django.field()
    wireless_lan_list: list[WirelessLANType] = strawberry_django.field()

    wireless_lan_group: WirelessLANGroupType = strawberry_django.field()
    wireless_lan_group_list: list[WirelessLANGroupType] = strawberry_django.field()

    wireless_link: WirelessLinkType = strawberry_django.field()
    wireless_link_list: list[WirelessLinkType] = strawberry_django.field()
