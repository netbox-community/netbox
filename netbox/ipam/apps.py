from django.apps import AppConfig


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = "IPAM"

    def ready(self):
        from . import signals, search
