from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

if TYPE_CHECKING:
    from .enums import *

__all__ = (
    'WirelessAuthenticationFilterMixin',
)


@dataclass
class WirelessAuthenticationFilterMixin:
    auth_type: Annotated['WirelessAuthTypeEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_cipher: Annotated['WirelessAuthCipherEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_psk: FilterLookup[str] | None = strawberry_django.filter_field()
