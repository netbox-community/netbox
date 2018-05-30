from __future__ import unicode_literals

from django.apps import AppConfig


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "DCIM"

    def ready(self):

        import dcim.signals

        # register webhook signals
        from extras.webhooks import register_signals
        from .models import Site, Rack, RackGroup, Device, Interface
        register_signals([Site, Rack, Device, Interface, RackGroup])
