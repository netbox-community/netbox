from django.contrib import admin
from django.contrib.auth.models import Group, User

from users.models import UserConfig

__all__ = (
    'GroupObjectPermissionInline',
    'UserConfigInline',
    'UserObjectPermissionInline',
)


class ObjectPermissionInline(admin.TabularInline):
    exclude = None
    extra = 3
    readonly_fields = ['object_types', 'actions', 'constraints']
    verbose_name = 'Permission'
    verbose_name_plural = 'Permissions'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('objectpermission__object_types')

    @staticmethod
    def object_types(instance):
        # Don't call .values_list() here because we want to reference the pre-fetched object_types
        return ', '.join([ot.name for ot in instance.objectpermission.object_types.all()])

    @staticmethod
    def actions(instance):
        return ', '.join(instance.objectpermission.actions)

    @staticmethod
    def constraints(instance):
        return instance.objectpermission.constraints


class GroupObjectPermissionInline(ObjectPermissionInline):
    model = Group.object_permissions.through


class UserObjectPermissionInline(ObjectPermissionInline):
    model = User.object_permissions.through


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    readonly_fields = ('data',)
    can_delete = False
    verbose_name = 'Preferences'
