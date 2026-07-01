from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Q

if TYPE_CHECKING:
    from .enums import *

__all__ = (
    'ServiceFilterMixin',
)


class ServiceFilterMixin:

    @strawberry_django.filter_field()
    def protocol(
        self,
        value: list[Annotated['ServiceProtocolEnum', strawberry.lazy('ipam.graphql.enums')]],
        prefix,
    ) -> Q:
        if not value:
            return Q()
        q = Q()
        for protocol in value:
            q |= Q(**{f'{prefix}port_assignments__contains': [{'protocol': protocol.value}]})
        return q

    @strawberry_django.filter_field()
    def port(self, value: list[int], prefix) -> Q:
        if not value:
            return Q()
        q = Q()
        for port in value:
            q |= Q(**{f'{prefix}port_assignments__contains': [{'port': port}]})
        return q
