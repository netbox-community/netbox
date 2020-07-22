import django_filters
from django.contrib.auth.models import Group, User
from django.db.models import Q

from utilities.filters import BaseFilterSet

__all__ = (
    'GroupFitlerSet',
    'UserFitlerSet',
)


class GroupFitlerSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )

    class Meta:
        model = Group
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)


class UserFitlerSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='groups',
        queryset=Group.objects.all(),
        label='Group',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='groups__name',
        queryset=Group.objects.all(),
        to_field_name='name',
        label='Group (name)',
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )
