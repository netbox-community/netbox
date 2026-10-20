from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from extras.models import CustomField, ImageAttachment, JournalEntry
from extras.querysets import ConfigContextDataExpression
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

    # Annotate context data for rows with an invalidated cache, so a list never falls back to a query per object
    @strawberry_django.field(
        only=['_config_context_data', 'local_context_data'],
        annotate={'config_context_data': ConfigContextDataExpression(only_invalidated=True)},
    )
    def config_context(self) -> strawberry.scalars.JSON:
        return self.get_config_context(copy_data=False)


@strawberry.type
class CustomFieldsMixin:

    @strawberry_django.field(only=['custom_field_data'])
    def custom_fields(self) -> strawberry.scalars.JSON:
        # Emit a key for every custom field assigned to the model, as the REST API does, rather than
        # returning the stored data verbatim. A key is materialized only once a value is assigned
        # (see CustomField.populate_initial_data()), so an object which predates a field carries no
        # key for it; without this, such a field would be absent from the response instead of null.
        # CustomFieldManager.get_for_model() is served from the per-request cache, so this costs one
        # query per model rather than one per object.
        return {
            cf.name: cf.resolve_selection_value(self.custom_field_data.get(cf.name))
            for cf in CustomField.objects.get_for_model(self)
        }


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
