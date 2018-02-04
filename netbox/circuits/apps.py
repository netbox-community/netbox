from __future__ import unicode_literals

from django.apps import AppConfig


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = "Circuits"

    def ready(self):
        import circuits.signals

        # register webhook signals
        from extras.webhooks import register_signals
        from .models import Circuit, Provider
        register_signals([Circuit, Provider])
