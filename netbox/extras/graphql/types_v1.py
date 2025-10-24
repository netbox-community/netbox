from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django

from core.graphql.mixins_v1 import SyncedDataMixinV1
from extras import models
from extras.graphql.mixins_v1 import CustomFieldsMixinV1, TagsMixinV1
from netbox.graphql.types_v1 import (
    BaseObjectTypeV1, ContentTypeTypeV1, NetBoxObjectTypeV1, ObjectTypeV1, OrganizationalObjectTypeV1
)
from .filters_v1 import *

if TYPE_CHECKING:
    from dcim.graphql.types_v1 import (
        DeviceRoleTypeV1,
        DeviceTypeV1,
        DeviceTypeTypeV1,
        LocationTypeV1,
        PlatformTypeV1,
        RegionTypeV1,
        SiteGroupTypeV1,
        SiteTypeV1,
    )
    from tenancy.graphql.types_v1 import TenantGroupTypeV1, TenantTypeV1
    from users.graphql.types_v1 import GroupTypeV1, UserTypeV1
    from virtualization.graphql.types_v1 import (
        ClusterGroupTypeV1, ClusterTypeV1, ClusterTypeTypeV1, VirtualMachineTypeV1
    )

__all__ = (
    'ConfigContextProfileTypeV1',
    'ConfigContextTypeV1',
    'ConfigTemplateTypeV1',
    'CustomFieldChoiceSetTypeV1',
    'CustomFieldTypeV1',
    'CustomLinkTypeV1',
    'EventRuleTypeV1',
    'ExportTemplateTypeV1',
    'ImageAttachmentTypeV1',
    'JournalEntryTypeV1',
    'NotificationGroupTypeV1',
    'NotificationTypeV1',
    'SavedFilterTypeV1',
    'SubscriptionTypeV1',
    'TableConfigTypeV1',
    'TagTypeV1',
    'WebhookTypeV1',
)


@strawberry_django.type(
    models.ConfigContextProfile,
    fields='__all__',
    filters=ConfigContextProfileFilterV1,
    pagination=True
)
class ConfigContextProfileTypeV1(SyncedDataMixinV1, NetBoxObjectTypeV1):
    pass


