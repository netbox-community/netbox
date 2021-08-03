import graphene
from graphene.types.generic import GenericScalar

__all__ = (
    'ChangelogMixin',
    'CustomFieldsMixin',
    'ImageAttachmentsMixin',
    'JournalEntriesMixin',
    'TagsMixin',
)


class ChangelogMixin:
    changelog = graphene.List('extras.graphql.types.ObjectChangeType')

    def resolve_changelog(self, info):
        return self.object_changes.restrict(info.context.user, 'view')


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
    tags = graphene.List('extras.graphql.types.TagType')

    def resolve_tags(self, info):
        return self.tags.all()
