from extras import filtersets, models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ObjectType

__all__ = (
    'ConfigContextType',
    'CustomFieldType',
    'CustomLinkType',
    'ExportTemplateType',
    'ImageAttachmentType',
    'JournalEntryType',
    'ObjectChangeType',
    'SavedFilterType',
    'TagType',
    'WebhookType',
)


class ConfigContextType(ObjectType):

    class Meta:
        model = models.ConfigContext
        fields = '__all__'
        filterset_class = filtersets.ConfigContextFilterSet


class CustomFieldType(ObjectType):

    class Meta:
        model = models.CustomField
        exclude = ('content_types', )
        filterset_class = filtersets.CustomFieldFilterSet


class CustomLinkType(ObjectType):

    class Meta:
        model = models.CustomLink
        exclude = ('content_types', )
        filterset_class = filtersets.CustomLinkFilterSet


class ExportTemplateType(ObjectType):

    class Meta:
        model = models.ExportTemplate
        exclude = ('content_types', )
        filterset_class = filtersets.ExportTemplateFilterSet


class ImageAttachmentType(BaseObjectType):

    class Meta:
        model = models.ImageAttachment
        fields = '__all__'
        filterset_class = filtersets.ImageAttachmentFilterSet


class JournalEntryType(CustomFieldsMixin, TagsMixin, ObjectType):

    class Meta:
        model = models.JournalEntry
        fields = '__all__'
        filterset_class = filtersets.JournalEntryFilterSet


class ObjectChangeType(BaseObjectType):

    class Meta:
        model = models.ObjectChange
        fields = '__all__'
        filterset_class = filtersets.ObjectChangeFilterSet


class SavedFilterType(ObjectType):

    class Meta:
        model = models.SavedFilter
        exclude = ('content_types', )
        filterset_class = filtersets.SavedFilterFilterSet


class TagType(ObjectType):

    class Meta:
        model = models.Tag
        exclude = ('extras_taggeditem_items',)
        filterset_class = filtersets.TagFilterSet


class WebhookType(ObjectType):

    class Meta:
        model = models.Webhook
        exclude = ('content_types', )
        filterset_class = filtersets.WebhookFilterSet
