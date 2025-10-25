from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1
from extras import models
from extras.graphql.filter_mixins_v1 import TagBaseFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1
from netbox.graphql.filter_mixins_v1 import PrimaryModelFilterMixinV1, SyncedDataFilterMixinV1

if TYPE_CHECKING:
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from dcim.graphql.filters_v1 import (
        DeviceRoleFilterV1,
        DeviceTypeFilterV1,
        LocationFilterV1,
        PlatformFilterV1,
        RegionFilterV1,
        SiteFilterV1,
        SiteGroupFilterV1,
    )
    from tenancy.graphql.filters_v1 import TenantFilterV1, TenantGroupFilterV1
    from netbox.graphql.enums import ColorEnum
    from netbox.graphql.filter_lookups import FloatLookup, IntegerLookup, JSONFilter, StringArrayLookup, TreeNodeFilter
    from virtualization.graphql.filters_v1 import ClusterFilterV1, ClusterGroupFilterV1, ClusterTypeFilterV1
    from .enums import *

__all__ = (
    'ConfigContextFilterV1',
    'ConfigContextProfileFilterV1',
    'ConfigTemplateFilterV1',
    'CustomFieldFilterV1',
    'CustomFieldChoiceSetFilterV1',
    'CustomLinkFilterV1',
    'EventRuleFilterV1',
    'ExportTemplateFilterV1',
    'ImageAttachmentFilterV1',
    'JournalEntryFilterV1',
    'NotificationGroupFilterV1',
    'SavedFilterFilterV1',
    'TableConfigFilterV1',
    'TagFilterV1',
    'WebhookFilterV1',
)


@strawberry_django.filter_type(models.ConfigContext, lookups=True)
class ConfigContextFilterV1(BaseObjectTypeFilterMixinV1, SyncedDataFilterMixinV1, ChangeLogFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    is_active: FilterLookup[bool] | None = strawberry_django.filter_field()
    regions: Annotated['RegionFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    region_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    site_groups: Annotated['SiteGroupFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    site_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    sites: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    locations: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    device_types: Annotated['DeviceTypeFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    roles: Annotated['DeviceRoleFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    platforms: Annotated['PlatformFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cluster_types: Annotated['ClusterTypeFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    cluster_groups: Annotated['ClusterGroupFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    clusters: Annotated['ClusterFilterV1', strawberry.lazy('virtualization.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tenant_groups: Annotated['TenantGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tenant_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    tenants: Annotated['TenantFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tags: Annotated['TagFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConfigContextProfile, lookups=True)
class ConfigContextProfileFilterV1(SyncedDataFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] = strawberry_django.filter_field()
    description: FilterLookup[str] = strawberry_django.filter_field()
    tags: Annotated['TagFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ConfigTemplate, lookups=True)
class ConfigTemplateFilterV1(BaseObjectTypeFilterMixinV1, SyncedDataFilterMixinV1, ChangeLogFilterMixinV1):
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
class CustomFieldFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    type: Annotated['CustomFieldTypeEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    object_types: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    related_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
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
    choice_set: Annotated['CustomFieldChoiceSetFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
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
class CustomFieldChoiceSetFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
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
class CustomLinkFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
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
class ExportTemplateFilterV1(BaseObjectTypeFilterMixinV1, SyncedDataFilterMixinV1, ChangeLogFilterMixinV1):
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
class ImageAttachmentFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
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
class JournalEntryFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
    assigned_object_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    assigned_object_type_id: ID | None = strawberry_django.filter_field()
    assigned_object_id: ID | None = strawberry_django.filter_field()
    created_by: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    kind: Annotated['JournalEntryKindEnum', strawberry.lazy('extras.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.NotificationGroup, lookups=True)
class NotificationGroupFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    groups: Annotated['GroupFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    users: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.SavedFilter, lookups=True)
class SavedFilterFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    user: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
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
class TableConfigFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    user: Annotated['UserFilterV1', strawberry.lazy('users.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    user_id: ID | None = strawberry_django.filter_field()
    weight: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    shared: FilterLookup[bool] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Tag, lookups=True)
class TagFilterV1(BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1, TagBaseFilterMixinV1):
    color: Annotated['ColorEnum', strawberry.lazy('netbox.graphql.enums')] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.Webhook, lookups=True)
class WebhookFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
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
    events: Annotated['EventRuleFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.EventRule, lookups=True)
class EventRuleFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
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
