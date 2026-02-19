from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

from core.graphql.mixins import SyncedDataMixin
from extras import models
from extras.graphql.mixins import CustomFieldsMixin, TagsMixin
from netbox.graphql.types import BaseObjectType, ContentTypeType, ObjectType, PrimaryObjectType
from users.graphql.mixins import OwnerMixin

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
class ConfigContextProfileType(SyncedDataMixin, PrimaryObjectType):
    pass


@strawberry_django.type(
    models.ConfigContext,
    fields='__all__',
    filters=ConfigContextFilter,
    pagination=True
)
class ConfigContextType(SyncedDataMixin, OwnerMixin, ObjectType):
    profile: ConfigContextProfileType | None
    roles: list[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]
    device_types: list[Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]]
    tags: list[Annotated["TagType", strawberry.lazy('extras.graphql.types')]]
    platforms: list[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    regions: list[Annotated["RegionType", strawberry.lazy('dcim.graphql.types')]]
    cluster_groups: list[Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')]]
    tenant_groups: list[Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]]
    cluster_types: list[Annotated["ClusterTypeType", strawberry.lazy('virtualization.graphql.types')]]
    clusters: list[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]
    locations: list[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]
    sites: list[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]
    tenants: list[Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')]]
    site_groups: list[Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.ConfigTemplate,
    fields='__all__',
    filters=ConfigTemplateFilter,
    pagination=True
)
class ConfigTemplateType(SyncedDataMixin, OwnerMixin, TagsMixin, ObjectType):
    virtualmachines: list[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]
    devices: list[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]
    platforms: list[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]
    device_roles: list[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]


@strawberry_django.type(
    models.CustomField,
    fields='__all__',
    filters=CustomFieldFilter,
    pagination=True
)
class CustomFieldType(OwnerMixin, ObjectType):
    related_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
    choice_set: Annotated["CustomFieldChoiceSetType", strawberry.lazy('extras.graphql.types')] | None


@strawberry_django.type(
    models.CustomFieldChoiceSet,
    exclude=['extra_choices'],
    filters=CustomFieldChoiceSetFilter,
    pagination=True
)
class CustomFieldChoiceSetType(OwnerMixin, ObjectType):

    choices_for: list[Annotated["CustomFieldType", strawberry.lazy('extras.graphql.types')]]
    extra_choices: list[list[str]] | None


@strawberry_django.type(
    models.CustomLink,
    fields='__all__',
    filters=CustomLinkFilter,
    pagination=True
)
class CustomLinkType(OwnerMixin, ObjectType):
    pass


@strawberry_django.type(
    models.ExportTemplate,
    fields='__all__',
    filters=ExportTemplateFilter,
    pagination=True
)
class ExportTemplateType(SyncedDataMixin, OwnerMixin, ObjectType):
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
    users: list[Annotated["UserType", strawberry.lazy('users.graphql.types')]]
    groups: list[Annotated["GroupType", strawberry.lazy('users.graphql.types')]]


@strawberry_django.type(
    models.SavedFilter,
    exclude=['content_types',],
    filters=SavedFilterFilter,
    pagination=True
)
class SavedFilterType(OwnerMixin, ObjectType):
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
class TagType(OwnerMixin, ObjectType):
    color: str

    object_types: list[ContentTypeType]


@strawberry_django.type(
    models.Webhook,
    exclude=['content_types',],
    filters=WebhookFilter,
    pagination=True
)
class WebhookType(OwnerMixin, CustomFieldsMixin, TagsMixin, ObjectType):
    pass


@strawberry_django.type(
    models.EventRule,
    exclude=['content_types',],
    filters=EventRuleFilter,
    pagination=True
)
class EventRuleType(OwnerMixin, CustomFieldsMixin, TagsMixin, ObjectType):
    action_object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')] | None
