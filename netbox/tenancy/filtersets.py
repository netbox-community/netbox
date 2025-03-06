import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import NetBoxModelFilterSet, OrganizationalModelFilterSet
from utilities.filters import ContentTypeFilter, TreeNodeMultipleChoiceFilter
from .models import *

__all__ = (
    'ContactAssignmentFilterSet',
    'ContactFilterSet',
    'ContactGroupFilterSet',
    'ContactModelFilterSet',
    'ContactRoleFilterSet',
    'TenancyFilterSet',
    'TenantFilterSet',
    'TenantGroupFilterSet',
)


#
# Contacts
#

class ContactGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        label=_('Parent contact group (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=ContactGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent contact group (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Contact group (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Contact group (slug)'),
    )

    class Meta:
        model = ContactGroup
        fields = ('id', 'name', 'slug', 'description')


class ContactRoleFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = ContactRole
        fields = ('id', 'name', 'slug', 'description')


class ContactFilterSet(NetBoxModelFilterSet):
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label=_('Contact group (ID)'),
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Contact group (slug)'),
    )

    class Meta:
        model = Contact
        fields = ('id', 'name', 'title', 'phone', 'email', 'address', 'link', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(title__icontains=value) |
            Q(phone__icontains=value) |
            Q(email__icontains=value) |
            Q(address__icontains=value) |
            Q(link__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class ContactAssignmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type = ContentTypeFilter()
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        label=_('Contact (ID)'),
    )
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='contact__group',
        lookup_expr='in',
        label=_('Contact group (ID)'),
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='contact__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Contact group (slug)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ContactRole.objects.all(),
        label=_('Contact role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=ContactRole.objects.all(),
        to_field_name='slug',
        label=_('Contact role (slug)'),
    )

    class Meta:
        model = ContactAssignment
        fields = ('id', 'object_type_id', 'object_id', 'priority')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(contact__name__icontains=value) |
            Q(role__name__icontains=value)
        )


class ContactModelFilterSet(django_filters.FilterSet):
    contact = django_filters.ModelMultipleChoiceFilter(
        field_name='contacts__contact',
        queryset=Contact.objects.all(),
        label=_('Contact'),
    )
    contact_role = django_filters.ModelMultipleChoiceFilter(
        field_name='contacts__role',
        queryset=ContactRole.objects.all(),
        label=_('Contact Role')
    )
    contact_group = TreeNodeMultipleChoiceFilter(
        queryset=ContactGroup.objects.all(),
        field_name='contacts__contact__group',
        lookup_expr='in',
        label=_('Contact group'),
    )


#
# Tenancy
#

class TenantGroupFilterSet(OrganizationalModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        label=_('Parent tenant group (ID)'),
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent tenant group (slug)'),
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        label=_('Tenant group (ID)'),
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='parent',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Tenant group (slug)'),
    )

    class Meta:
        model = TenantGroup
        fields = ('id', 'name', 'slug', 'description')


class TenantFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
    group_id = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        label=_('Tenant group (ID)'),
    )
    group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Tenant group (slug)'),
    )

    class Meta:
        model = Tenant
        fields = ('id', 'name', 'slug', 'description')

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
        label=_('Tenant Group (ID)'),
    )
    tenant_group = TreeNodeMultipleChoiceFilter(
        queryset=TenantGroup.objects.all(),
        field_name='tenant__group',
        to_field_name='slug',
        lookup_expr='in',
        label=_('Tenant Group (slug)'),
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label=_('Tenant (ID)'),
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__slug',
        to_field_name='slug',
        label=_('Tenant (slug)'),
    )
