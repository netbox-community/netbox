from django.apps import AppConfig
from django.utils.translation import gettext as _


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = _('IPAM')
