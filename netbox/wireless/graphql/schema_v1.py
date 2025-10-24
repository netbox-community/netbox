from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class WirelessQueryV1:
    wireless_lan: WirelessLANTypeV1 = strawberry_django.field()
    wireless_lan_list: List[WirelessLANTypeV1] = strawberry_django.field()

    wireless_lan_group: WirelessLANGroupTypeV1 = strawberry_django.field()
    wireless_lan_group_list: List[WirelessLANGroupTypeV1] = strawberry_django.field()

    wireless_link: WirelessLinkTypeV1 = strawberry_django.field()
    wireless_link_list: List[WirelessLinkTypeV1] = strawberry_django.field()
