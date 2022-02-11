import django_filters
from django.db.models import Q

from extras.filters import TagFilter
from netbox.filtersets import ChangeLoggedModelFilterSet, OrganizationalModelFilterSet, PrimaryModelFilterSet
from utilities.filters import ContentTypeFilter, TreeNodeMultipleChoiceFilter
from .models import *


__all__ = (
    'ContactAssignmentFilterSet',
    'ContactFilterSet',
    'ContactGroupFilterSet',
    'ContactRoleFilterSet',
    'TenancyFilterSet',
    'TenantFilterSet',
    'TenantGroupFilterSet',
)


#
# Tenancy
#

class TenantGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label='Tenant group (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Tenant group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = TenantGroup
        fields = ['id', 'name', 'slug', 'description']


class TenantFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label='Tenant group (ID)',
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='slug',
        label='Tenant group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class TenancyFilterSet(django_filters.FilterSet):
    """
    An inheritable FilterSet for models which support Tenant assignment.
    """
    tenant_group_id = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='tenant__group',
        lookup_expr='in',
        label='Tenant Group (ID)',
    )
    tenant_group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='tenant__group',
        to_field_name='slug',
        lookup_expr='in',
        label='Tenant Group (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__slug',
        to_field_name='slug',
        label='Tenant (slug)',
    )


#
# Contacts
#

class ContactGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        label='Contact group (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=ContactGroup.objects.all(),
        to_field_name='slug',
        label='Contact group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = ContactGroup
        fields = ['id', 'name', 'slug', 'description']


class ContactRoleFilterSet(OrganizationalModelFilterSet):
    tag = TagFilter()

    class Meta:
        model = ContactRole
        fields = ['id', 'name', 'slug']


class ContactFilterSet(PrimaryModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label='Contact group (ID)',
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='slug',
        label='Contact group (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Contact
        fields = ['id', 'name', 'title', 'phone', 'email', 'address']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(title__icontains=value) |
            Q(phone__icontains=value) |
            Q(email__icontains=value) |
            Q(address__icontains=value) |
            Q(comments__icontains=value)
        )


class ContactAssignmentFilterSet(ChangeLoggedModelFilterSet):
    content_type = ContentTypeFilter()
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label='Contact (ID)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContactRole.objects.all(),
        label='Contact role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=ContactRole.objects.all(),
        to_field_name='slug',
        label='Contact role (slug)',
    )

    class Meta:
        model = ContactAssignment
        fields = ['id', 'content_type_id', 'object_id', 'priority']
