from typing import TYPE_CHECKING, Annotated, List

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType

from extras.models import ObjectChange

__all__ = (
    'ChangelogMixin',
    'ConfigContextMixin',
    'ContactsMixin',
    'CustomFieldsMixin',
    'ImageAttachmentsMixin',
    'JournalEntriesMixin',
    'TagsMixin',
)

if TYPE_CHECKING:
    from .types import ImageAttachmentType, JournalEntryType, ObjectChangeType, TagType
    from tenancy.graphql.types import ContactAssignmentType


@strawberry.type
class ChangelogMixin:

    @strawberry_django.field
    def changelog(self, info) -> List[Annotated["ObjectChangeType", strawberry.lazy('.types')]]:
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.request.user, 'view')


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
    def image_attachments(self, info) -> List[Annotated["ImageAttachmentType", strawberry.lazy('.types')]]:
        return self.images.restrict(info.context.request.user, 'view')


@strawberry.type
class JournalEntriesMixin:

    @strawberry_django.field
    def journal_entries(self, info) -> List[Annotated["JournalEntryType", strawberry.lazy('.types')]]:
        return self.journal_entries.all()


@strawberry.type
class TagsMixin:

    tags: List[Annotated["TagType", strawberry.lazy('.types')]]


@strawberry.type
class ContactsMixin:

    contacts: List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]
