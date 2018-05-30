from __future__ import unicode_literals

from django.apps import AppConfig


class TenancyConfig(AppConfig):
    name = 'tenancy'

    def ready(self):

        # register webhook signals
        from extras.webhooks import register_signals
        from .models import Tenant, TenantGroup
        register_signals([Tenant, TenantGroup])
