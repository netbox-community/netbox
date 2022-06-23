from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import Group, User

from users.models import ObjectPermission, Token
from . import filters, forms, inlines


#
# Users & groups
#

# Unregister the built-in GroupAdmin and UserAdmin classes so that we can use our custom admin classes below
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = forms.GroupAdminForm
    list_display = ('name', 'user_count')
    ordering = ('name',)
    search_fields = ('name',)
    inlines = [inlines.GroupObjectPermissionInline]

    @staticmethod
    def user_count(obj):
        return obj.user_set.count()


@admin.register(User)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        ('Groups', {'fields': ('groups',)}),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups',)
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups__name')

    def get_inlines(self, request, obj):
        if obj is not None:
            return (inlines.UserObjectPermissionInline, inlines.UserConfigInline)
        return ()


#
# REST API tokens
#

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    form = forms.TokenAdminForm
    list_display = [
        'key', 'user', 'created', 'expires', 'last_used', 'write_enabled', 'description', 'list_allowed_ips'
    ]

    def list_allowed_ips(self, obj):
        return obj.allowed_ips or 'Any'
    list_allowed_ips.short_description = "Allowed IPs"


#
# Permissions
#

@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    actions = ('enable', 'disable')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'enabled')
        }),
        ('Actions', {
            'fields': (('can_view', 'can_add', 'can_change', 'can_delete'), 'actions')
        }),
        ('Objects', {
            'fields': ('object_types',)
        }),
        ('Assignment', {
            'fields': ('groups', 'users')
        }),
        ('Constraints', {
            'fields': ('constraints',),
            'classes': ('monospace',)
        }),
    )
    filter_horizontal = ('object_types', 'groups', 'users')
    form = forms.ObjectPermissionForm
    list_display = [
        'name', 'enabled', 'list_models', 'list_users', 'list_groups', 'actions', 'constraints', 'description',
    ]
    list_filter = [
        'enabled', filters.ActionListFilter, filters.ObjectTypeListFilter, 'groups', 'users'
    ]
    search_fields = ['actions', 'constraints', 'description', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('object_types', 'users', 'groups')

    def list_models(self, obj):
        return ', '.join([f"{ct}" for ct in obj.object_types.all()])
    list_models.short_description = 'Models'

    def list_users(self, obj):
        return ', '.join([u.username for u in obj.users.all()])
    list_users.short_description = 'Users'

    def list_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    list_groups.short_description = 'Groups'

    #
    # Admin actions
    #

    def enable(self, request, queryset):
        updated = queryset.update(enabled=True)
        self.message_user(request, f"Enabled {updated} permissions")

    def disable(self, request, queryset):
        updated = queryset.update(enabled=False)
        self.message_user(request, f"Disabled {updated} permissions")
