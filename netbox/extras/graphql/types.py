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
    data_source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated["DataFileType", strawberry.lazy('core.graphql.types')] | None

    @strawberry_django.field
    def roles(self) -> List[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]:
        return self.roles.all()

    @strawberry_django.field
    def device_types(self) -> List[Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')]]:
        return self.device_types.all()

    @strawberry_django.field
    def tags(self) -> List[Annotated["TagType", strawberry.lazy('extras.graphql.types')]]:
        return self.tags.all()

    @strawberry_django.field
    def platforms(self) -> List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]:
        return self.platforms.all()

    @strawberry_django.field
    def regions(self) -> List[Annotated["RegionType", strawberry.lazy('dcim.graphql.types')]]:
        return self.regions.all()

    @strawberry_django.field
    def cluster_groups(self) -> List[Annotated["ClusterGroupType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_groups.all()

    @strawberry_django.field
    def tenant_groups(self) -> List[Annotated["TenantGroupType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.tenant_groups.all()

    @strawberry_django.field
    def cluster_types(self) -> List[Annotated["ClusterTypeType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.cluster_types.all()

    @strawberry_django.field
    def clusters(self) -> List[Annotated["ClusterType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.clusters.all()

    @strawberry_django.field
    def locations(self) -> List[Annotated["LocationType", strawberry.lazy('dcim.graphql.types')]]:
        return self.locations.all()

    @strawberry_django.field
    def sites(self) -> List[Annotated["SiteType", strawberry.lazy('dcim.graphql.types')]]:
        return self.sites.all()

    @strawberry_django.field
    def tenants(self) -> List[Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')]]:
        return self.tenants.all()

    @strawberry_django.field
    def site_groups(self) -> List[Annotated["SiteGroupType", strawberry.lazy('dcim.graphql.types')]]:
        return self.site_groups.all()


@strawberry_django.type(
    models.ConfigTemplate,
    fields='__all__',
    filters=ConfigTemplateFilter
)
class ConfigTemplateType(TagsMixin, ObjectType):
    data_source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')] | None
    data_file: Annotated["DataFileType", strawberry.lazy('core.graphql.types')] | None

    @strawberry_django.field
    def virtualmachines(self) -> List[Annotated["VirtualMachineType", strawberry.lazy('virtualization.graphql.types')]]:
        return self.virtualmachines.all()

    @strawberry_django.field
    def devices(self) -> List[Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.devices.all()

    @strawberry_django.field
    def platforms(self) -> List[Annotated["PlatformType", strawberry.lazy('dcim.graphql.types')]]:
        return self.platforms.all()

    @strawberry_django.field
    def device_roles(self) -> List[Annotated["DeviceRoleType", strawberry.lazy('dcim.graphql.types')]]:
        return self.device_roles.all()


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

    @strawberry_django.field
    def choices_for(self) -> List[Annotated["CustomFieldType", strawberry.lazy('extras.graphql.types')]]:
        return self.choices_for.all()

    @strawberry_django.field
    def extra_choices(self) -> List[str] | None:
        return list(self.extra_choices)


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
    user: Annotated["UserType", strawberry.lazy('users.graphql.types')] | None


@strawberry_django.type(
    models.Tag,
    exclude=['extras_taggeditem_items', ],
    filters=TagFilter
)
class TagType(ObjectType):
    color: str

    @strawberry_django.field
    def object_types(self) -> List[ContentTypeType]:
        return self.object_types.all()


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
