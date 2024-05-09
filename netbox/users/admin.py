from django.contrib import admin
from django.contrib.auth.models import Group as DjangoGroup

# Prevent the stock Django Group model from appearing in the admin UI (if enabled)
admin.site.unregister(DjangoGroup)
