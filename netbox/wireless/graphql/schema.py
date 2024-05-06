from typing import List

import strawberry
import strawberry_django

from wireless import models
from .types import *


@strawberry.type
class WirelessQuery:
    @strawberry.field
    def wireless_lan(self, id: int) -> WirelessLANType:
        return models.WirelessLAN.objects.get(pk=id)
    wireless_lan_list: List[WirelessLANType] = strawberry_django.field()

    @strawberry.field
    def wireless_lan_group(self, id: int) -> WirelessLANGroupType:
        return models.WirelessLANGroup.objects.get(pk=id)
    wireless_lan_group_list: List[WirelessLANGroupType] = strawberry_django.field()

    @strawberry.field
    def wireless_link(self, id: int) -> WirelessLinkType:
        return models.WirelessLink.objects.get(pk=id)
    wireless_link_list: List[WirelessLinkType] = strawberry_django.field()
