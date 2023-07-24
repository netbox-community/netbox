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
