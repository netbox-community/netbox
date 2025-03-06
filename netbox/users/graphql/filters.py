import strawberry_django

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin
from users import filtersets, models

__all__ = (
    'GroupFilter',
    'UserFilter',
)


@strawberry_django.filter(models.Group, lookups=True)
@autotype_decorator(filtersets.GroupFilterSet)
class GroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.User, lookups=True)
@autotype_decorator(filtersets.UserFilterSet)
class UserFilter(BaseFilterMixin):
    pass
