import graphene
from graphene.types.generic import GenericScalar

__all__ = (
    'CustomFieldsMixin',
    'ImageAttachmentsMixin',
    'JournalEntriesMixin',
    'TagsMixin',
)


class CustomFieldsMixin:
    custom_fields = GenericScalar()

    def resolve_custom_fields(self, info):
        return self.custom_field_data


class ImageAttachmentsMixin:
    image_attachments = graphene.List('extras.graphql.types.ImageAttachmentType')

    def resolve_image_attachments(self, info):
        return self.images.restrict(info.context.user, 'view')


class JournalEntriesMixin:
    journal_entries = graphene.List('extras.graphql.types.JournalEntryType')

    def resolve_journal_entries(self, info):
        return self.journal_entries.restrict(info.context.user, 'view')


class TagsMixin:
    tags = graphene.List(graphene.String)

    def resolve_tags(self, info):
        return self.tags.all()
