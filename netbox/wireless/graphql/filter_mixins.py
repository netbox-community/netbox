from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from .enums import *

__all__ = (
    'WirelessAuthenticationBaseFilterMixin',
)


@dataclass
class WirelessAuthenticationBaseFilterMixin(BaseFilterMixin):
    auth_type: Annotated['WirelessAuthTypeEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_cipher: Annotated['WirelessAuthCipherEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    auth_psk: FilterLookup[str] | None = strawberry_django.filter_field()
