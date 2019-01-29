from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import User

from netbox.admin import admin_site
from .models import Token


# Unregister the built-in UserAdmin so that we can use our custom admin view below
admin_site.unregister(User)


@admin.register(User, site=admin_site)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]


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


@admin.register(Token, site=admin_site)
class TokenAdmin(admin.ModelAdmin):
    form = TokenAdminForm
    list_display = [
        'key', 'user', 'created', 'expires', 'write_enabled', 'description'
    ]
