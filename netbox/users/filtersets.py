import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext as _

from netbox.filtersets import BaseFilterSet
from users.models import Group, ObjectPermission, Token
from utilities.filters import ContentTypeFilter, MultiValueNumberFilter

__all__ = (
    'GroupFilterSet',
    'ObjectPermissionFilterSet',
    'TokenFilterSet',
    'UserFilterSet',
)


class GroupFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=get_user_model().objects.all(),
        label=_('User (ID)'),
    )
    permission_id = django_filters.ModelMultipleChoiceFilter(
        field_name='object_permissions',
        queryset=ObjectPermission.objects.all(),
        label=_('Permission (ID)'),
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(name__icontains=value)


class UserFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='groups',
        queryset=Group.objects.all(),
        label=_('Group'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='groups__name',
        queryset=Group.objects.all(),
        to_field_name='name',
        label=_('Group (name)'),
    )
    permission_id = django_filters.ModelMultipleChoiceFilter(
        field_name='object_permissions',
        queryset=ObjectPermission.objects.all(),
        label=_('Permission (ID)'),
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_staff', 'is_active',
            'is_superuser',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value)
        )


class TokenFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=get_user_model().objects.all(),
        label=_('User'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )
    created = django_filters.DateTimeFilter()
    created__gte = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )
    created__lte = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    expires = django_filters.DateTimeFilter()
    expires__gte = django_filters.DateTimeFilter(
        field_name='expires',
        lookup_expr='gte'
    )
    expires__lte = django_filters.DateTimeFilter(
        field_name='expires',
        lookup_expr='lte'
    )

    class Meta:
        model = Token
        fields = ('id', 'key', 'write_enabled', 'description', 'last_used')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class ObjectPermissionFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = MultiValueNumberFilter(
        field_name='object_types__id'
    )
    object_type = ContentTypeFilter(
        field_name='object_types'
    )
    can_view = django_filters.BooleanFilter(
        method='_check_action'
    )
    can_add = django_filters.BooleanFilter(
        method='_check_action'
    )
    can_change = django_filters.BooleanFilter(
        method='_check_action'
    )
    can_delete = django_filters.BooleanFilter(
        method='_check_action'
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='users',
        queryset=get_user_model().objects.all(),
        label=_('User'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='users__username',
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        label=_('User (name)'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='groups',
        queryset=Group.objects.all(),
        label=_('Group'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='groups__name',
        queryset=Group.objects.all(),
        to_field_name='name',
        label=_('Group (name)'),
    )

    class Meta:
        model = ObjectPermission
        fields = ('id', 'name', 'enabled', 'object_types', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )

    def _check_action(self, queryset, name, value):
        action = name.split('_')[1]
        if value:
            return queryset.filter(actions__contains=[action])
        else:
            return queryset.exclude(actions__contains=[action])
