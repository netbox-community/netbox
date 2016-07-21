import django_filters

from .models import Secret, SecretRole
from dcim.models import Device


class SecretFilter(django_filters.FilterSet):
    role_id = django_filters.ModelMultipleChoiceFilter(
        name='role',
        queryset=SecretRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role',
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
        fields = ['name', 'role_id', 'role', 'device']
