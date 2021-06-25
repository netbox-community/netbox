import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class ExtrasQuery(graphene.ObjectType):
    config_context = ObjectField(ConfigContextType)
    config_contexts = ObjectListField(ConfigContextType)

    custom_field = ObjectField(CustomFieldType)
    custom_fields = ObjectListField(CustomFieldType)

    custom_link = ObjectField(CustomLinkType)
    custom_links = ObjectListField(CustomLinkType)

    export_template = ObjectField(ExportTemplateType)
    export_templates = ObjectListField(ExportTemplateType)

    image_attachment = ObjectField(ImageAttachmentType)
    image_attachments = ObjectListField(ImageAttachmentType)

    journal_entry = ObjectField(JournalEntryType)
    journal_entries = ObjectListField(JournalEntryType)

    tag = ObjectField(TagType)
    tags = ObjectListField(TagType)

    webhook = ObjectField(WebhookType)
    webhooks = ObjectListField(WebhookType)
