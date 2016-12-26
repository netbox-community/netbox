import django_filters

from django.db.models import Q

from .models import Secret, SecretRole
from dcim.models import Device


class SecretFilter(django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        name='role',
        queryset=SecretRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role__slug',
        queryset=SecretRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (Name)',
    )

    class Meta:
        model = Secret
        fields = ['name']

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(device__name__icontains=value)
        )
