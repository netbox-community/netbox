import graphene
from django.contrib.contenttypes.models import ContentType
from graphene.types.generic import GenericScalar

from extras.models import ObjectChange

__all__ = (
    'ChangelogMixin',
    'ConfigContextMixin',
    'CustomFieldsMixin',
    'ImageAttachmentsMixin',
    'JournalEntriesMixin',
    'TagsMixin',
)


class ChangelogMixin:
    changelog = graphene.List('extras.graphql.types.ObjectChangeType')

    def resolve_changelog(self, info):
        content_type = ContentType.objects.get_for_model(self)
        object_changes = ObjectChange.objects.filter(
            changed_object_type=content_type,
            changed_object_id=self.pk
        )
        return object_changes.restrict(info.context.user, 'view')


class ConfigContextMixin:
    config_context = GenericScalar()

    def resolve_config_context(self, info):
        return self.get_config_context()


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
