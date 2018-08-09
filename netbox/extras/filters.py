from __future__ import unicode_literals

import django_filters
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from taggit.models import Tag

from dcim.models import DeviceRole, Platform, Region, Site
from tenancy.models import Tenant, TenantGroup
from .constants import CF_FILTER_DISABLED, CF_FILTER_EXACT, CF_TYPE_BOOLEAN, CF_TYPE_SELECT
from .models import ConfigContext, CustomField, Graph, ExportTemplate, ObjectChange, TopologyMap, UserAction


class CustomFieldFilter(django_filters.Filter):
    """
    Filter objects by the presence of a CustomFieldValue. The filter's name is used as the CustomField name.
    """

    def __init__(self, custom_field, *args, **kwargs):
        self.cf_type = custom_field.type
        self.filter_logic = custom_field.filter_logic
        super(CustomFieldFilter, self).__init__(*args, **kwargs)

    def filter(self, queryset, value):

        # Skip filter on empty value
        if not value.strip():
            return queryset

        # Selection fields get special treatment (values must be integers)
        if self.cf_type == CF_TYPE_SELECT:
            try:
                # Treat 0 as None
                if int(value) == 0:
                    return queryset.exclude(
                        custom_field_values__field__name=self.name,
                    )
                # Match on exact CustomFieldChoice PK
                else:
                    return queryset.filter(
                        custom_field_values__field__name=self.name,
                        custom_field_values__serialized_value=value,
                    )
            except ValueError:
                return queryset.none()

        # Apply the assigned filter logic (exact or loose)
        if self.cf_type == CF_TYPE_BOOLEAN or self.filter_logic == CF_FILTER_EXACT:
            queryset = queryset.filter(
                custom_field_values__field__name=self.name,
                custom_field_values__serialized_value=value
            )
        else:
            queryset = queryset.filter(
                custom_field_values__field__name=self.name,
                custom_field_values__serialized_value__icontains=value
            )

        return queryset


class CustomFieldFilterSet(django_filters.FilterSet):
    """
    Dynamically add a Filter for each CustomField applicable to the parent model.
    """

    def __init__(self, *args, **kwargs):
        super(CustomFieldFilterSet, self).__init__(*args, **kwargs)

        obj_type = ContentType.objects.get_for_model(self._meta.model)
        custom_fields = CustomField.objects.filter(obj_type=obj_type).exclude(filter_logic=CF_FILTER_DISABLED)
        for cf in custom_fields:
            self.filters['cf_{}'.format(cf.name)] = CustomFieldFilter(name=cf.name, custom_field=cf)


class GraphFilter(django_filters.FilterSet):

    class Meta:
        model = Graph
        fields = ['type', 'name']


class ExportTemplateFilter(django_filters.FilterSet):

    class Meta:
        model = ExportTemplate
        fields = ['content_type', 'name']


class TagFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = Tag
        fields = ['name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value)
        )


class TopologyMapFilter(django_filters.FilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = TopologyMap
        fields = ['name', 'slug']


class ConfigContextFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        name='regions',
        queryset=Region.objects.all(),
        label='Region',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        name='regions__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='sites',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='sites__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        name='roles',
        queryset=DeviceRole.objects.all(),
        label='Role',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='roles__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        name='platforms',
        queryset=Platform.objects.all(),
        label='Platform',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        name='platforms__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    tenant_group_id = django_filters.ModelMultipleChoiceFilter(
        name='tenant_groups',
        queryset=TenantGroup.objects.all(),
        label='Tenant group',
    )
    tenant_group = django_filters.ModelMultipleChoiceFilter(
        name='tenant_groups__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Tenant group (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        name='tenants',
        queryset=Tenant.objects.all(),
        label='Tenant',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenants__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )

    class Meta:
        model = ConfigContext
        fields = ['name', 'is_active']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(data__icontains=value)
        )


class ObjectChangeFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    time = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ObjectChange
        fields = ['user', 'user_name', 'request_id', 'action', 'changed_object_type', 'object_repr']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user_name__icontains=value) |
            Q(object_repr__icontains=value)
        )


class UserActionFilter(django_filters.FilterSet):
    username = django_filters.ModelMultipleChoiceFilter(
        name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
    )

    class Meta:
        model = UserAction
        fields = ['user']
