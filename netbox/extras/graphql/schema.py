import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class ExtrasQuery(graphene.ObjectType):
    config_context = ObjectField(ConfigContextType)
    config_context_list = ObjectListField(ConfigContextType)

    custom_field = ObjectField(CustomFieldType)
    custom_field_list = ObjectListField(CustomFieldType)

    custom_link = ObjectField(CustomLinkType)
    custom_link_list = ObjectListField(CustomLinkType)

    export_template = ObjectField(ExportTemplateType)
    export_template_list = ObjectListField(ExportTemplateType)

    image_attachment = ObjectField(ImageAttachmentType)
    image_attachment_list = ObjectListField(ImageAttachmentType)

    journal_entry = ObjectField(JournalEntryType)
    journal_entry_list = ObjectListField(JournalEntryType)

    tag = ObjectField(TagType)
    tag_list = ObjectListField(TagType)

    webhook = ObjectField(WebhookType)
    webhook_list = ObjectListField(WebhookType)
