from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from netbox.admin import admin_site
from .models import Token


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(required=False, help_text="If no key is provided, one will be generated automatically.")

    class Meta:
        fields = ['user', 'key', 'write_enabled', 'expires', 'description']
        model = Token


@admin.register(Token, site=admin_site)
class TokenAdmin(admin.ModelAdmin):
    form = TokenAdminForm
    list_display = ['key', 'user', 'created', 'expires', 'write_enabled', 'description']
