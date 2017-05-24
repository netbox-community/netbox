from __future__ import unicode_literals

from django.conf import settings as django_settings


def settings(request):
    return {
        'settings': django_settings,
    }
