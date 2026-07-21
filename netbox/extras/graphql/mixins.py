from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry.types import Info

from extras.models import ImageAttachment, JournalEntry
from utilities.querysets import RestrictedPrefetch

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

        # When `config_context` is requested, annotate the aggregated context data — but only for
        # rows whose pre-rendered cache (`_config_context_data`) is invalidated (NULL). Warm rows
        # are served from the cache by get_config_context() and skip the subquery entirely
        # (PostgreSQL short-circuits the CASE), so resolving config_context across a list of objects
        # with cold caches no longer incurs a per-object fallback query.
        selected = {f.name for f in info.selected_fields[0].selections}
        if 'config_context' in selected and hasattr(queryset, 'annotate_config_context_data'):
            return queryset.annotate_config_context_data(only_invalidated=True)

        return queryset

    # Ensure both the pre-rendered cache and `local_context_data` are fetched when `config_context`
    # is requested, so the warm-cache read path requires no additional queries.
    @strawberry_django.field(only=['_config_context_data', 'local_context_data'])
    def config_context(self) -> strawberry.scalars.JSON:
        return self.get_config_context()


@strawberry.type
class CustomFieldsMixin:

    @strawberry_django.field
    def custom_fields(self) -> strawberry.scalars.JSON:
        return self.custom_field_data


@strawberry.type
class ImageAttachmentsMixin:

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            'images', info.context.request.user, 'view', queryset=ImageAttachment.objects.all()
        ),
    )
    def image_attachments(self) -> list[Annotated['ImageAttachmentType', strawberry.lazy('.types')]]:
        return self.images.all()


@strawberry.type
class JournalEntriesMixin:

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            'journal_entries', info.context.request.user, 'view', queryset=JournalEntry.objects.all()
        ),
    )
    def journal_entries(self) -> list[Annotated['JournalEntryType', strawberry.lazy('.types')]]:
        return self.journal_entries.all()


@strawberry.type
class TagsMixin:

    tags: list[Annotated['TagType', strawberry.lazy('.types')]] = strawberry_django.field(
        prefetch_related=['tags'],
    )


@strawberry.type
class ContactsMixin:

    contacts: list[Annotated['ContactAssignmentType', strawberry.lazy('tenancy.graphql.types')]]
