from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.types import Info

__all__ = (
    'ConfigContextMixin',
    'ContactsMixin',
    'CustomFieldsMixin',
    'ImageAttachmentsMixin',
    'JournalEntriesMixin',
    'TagsMixin',
)

if TYPE_CHECKING:
    from tenancy.graphql.types import ContactAssignmentType

    from .types import ImageAttachmentType, JournalEntryType, TagType


@strawberry.type
class ConfigContextMixin:

    @strawberry_django.field
    def config_context(self) -> strawberry.scalars.JSON:
        return self.get_config_context()


@strawberry.type
class CustomFieldsMixin:

    @strawberry_django.field
    def custom_fields(self) -> strawberry.scalars.JSON:
        return self.custom_field_data


@strawberry.type
class ImageAttachmentsMixin:

    @strawberry_django.field
    def image_attachments(self, info: Info) -> list[Annotated['ImageAttachmentType', strawberry.lazy('.types')]]:
        return self.images.restrict(info.context.request.user, 'view')


@strawberry.type
class JournalEntriesMixin:

    @strawberry_django.field
    def journal_entries(self, info: Info) -> list[Annotated['JournalEntryType', strawberry.lazy('.types')]]:
        return self.journal_entries.all()


@strawberry.type
class TagsMixin:

    tags: list[Annotated['TagType', strawberry.lazy('.types')]]


@strawberry.type
class ContactsMixin:

    contacts: list[Annotated['ContactAssignmentType', strawberry.lazy('tenancy.graphql.types')]]
