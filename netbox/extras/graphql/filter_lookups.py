import strawberry
import strawberry_django
from django.db.models import Q, QuerySet
from strawberry.directive import DirectiveValue
from strawberry.types import Info

__all__ = (
    'ExtraChoicesLookup',
)


@strawberry.input(
    one_of=True,
    description='Lookup for extra choices defined on a choice set. Only one of the lookup fields can be set.',
)
class ExtraChoicesLookup:
    contains: str | None = strawberry.field(
        default=strawberry.UNSET, description='Has an extra choice with this value'
    )
    length: int | None = strawberry.field(
        default=strawberry.UNSET, description='Number of extra choices'
    )

    @strawberry_django.filter_field
    def filter(self, info: Info, queryset: QuerySet, prefix: DirectiveValue[str] = '') -> tuple[QuerySet, Q]:
        if self.contains is not strawberry.UNSET and self.contains is not None:
            return queryset, Q(**{f'{prefix}choice_value': self.contains})
        if self.length is not strawberry.UNSET and self.length is not None:
            return queryset, Q(**{f'{prefix}len': self.length})
        return queryset, Q()
