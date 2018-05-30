from __future__ import unicode_literals

from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):

        # register webhook signals
        from extras.webhooks import register_signals
        from .models import Cluster, ClusterGroup, VirtualMachine
        register_signals([Cluster, VirtualMachine, ClusterGroup])
