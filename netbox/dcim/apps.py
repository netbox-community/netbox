from django.apps import AppConfig
from django.utils.translation import gettext as _

class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = _('DCIM')

    def ready(self):

        import dcim.signals
