from django.contrib import admin

from .models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'created', 'expires', 'write_enabled', 'description']
