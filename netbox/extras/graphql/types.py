from extras import filtersets, models
from netbox.graphql.types import BaseObjectType

__all__ = (
    'ConfigContextType',
    'CustomFieldType',
    'CustomLinkType',
    'ExportTemplateType',
    'ImageAttachmentType',
    'JournalEntryType',
    'TagType',
    'WebhookType',
)


class ConfigContextType(BaseObjectType):

    class Meta:
        model = models.ConfigContext
        fields = '__all__'
        filterset_class = filtersets.ConfigContextFilterSet


class CustomFieldType(BaseObjectType):

    class Meta:
        model = models.CustomField
        fields = '__all__'
        filterset_class = filtersets.CustomFieldFilterSet


class CustomLinkType(BaseObjectType):

    class Meta:
        model = models.CustomLink
        fields = '__all__'
        filterset_class = filtersets.CustomLinkFilterSet


class ExportTemplateType(BaseObjectType):

    class Meta:
        model = models.ExportTemplate
        fields = '__all__'
        filterset_class = filtersets.ExportTemplateFilterSet


class ImageAttachmentType(BaseObjectType):

    class Meta:
        model = models.ImageAttachment
        fields = '__all__'
        filterset_class = filtersets.ImageAttachmentFilterSet


class JournalEntryType(BaseObjectType):

    class Meta:
        model = models.JournalEntry
        fields = '__all__'
        filterset_class = filtersets.JournalEntryFilterSet


class TagType(BaseObjectType):

    class Meta:
        model = models.Tag
        fields = '__all__'
        filterset_class = filtersets.TagFilterSet


class WebhookType(BaseObjectType):

    class Meta:
        model = models.Webhook
        fields = '__all__'
        filterset_class = filtersets.WebhookFilterSet
