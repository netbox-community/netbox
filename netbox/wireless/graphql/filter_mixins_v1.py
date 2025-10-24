from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1

if TYPE_CHECKING:
    from .enums import *

__all__ = (
    'WirelessAuthenticationBaseFilterMixinV1',
)


@dataclass
class WirelessAuthenticationBaseFilterMixinV1(BaseFilterMixinV1):
    auth_type: Annotated['WirelessAuthTypeEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_cipher: Annotated['WirelessAuthCipherEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_psk: FilterLookup[str] | None = strawberry_django.filter_field()
