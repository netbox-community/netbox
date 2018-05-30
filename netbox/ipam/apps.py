from __future__ import unicode_literals

from django.apps import AppConfig


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = "IPAM"

    def ready(self):

        # register webhook signals
        from extras.webhooks import register_signals
        from .models import Aggregate, Prefix, IPAddress, VLAN, VRF, VLANGroup, Service
        register_signals([Aggregate, Prefix, IPAddress, VLAN, VRF, VLANGroup, Service])
