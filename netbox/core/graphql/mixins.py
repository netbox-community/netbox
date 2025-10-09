from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType
from strawberry.types import Info

from core.models import ObjectChange

if TYPE_CHECKING:
    from core.graphql.types import DataFileType, DataSourceType, ObjectChangeType

__all__ = (
    'ChangelogMixin',
    'SyncedDataMixin',
)


@strawberry.type
class ChangelogMixin:

    @strawberry_django.field
    def changelog(self, info: Info) -> List[Annotated['ObjectChangeType', strawberry.lazy('.types')]]:  # noqa: F821
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.request.user, 'view')


@strawberry.type
class SyncedDataMixin:
    data_source: Annotated['DataSourceType', strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated['DataFileType', strawberry.lazy('core.graphql.types')] | None
