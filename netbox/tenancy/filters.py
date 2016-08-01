import django_filters

from django.db.models import Q

from .models import Tenant, TenantGroup


class TenantFilter(django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        name='group',
        queryset=TenantGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='group',
        queryset=TenantGroup.objects.all(),
        to_field_name='slug',
        label='Group (slug)',
    )

    class Meta:
        model = Tenant
        fields = ['q', 'group_id', 'group', 'name']

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )
