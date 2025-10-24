from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType
from strawberry.types import Info

from core.models import ObjectChange

if TYPE_CHECKING:
    from core.graphql.types_v1 import DataFileTypeV1, DataSourceTypeV1, ObjectChangeTypeV1

__all__ = (
    'ChangelogMixinV1',
    'SyncedDataMixinV1',
)


@strawberry.type
class ChangelogMixinV1:

    @strawberry_django.field
    def changelog(self, info: Info) -> List[Annotated['ObjectChangeTypeV1', strawberry.lazy('.types_v1')]]:  # noqa: F821
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.request.user, 'view')


@strawberry.type
class SyncedDataMixinV1:
    data_source: Annotated['DataSourceTypeV1', strawberry.lazy('core.graphql.types_v1')] | None
    data_file: Annotated['DataFileTypeV1', strawberry.lazy('core.graphql.types_v1')] | None
