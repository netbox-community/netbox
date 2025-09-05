from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins import BaseObjectTypeFilterMixin, ChangeLogFilterMixin
from extras import models
from extras.graphql.filter_mixins import TagBaseFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin
from netbox.graphql.filter_mixins import PrimaryModelFilterMixin, SyncedDataFilterMixin

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from dcim.graphql.filters import (
        DeviceRoleFilter, DeviceTypeFilter, LocationFilter, PlatformFilter, RegionFilter, SiteFilter, SiteGroupFilter,
    )
    from tenancy.graphql.filters import TenantFilter, TenantGroupFilter
    from netbox.graphql.enums import ColorEnum
    from netbox.graphql.filter_lookups import FloatLookup, IntegerLookup, JSONFilter, StringArrayLookup, TreeNodeFilter
    from users.graphql.filters import GroupFilter, UserFilter
    from virtualization.graphql.filters import ClusterFilter, ClusterGroupFilter, ClusterTypeFilter
    from .enums import *

__all__ = (
    'ConfigContextFilter',
    'ConfigContextProfileFilter',
    'ConfigTemplateFilter',
    'CustomFieldFilter',
    'CustomFieldChoiceSetFilter',
    'CustomLinkFilter',
    'EventRuleFilter',
    'ExportTemplateFilter',
    'ImageAttachmentFilter',
    'JournalEntryFilter',
    'NotificationGroupFilter',
    'SavedFilterFilter',
    'TableConfigFilter',
    'TagFilter',
    'WebhookFilter',
)


@strawberry_django.filter_type(models.ConfigContext, lookups=True)
class ConfigContextFilter(BaseObjectTypeFilterMixin, SyncedDataFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    regions: Annotated['RegionFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    region_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    site_groups: Annotated['SiteGroupFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    site_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sites: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = strawberry_django.filter_field()
    locations: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    device_types: Annotated['DeviceTypeFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    roles: Annotated['DeviceRoleFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    platforms: Annotated['PlatformFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cluster_types: Annotated['ClusterTypeFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    cluster_groups: Annotated['ClusterGroupFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    clusters: Annotated['ClusterFilter', strawberry.lazy('virtualization.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_groups: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenants: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()
    data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConfigContextProfile, lookups=True)
class ConfigContextProfileFilter(SyncedDataFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] = strawberry_django.filter_field()
    description: FilterLookup[str] = strawberry_django.filter_field()
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ConfigTemplate, lookups=True)
class ConfigTemplateFilter(BaseObjectTypeFilterMixin, SyncedDataFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    template_code: FilterLookup[str] | None = strawberry_django.filter_field()
    environment_params: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    mime_type: FilterLookup[str] | None = strawberry_django.filter_field()
    file_name: FilterLookup[str] | None = strawberry_django.filter_field()
    file_extension: FilterLookup[str] | None = strawberry_django.filter_field()
    as_attachment: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.CustomField, lookups=True)
class CustomFieldFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    type: Annotated['CustomFieldTypeEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    object_types: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    related_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    label: FilterLookup[str] | None = strawberry_django.filter_field()
    group_name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    required: FilterLookup[bool] | None = strawberry_django.filter_field()
    unique: FilterLookup[bool] | None = strawberry_django.filter_field()
    search_weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    filter_logic: Annotated['CustomFieldFilterLogicEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    default: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    related_object_filter: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    validation_minimum: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    validation_maximum: Annotated['FloatLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    validation_regex: FilterLookup[str] | None = strawberry_django.filter_field()
    choice_set: Annotated['CustomFieldChoiceSetFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    choice_set_id: ID | None = strawberry_django.filter_field()
    ui_visible: Annotated['CustomFieldUIVisibleEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    ui_editable: Annotated['CustomFieldUIEditableEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    is_cloneable: FilterLookup[bool] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.CustomFieldChoiceSet, lookups=True)
class CustomFieldChoiceSetFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    base_choices: Annotated['CustomFieldChoiceSetBaseEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    extra_choices: Annotated['StringArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    order_alphabetically: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.CustomLink, lookups=True)
class CustomLinkFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    link_text: FilterLookup[str] | None = strawberry_django.filter_field()
    link_url: FilterLookup[str] | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    group_name: FilterLookup[str] | None = strawberry_django.filter_field()
    button_class: Annotated['CustomLinkButtonClassEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    new_window: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ExportTemplate, lookups=True)
class ExportTemplateFilter(BaseObjectTypeFilterMixin, SyncedDataFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    template_code: FilterLookup[str] | None = strawberry_django.filter_field()
    environment_params: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    mime_type: FilterLookup[str] | None = strawberry_django.filter_field()
    file_name: FilterLookup[str] | None = strawberry_django.filter_field()
    file_extension: FilterLookup[str] | None = strawberry_django.filter_field()
    as_attachment: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ImageAttachment, lookups=True)
class ImageAttachmentFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    object_id: ID | None = strawberry_django.filter_field()
    image_height: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    image_width: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.JournalEntry, lookups=True)
class JournalEntryFilter(BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin):
    assigned_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type_id: ID | None = strawberry_django.filter_field()
    assigned_object_id: ID | None = strawberry_django.filter_field()
    created_by: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    kind: Annotated['JournalEntryKindEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.NotificationGroup, lookups=True)
class NotificationGroupFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    users: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.SavedFilter, lookups=True)
class SavedFilterFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_id: ID | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    shared: FilterLookup[bool] | None = strawberry_django.filter_field()
    parameters: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.TableConfig, lookups=True)
class TableConfigFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_id: ID | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    shared: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Tag, lookups=True)
class TagFilter(BaseObjectTypeFilterMixin, ChangeLogFilterMixin, TagBaseFilterMixin):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Webhook, lookups=True)
class WebhookFilter(BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    payload_url: FilterLookup[str] | None = strawberry_django.filter_field()
    http_method: Annotated['WebhookHttpMethodEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    http_content_type: FilterLookup[str] | None = strawberry_django.filter_field()
    additional_headers: FilterLookup[str] | None = strawberry_django.filter_field()
    body_template: FilterLookup[str] | None = strawberry_django.filter_field()
    secret: FilterLookup[str] | None = strawberry_django.filter_field()
    ssl_verification: FilterLookup[bool] | None = strawberry_django.filter_field()
    ca_file_path: FilterLookup[str] | None = strawberry_django.filter_field()
    events: Annotated['EventRuleFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.EventRule, lookups=True)
class EventRuleFilter(BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    event_types: Annotated['StringArrayLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    conditions: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    action_type: Annotated['EventRuleActionEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    action_object_type: FilterLookup[str] | None = strawberry_django.filter_field()
    action_object_type_id: ID | None = strawberry_django.filter_field()
    action_object_id: ID | None = strawberry_django.filter_field()
    action_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
