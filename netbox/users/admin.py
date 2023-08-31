from django.contrib import admin
from django.contrib.auth.models import Group, User

# Unregister Django's built-in Group and User admin views
admin.site.unregister(Group)
admin.site.unregister(User)
