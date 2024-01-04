import strawberry
import strawberry_django
from typing import TYPE_CHECKING, Annotated, List

from django.contrib.contenttypes.models import ContentType

from extras.models import ObjectChange

__all__ = (
    'ChangelogMixin',
    'ConfigContextMixin',
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
    def changelog(self) -> List[Annotated["ObjectChangeType", strawberry.lazy('.types')]]:
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.user, 'view')


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
    def image_attachments(self) -> List[Annotated["ImageAttachmentType", strawberry.lazy('.types')]]:
        return self.images.restrict(info.context.user, 'view')


@strawberry.type
class JournalEntriesMixin:

    @strawberry_django.field
    def journal_entries(self) -> List[Annotated["JournalEntryType", strawberry.lazy('.types')]]:
        return self.journal_entries.restrict(info.context.user, 'view')


@strawberry.type
class TagsMixin:

    @strawberry_django.field
    def tags(self) -> List[Annotated["TagType", strawberry.lazy('.types')]]:
        return self.tags.all()


@strawberry.type
class ContactsMixin:

    @strawberry_django.field
    def contacts(self) -> List[Annotated["ContactAssignmentType", strawberry.lazy('tenancy.graphql.types')]]:
        return list(self.contacts.all())
