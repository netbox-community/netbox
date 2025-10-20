from typing import List

import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class WirelessQueryOld:
    wireless_lan: WirelessLANType = strawberry_django.field()
    wireless_lan_list: List[WirelessLANType] = strawberry_django.field()

    wireless_lan_group: WirelessLANGroupType = strawberry_django.field()
    wireless_lan_group_list: List[WirelessLANGroupType] = strawberry_django.field()

    wireless_link: WirelessLinkType = strawberry_django.field()
    wireless_link_list: List[WirelessLinkType] = strawberry_django.field()


@strawberry.type(name="Query")
class WirelessQuery:
    wireless_lan: WirelessLANType = strawberry_django.field()
    wireless_lan_list: OffsetPaginated[WirelessLANType] = strawberry_django.offset_paginated()

    wireless_lan_group: WirelessLANGroupType = strawberry_django.field()
    wireless_lan_group_list: OffsetPaginated[WirelessLANGroupType] = strawberry_django.offset_paginated()

    wireless_link: WirelessLinkType = strawberry_django.field()
    wireless_link_list: OffsetPaginated[WirelessLinkType] = strawberry_django.offset_paginated()