@strawberry_django.type(
    models.ConfigContext,
    fields='__all__',
    filters=ConfigContextFilterV1,
    pagination=True
)
class ConfigContextTypeV1(SyncedDataMixinV1, ObjectTypeV1):
    profile: ConfigContextProfileTypeV1 | None
    roles: List[Annotated["DeviceRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    device_types: List[Annotated["DeviceTypeTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    tags: List[Annotated["TagTypeV1", strawberry.lazy('extras.graphql.types_v1')]]
    platforms: List[Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    regions: List[Annotated["RegionTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    cluster_groups: List[Annotated["ClusterGroupTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    tenant_groups: List[Annotated["TenantGroupTypeV1", strawberry.lazy('tenancy.graphql.types_v1')]]
    cluster_types: List[Annotated["ClusterTypeTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    clusters: List[Annotated["ClusterTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    locations: List[Annotated["LocationTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    sites: List[Annotated["SiteTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    tenants: List[Annotated["TenantTypeV1", strawberry.lazy('tenancy.graphql.types_v1')]]
    site_groups: List[Annotated["SiteGroupTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.ConfigTemplate,
    fields='__all__',
    filters=ConfigTemplateFilterV1,
    pagination=True
)
class ConfigTemplateTypeV1(SyncedDataMixinV1, TagsMixinV1, ObjectTypeV1):
    virtualmachines: List[Annotated["VirtualMachineTypeV1", strawberry.lazy('virtualization.graphql.types_v1')]]
    devices: List[Annotated["DeviceTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    platforms: List[Annotated["PlatformTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]
    device_roles: List[Annotated["DeviceRoleTypeV1", strawberry.lazy('dcim.graphql.types_v1')]]


@strawberry_django.type(
    models.CustomField,
    fields='__all__',
    filters=CustomFieldFilterV1,
    pagination=True
)
class CustomFieldTypeV1(ObjectTypeV1):
    related_object_type: Annotated["ContentTypeTypeV1", strawberry.lazy('netbox.graphql.types_v1')] | None
    choice_set: Annotated["CustomFieldChoiceSetTypeV1", strawberry.lazy('extras.graphql.types_v1')] | None


@strawberry_django.type(
    models.CustomFieldChoiceSet,
    exclude=['extra_choices'],
    filters=CustomFieldChoiceSetFilterV1,
    pagination=True
)
class CustomFieldChoiceSetTypeV1(ObjectTypeV1):

    choices_for: List[Annotated["CustomFieldTypeV1", strawberry.lazy('extras.graphql.types_v1')]]
    extra_choices: List[List[str]] | None


@strawberry_django.type(
    models.CustomLink,
    fields='__all__',
    filters=CustomLinkFilterV1,
    pagination=True
)
class CustomLinkTypeV1(ObjectTypeV1):
    pass


@strawberry_django.type(
    models.ExportTemplate,
    fields='__all__',
    filters=ExportTemplateFilterV1,
    pagination=True
)
class ExportTemplateTypeV1(SyncedDataMixinV1, ObjectTypeV1):
    pass


@strawberry_django.type(
    models.ImageAttachment,
    fields='__all__',
    filters=ImageAttachmentFilterV1,
    pagination=True
)
class ImageAttachmentTypeV1(BaseObjectTypeV1):
    object_type: Annotated["ContentTypeTypeV1", strawberry.lazy('netbox.graphql.types_v1')] | None


@strawberry_django.type(
    models.JournalEntry,
    fields='__all__',
    filters=JournalEntryFilterV1,
    pagination=True
)
class JournalEntryTypeV1(CustomFieldsMixinV1, TagsMixinV1, ObjectTypeV1):
    assigned_object_type: Annotated["ContentTypeTypeV1", strawberry.lazy('netbox.graphql.types_v1')] | None
    created_by: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')] | None


@strawberry_django.type(
    models.Notification,
    # filters=NotificationFilter
    pagination=True
)
class NotificationTypeV1(ObjectTypeV1):
    user: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')] | None


@strawberry_django.type(
    models.NotificationGroup,
    filters=NotificationGroupFilterV1,
    pagination=True
)
class NotificationGroupTypeV1(ObjectTypeV1):
    users: List[Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')]]
    groups: List[Annotated["GroupTypeV1", strawberry.lazy('users.graphql.types_v1')]]


@strawberry_django.type(
    models.SavedFilter,
    exclude=['content_types',],
    filters=SavedFilterFilterV1,
    pagination=True
)
class SavedFilterTypeV1(ObjectTypeV1):
    user: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')] | None


@strawberry_django.type(
    models.Subscription,
    # filters=NotificationFilter
    pagination=True
)
class SubscriptionTypeV1(ObjectTypeV1):
    user: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')] | None


@strawberry_django.type(
    models.TableConfig,
    fields='__all__',
    filters=TableConfigFilterV1,
    pagination=True
)
class TableConfigTypeV1(ObjectTypeV1):
    user: Annotated["UserTypeV1", strawberry.lazy('users.graphql.types_v1')] | None


@strawberry_django.type(
    models.Tag,
    exclude=['extras_taggeditem_items', ],
    filters=TagFilterV1,
    pagination=True
)
class TagTypeV1(ObjectTypeV1):
    color: str

    object_types: List[ContentTypeTypeV1]


@strawberry_django.type(
    models.Webhook,
    exclude=['content_types',],
    filters=WebhookFilterV1,
    pagination=True
)
class WebhookTypeV1(OrganizationalObjectTypeV1):
    pass


@strawberry_django.type(
    models.EventRule,
    exclude=['content_types',],
    filters=EventRuleFilterV1,
    pagination=True
)
class EventRuleTypeV1(OrganizationalObjectTypeV1):
    action_object_type: Annotated["ContentTypeTypeV1", strawberry.lazy('netbox.graphql.types_v1')] | None
