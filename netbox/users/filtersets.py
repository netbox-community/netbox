import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.models import NotificationGroup
from netbox.filtersets import BaseFilterSet
from users.models import Group, ObjectPermission, Owner, OwnerGroup, Token, User
from utilities.filters import MultiValueContentTypeFilter
from utilities.filtersets import register_filterset

__all__ = (
    'GroupFilterSet',
    'ObjectPermissionFilterSet',
    'OwnerFilterSet',
    'OwnerGroupFilterSet',
    'TokenFilterSet',
    'UserFilterSet',
)


@register_filterset
class GroupFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        label=_('User (ID)'),
    )
    owner_id = django_filters.ModelMultipleChoiceFilter(
        field_name='owner',
        queryset=Owner.objects.all(),
        label=_('Owner (ID)'),
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name='owner__name',
        queryset=Owner.objects.all(),
        to_field_name='name',
        label=_('Owner (name)'),
    )
    permission_id = django_filters.ModelMultipleChoiceFilter(
        field_name='object_permissions',
        queryset=ObjectPermission.objects.all(),
        label=_('Permission (ID)'),
    )
    notification_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='notification_groups',
        queryset=NotificationGroup.objects.all(),
        label=_('Notification group (ID)'),
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


@register_filterset
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
    owner_id = django_filters.ModelMultipleChoiceFilter(
        field_name='owner',
        queryset=Owner.objects.all(),
        label=_('Owner (ID)'),
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        field_name='owner__name',
        queryset=Owner.objects.all(),
        to_field_name='name',
        label=_('Owner (name)'),
    )
    permission_id = django_filters.ModelMultipleChoiceFilter(
        field_name='object_permissions',
        queryset=ObjectPermission.objects.all(),
        label=_('Permission (ID)'),
    )
    notification_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='notification_groups',
        queryset=NotificationGroup.objects.all(),
        label=_('Notification group (ID)'),
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_active',
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


@register_filterset
class TokenFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        distinct=False,
        label=_('User'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user__username',
        queryset=User.objects.all(),
        distinct=False,
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
    last_used = django_filters.DateTimeFilter()
    last_used__gte = django_filters.DateTimeFilter(
        field_name='last_used',
        lookup_expr='gte'
    )
    last_used__lte = django_filters.DateTimeFilter(
        field_name='last_used',
        lookup_expr='lte'
    )

    class Meta:
        model = Token
        fields = (
            'id', 'version', 'key', 'pepper_id', 'enabled', 'write_enabled',
            'description', 'created', 'expires', 'last_used',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(key=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


@register_filterset
class ObjectPermissionFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    object_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ObjectType.objects.all(),
        field_name='object_types'
    )
    object_type = MultiValueContentTypeFilter(
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
        queryset=User.objects.all(),
        label=_('User'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='users__username',
        queryset=User.objects.all(),
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
        return queryset.exclude(actions__contains=[action])


@register_filterset
class OwnerGroupFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = OwnerGroup
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


@register_filterset
class OwnerFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=OwnerGroup.objects.all(),
        distinct=False,
        label=_('Group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__name',
        queryset=OwnerGroup.objects.all(),
        distinct=False,
        to_field_name='name',
        label=_('Group (name)'),
    )
    user_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='user_groups',
        queryset=Group.objects.all(),
        label=_('User group (ID)'),
    )
    user_group = django_filters.ModelMultipleChoiceFilter(
        field_name='user_groups__name',
        queryset=Group.objects.all(),
        to_field_name='name',
        label=_('User group (name)'),
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name='users',
        queryset=User.objects.all(),
        label=_('User (ID)'),
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='users__username',
        queryset=User.objects.all(),
        to_field_name='username',
        label=_('User (username)'),
    )

    class Meta:
        model = Owner
        fields = ('id', 'name', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
