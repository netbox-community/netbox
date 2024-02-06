import strawberry
import strawberry_django

import strawberry
from strawberry import auto
import strawberry_django

from extras import models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ObjectType, OrganizationalObjectType
from .filters import *

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


@strawberry_django.type(
    models.ConfigContext,
    fields='__all__',
    filters=ConfigContextFilter
)
class ConfigContextType(ObjectType):
    pass


@strawberry_django.type(
    models.ConfigTemplate,
    fields='__all__',
    filters=ConfigTemplateFilter
)
class ConfigTemplateType(TagsMixin, ObjectType):
    pass


@strawberry_django.type(
    models.CustomField,
    fields='__all__',
    filters=CustomFieldFilter
)
class CustomFieldType(ObjectType):
    pass


@strawberry_django.type(
    models.CustomFieldChoiceSet,
    fields='__all__',
    filters=CustomFieldChoiceSetFilter
)
class CustomFieldChoiceSetType(ObjectType):
    pass


@strawberry_django.type(
    models.CustomLink,
    fields='__all__',
    filters=CustomLinkFilter
)
class CustomLinkType(ObjectType):
    pass


@strawberry_django.type(
    models.ExportTemplate,
    fields='__all__',
    filters=ExportTemplateFilter
)
class ExportTemplateType(ObjectType):
    pass


@strawberry_django.type(
    models.ImageAttachment,
    fields='__all__',
    filters=ImageAttachmentFilter
)
class ImageAttachmentType(BaseObjectType):
    pass


@strawberry_django.type(
    models.JournalEntry,
    fields='__all__',
    filters=JournalEntryFilter
)
class JournalEntryType(CustomFieldsMixin, TagsMixin, ObjectType):
    pass


@strawberry_django.type(
    models.ObjectChange,
    fields='__all__',
    filters=ObjectChangeFilter
)
class ObjectChangeType(BaseObjectType):
    pass


@strawberry_django.type(
    models.SavedFilter,
    exclude=['content_types',],
    filters=SavedFilterFilter
)
class SavedFilterType(ObjectType):
    pass


@strawberry_django.type(
    models.Tag,
    exclude=['extras_taggeditem_items', 'color'],  # bug - remove color from exclude
    filters=TagFilter
)
class TagType(ObjectType):
    pass


@strawberry_django.type(
    models.Webhook,
    exclude=['content_types',],
    filters=WebhookFilter
)
class WebhookType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.EventRule,
    exclude=['content_types',],
    filters=EventRuleFilter
)
class EventRuleType(OrganizationalObjectType):
    pass
