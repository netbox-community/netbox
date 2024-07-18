from typing import Annotated, List

import strawberry
import strawberry_django

from extras import models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ContentTypeType, ObjectType, OrganizationalObjectType
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
    'NotificationGroupType',
    'NotificationType',
    'SavedFilterType',
    'SubscriptionType',
    'TagType',
    'WebhookType',
)


@strawberry_django.type(
    models.ConfigContext,
    fields='__all__',
    filters=ConfigContextFilter
)
class ConfigContextType(ObjectType):
    data_source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated["DataFileType", strawberry.lazy('core.graphql.types')] | None

    roles: List[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]
    device_types: List[Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]]
    tags: List[Annotated["TagType", strawberry.lazy('extras.graphql.types')]]
    platforms: List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    regions: List[Annotated["RegionType", strawberry.lazy('dcim.graphql.types')]]
    cluster_groups: List[Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')]]
    tenant_groups: List[Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]]
    cluster_types: List[Annotated["ClusterTypeType", strawberry.lazy('virtualization.graphql.types')]]
    clusters: List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]
    locations: List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]
    sites: List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]
    tenants: List[Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')]]
    site_groups: List[Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.ConfigTemplate,
    fields='__all__',
    filters=ConfigTemplateFilter
)
class ConfigTemplateType(TagsMixin, ObjectType):
    data_source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated["DataFileType", strawberry.lazy('core.graphql.types')] | None

    virtualmachines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    platforms: List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    device_roles: List[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.CustomField,
    fields='__all__',
    filters=CustomFieldFilter
)
class CustomFieldType(ObjectType):
    related_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    choice_set: Annotated["CustomFieldChoiceSetType", strawberry.lazy('extras.graphql.types')] | None


@strawberry_django.type(
    models.CustomFieldChoiceSet,
    exclude=('extra_choices', ),
    filters=CustomFieldChoiceSetFilter
)
class CustomFieldChoiceSetType(ObjectType):

    choices_for: List[Annotated["CustomFieldType", strawberry.lazy('extras.graphql.types')]]
    extra_choices: List[str] | None


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
    data_source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated["DataFileType", strawberry.lazy('core.graphql.types')] | None


@strawberry_django.type(
    models.ImageAttachment,
    fields='__all__',
    filters=ImageAttachmentFilter
)
class ImageAttachmentType(BaseObjectType):
    object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None


@strawberry_django.type(
    models.JournalEntry,
    fields='__all__',
    filters=JournalEntryFilter
)
class JournalEntryType(CustomFieldsMixin, TagsMixin, ObjectType):
    assigned_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    created_by: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Notification,
    # filters=NotificationFilter
)
class NotificationType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.NotificationGroup,
    filters=NotificationGroupFilter
)
class NotificationGroupType(ObjectType):
    users: List[Annotated["UserType", strawberry.lazy('users.graphql.types')]]
    groups: List[Annotated["GroupType", strawberry.lazy('users.graphql.types')]]


@strawberry_django.type(
    models.SavedFilter,
    exclude=['content_types',],
    filters=SavedFilterFilter
)
class SavedFilterType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Subscription,
    # filters=NotificationFilter
)
class SubscriptionType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Tag,
    exclude=['extras_taggeditem_items', ],
    filters=TagFilter
)
class TagType(ObjectType):
    color: str

    object_types: List[ContentTypeType]


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
    action_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
