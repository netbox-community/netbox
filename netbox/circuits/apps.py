from django.apps import AppConfig
from django.utils.translation import gettext as _


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = _('Circuits')

    def ready(self):
        import circuits.signals
