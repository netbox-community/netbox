import strawberry
import strawberry_django
from django.contrib.auth import get_user_model
from users import filtersets, models

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

__all__ = (
    'GroupFilter',
    'UserFilter',
)


@strawberry_django.filter(models.Group, lookups=True)
@autotype_decorator(filtersets.GroupFilterSet)
class GroupFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(get_user_model(), lookups=True)
@autotype_decorator(filtersets.UserFilterSet)
class UserFilter(BaseFilterMixin):
    pass
