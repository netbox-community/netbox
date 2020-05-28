from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import Group, User

from .models import ObjectPermission, Token, UserConfig

# Unregister the built-in GroupAdmin and UserAdmin classes so that we can use our custom admin classes below
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name', 'user_count')
    ordering = ('name',)
    search_fields = ('name',)

    def user_count(self, obj):
        return obj.user_set.count()


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    readonly_fields = ('data',)
    can_delete = False
    verbose_name = 'Preferences'


@admin.register(User)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (UserConfigInline,)


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="If no key is provided, one will be generated automatically."
    )

    class Meta:
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description'
        ]
        model = Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    form = TokenAdminForm
    list_display = [
        'key', 'user', 'created', 'expires', 'write_enabled', 'description'
    ]


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'model', 'can_view', 'can_add', 'can_change', 'can_delete'
    ]
