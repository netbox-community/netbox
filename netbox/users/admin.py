from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from .models import Token, UserConfig

# Unregister the built-in UserAdmin so that we can use our custom admin view below
admin.site.unregister(User)


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    readonly_fields = ('data',)
    can_delete = False
    verbose_name = _('Preferences')


@admin.register(User)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    inlines = (UserConfigInline,)


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text=_('If no key is provided, one will be generated automatically.')
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
