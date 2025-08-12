from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django

from core.graphql.mixins import SyncedDataMixin
from extras import models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ContentTypeType, NetBoxObjectType, ObjectType, OrganizationalObjectType
from .filters import *

if TYPE_CHECKING:
    from dcim.graphql.types import (
        DeviceRoleType,
        DeviceType,
        DeviceTypeType,
        LocationType,
        PlatformType,
        RegionType,
        SiteGroupType,
        SiteType,
    )
    from tenancy.graphql.types import TenantGroupType, TenantType
    from users.graphql.types import GroupType, UserType
    from virtualization.graphql.types import ClusterGroupType, ClusterType, ClusterTypeType, VirtualMachineType

__all__ = (
    'ConfigContextProfileType',
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
    'TableConfigType',
    'TagType',
    'WebhookType',
)


@strawberry_django.type(
    models.ConfigContextProfile,
    fields='__all__',
    filters=ConfigContextProfileFilter,
    pagination=True
)
class ConfigContextProfileType(SyncedDataMixin, NetBoxObjectType):
    pass


@strawberry_django.type(
    models.ConfigContext,
    fields='__all__',
    filters=ConfigContextFilter,
    pagination=True
)
class ConfigContextType(SyncedDataMixin, ObjectType):
    profile: ConfigContextProfileType | None
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
    filters=ConfigTemplateFilter,
    pagination=True
)
class ConfigTemplateType(SyncedDataMixin, TagsMixin, ObjectType):
    virtualmachines: List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    platforms: List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    device_roles: List[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.CustomField,
    fields='__all__',
    filters=CustomFieldFilter,
    pagination=True
)
class CustomFieldType(ObjectType):
    related_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    choice_set: Annotated["CustomFieldChoiceSetType", strawberry.lazy('extras.graphql.types')] | None


@strawberry_django.type(
    models.CustomFieldChoiceSet,
    exclude=['extra_choices'],
    filters=CustomFieldChoiceSetFilter,
    pagination=True
)
class CustomFieldChoiceSetType(ObjectType):

    choices_for: List[Annotated["CustomFieldType", strawberry.lazy('extras.graphql.types')]]
    extra_choices: List[List[str]] | None


@strawberry_django.type(
    models.CustomLink,
    fields='__all__',
    filters=CustomLinkFilter,
    pagination=True
)
class CustomLinkType(ObjectType):
    pass


@strawberry_django.type(
    models.ExportTemplate,
    fields='__all__',
    filters=ExportTemplateFilter,
    pagination=True
)
class ExportTemplateType(SyncedDataMixin, ObjectType):
    pass


@strawberry_django.type(
    models.ImageAttachment,
    fields='__all__',
    filters=ImageAttachmentFilter,
    pagination=True
)
class ImageAttachmentType(BaseObjectType):
    object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None


@strawberry_django.type(
    models.JournalEntry,
    fields='__all__',
    filters=JournalEntryFilter,
    pagination=True
)
class JournalEntryType(CustomFieldsMixin, TagsMixin, ObjectType):
    assigned_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    created_by: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Notification,
    # filters=NotificationFilter
    pagination=True
)
class NotificationType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.NotificationGroup,
    filters=NotificationGroupFilter,
    pagination=True
)
class NotificationGroupType(ObjectType):
    users: List[Annotated["UserType", strawberry.lazy('users.graphql.types')]]
    groups: List[Annotated["GroupType", strawberry.lazy('users.graphql.types')]]


@strawberry_django.type(
    models.SavedFilter,
    exclude=['content_types',],
    filters=SavedFilterFilter,
    pagination=True
)
class SavedFilterType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Subscription,
    # filters=NotificationFilter
    pagination=True
)
class SubscriptionType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.TableConfig,
    fields='__all__',
    filters=TableConfigFilter,
    pagination=True
)
class TableConfigType(ObjectType):
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Tag,
    exclude=['extras_taggeditem_items', ],
    filters=TagFilter,
    pagination=True
)
class TagType(ObjectType):
    color: str

    object_types: List[ContentTypeType]


@strawberry_django.type(
    models.Webhook,
    exclude=['content_types',],
    filters=WebhookFilter,
    pagination=True
)
class WebhookType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.EventRule,
    exclude=['content_types',],
    filters=EventRuleFilter,
    pagination=True
)
class EventRuleType(OrganizationalObjectType):
    action_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
