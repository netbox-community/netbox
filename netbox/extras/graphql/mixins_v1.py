from typing import TYPE_CHECKING, Annotated, List

import strawberry
import strawberry_django
from strawberry.types import Info

__all__ = (
    'ConfigContextMixinV1',
    'ContactsMixinV1',
    'CustomFieldsMixinV1',
    'ImageAttachmentsMixinV1',
    'JournalEntriesMixinV1',
    'TagsMixinV1',
)

if TYPE_CHECKING:
    from .types_v1 import ImageAttachmentTypeV1, JournalEntryTypeV1, TagTypeV1
    from tenancy.graphql.types_v1 import ContactAssignmentTypeV1


@strawberry.type
class ConfigContextMixinV1:

    @strawberry_django.field
    def config_context(self) -> strawberry.scalars.JSON:
        return self.get_config_context()


@strawberry.type
class CustomFieldsMixinV1:

    @strawberry_django.field
    def custom_fields(self) -> strawberry.scalars.JSON:
        return self.custom_field_data


@strawberry.type
class ImageAttachmentsMixinV1:

    @strawberry_django.field
    def image_attachments(self, info: Info) -> List[Annotated['ImageAttachmentTypeV1', strawberry.lazy('.types_v1')]]:
        return self.images.restrict(info.context.request.user, 'view')


@strawberry.type
class JournalEntriesMixinV1:

    @strawberry_django.field
    def journal_entries(self, info: Info) -> List[Annotated['JournalEntryTypeV1', strawberry.lazy('.types_v1')]]:
        return self.journal_entries.all()


@strawberry.type
class TagsMixinV1:

    tags: List[Annotated['TagTypeV1', strawberry.lazy('.types_v1')]]


@strawberry.type
class ContactsMixinV1:

    contacts: List[Annotated['ContactAssignmentTypeV1', strawberry.lazy('tenancy.graphql.types_v1')]]
