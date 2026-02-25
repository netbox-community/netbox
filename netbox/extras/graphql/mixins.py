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

    @classmethod
    def get_queryset(cls, queryset, info: Info, **kwargs):
        queryset = super().get_queryset(queryset, info, **kwargs)

        # If `config_context` is requested, call annotate_config_context_data() on the queryset
        selected = {f.name for f in info.selected_fields[0].selections}
        if 'config_context' in selected and hasattr(queryset, 'annotate_config_context_data'):
            return queryset.annotate_config_context_data()

        return queryset

    # Ensure `local_context_data` is fetched when `config_context` is requested
    @strawberry_django.field(only=['local_context_data'])
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
