from typing import Annotated, List

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType

from core.models import ObjectChange

__all__ = (
    'ChangelogMixin',
)


@strawberry.type
class ChangelogMixin:

    @strawberry_django.field
    def changelog(self, info) -> List[Annotated["ObjectChangeType", strawberry.lazy('.types')]]:  # noqa: F821
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.request.user, 'view')
