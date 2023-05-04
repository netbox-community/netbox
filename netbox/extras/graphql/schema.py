import graphene

from extras import models
from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer


class ExtrasQuery(graphene.ObjectType):
    config_context = ObjectField(ConfigContextType)
    config_context_list = ObjectListField(ConfigContextType)

    def resolve_config_context_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConfigContext.objects.all(), info)

    config_template = ObjectField(ConfigTemplateType)
    config_template_list = ObjectListField(ConfigTemplateType)

    def resolve_config_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ConfigTemplate.objects.all(), info)

    custom_field = ObjectField(CustomFieldType)
    custom_field_list = ObjectListField(CustomFieldType)

    def resolve_custom_field_list(root, info, **kwargs):
        return gql_query_optimizer(models.CustomField.objects.all(), info)

    custom_link = ObjectField(CustomLinkType)
    custom_link_list = ObjectListField(CustomLinkType)

    def resolve_custom_link_list(root, info, **kwargs):
        return gql_query_optimizer(models.CustomLink.objects.all(), info)

    export_template = ObjectField(ExportTemplateType)
    export_template_list = ObjectListField(ExportTemplateType)

    def resolve_export_template_list(root, info, **kwargs):
        return gql_query_optimizer(models.ExportTemplate.objects.all(), info)

    image_attachment = ObjectField(ImageAttachmentType)
    image_attachment_list = ObjectListField(ImageAttachmentType)

    def resolve_image_attachment_list(root, info, **kwargs):
        return gql_query_optimizer(models.ImageAttachment.objects.all(), info)

    saved_filter = ObjectField(SavedFilterType)
    saved_filter_list = ObjectListField(SavedFilterType)

    def resolve_saved_filter_list(root, info, **kwargs):
        return gql_query_optimizer(models.SavedFilter.objects.all(), info)

    journal_entry = ObjectField(JournalEntryType)
    journal_entry_list = ObjectListField(JournalEntryType)

    def resolve_journal_entry_list(root, info, **kwargs):
        return gql_query_optimizer(models.JournalEntry.objects.all(), info)

    tag = ObjectField(TagType)
    tag_list = ObjectListField(TagType)

    def resolve_tag_list(root, info, **kwargs):
        return gql_query_optimizer(models.Tag.objects.all(), info)

    webhook = ObjectField(WebhookType)
    webhook_list = ObjectListField(WebhookType)

    def resolve_webhook_list(root, info, **kwargs):
        return gql_query_optimizer(models.Webhook.objects.all(), info)
