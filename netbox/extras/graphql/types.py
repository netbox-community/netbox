from extras import filtersets, models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ObjectType, OrganizationalObjectType

__all__ = (
    'ConfigContextType',
    'ConfigTemplateType',
    'CustomFieldChoiceSetType',
    'CustomFieldType',
    'CustomLinkType',
    'EventRuleType',
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


class ConfigTemplateType(TagsMixin, ObjectType):

    class Meta:
        model = models.ConfigTemplate
        fields = '__all__'
        filterset_class = filtersets.ConfigTemplateFilterSet


class CustomFieldType(ObjectType):

    class Meta:
        model = models.CustomField
        exclude = ('object_types', 'object_type')
        filterset_class = filtersets.CustomFieldFilterSet


class CustomFieldChoiceSetType(ObjectType):

    class Meta:
        model = models.CustomFieldChoiceSet
        fields = '__all__'
        filterset_class = filtersets.CustomFieldChoiceSetFilterSet


class CustomLinkType(ObjectType):

    class Meta:
        model = models.CustomLink
        exclude = ('object_types', )
        filterset_class = filtersets.CustomLinkFilterSet


class EventRuleType(OrganizationalObjectType):

    class Meta:
        model = models.EventRule
        exclude = ('object_types',)
        filterset_class = filtersets.EventRuleFilterSet


class ExportTemplateType(ObjectType):

    class Meta:
        model = models.ExportTemplate
        exclude = ('object_types', )
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
        exclude = ('object_types', )
        filterset_class = filtersets.SavedFilterFilterSet


class TagType(ObjectType):

    class Meta:
        model = models.Tag
        exclude = ('extras_taggeditem_items',)
        filterset_class = filtersets.TagFilterSet


class WebhookType(OrganizationalObjectType):

    class Meta:
        model = models.Webhook
        filterset_class = filtersets.WebhookFilterSet
