from __future__ import unicode_literals

from django.conf import settings as django_settings


def settings(request):
    """
    Expose Django settings in the template context. Example: {{ settings.DEBUG }}
    """
    return {
        'settings': django_settings,
    }
