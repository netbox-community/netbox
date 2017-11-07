from __future__ import unicode_literals

import code
import platform
import sys

from django import get_version
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Model

APPS = ['circuits', 'dcim', 'extras', 'ipam', 'secrets', 'tenancy', 'users', 'virtualization']

BANNER_TEXT = """### NetBox interactive shell ({node})
### Python {python} | Django {django} | NetBox {netbox}
### lsmodels() will show available models. Use help(<model>) for more info.""".format(
    node=platform.node(),
    python=platform.python_version(),
    django=get_version(),
    netbox=settings.VERSION
)


class Command(BaseCommand):
    help = "Start the Django shell with all NetBox models already imported"
    django_models = {}

    def _lsmodels(self):
        for app, models in self.django_models.items():
            app_name = apps.get_app_config(app).verbose_name
            print('{}:'.format(app_name))
            for m in models:
                print('  {}'.format(m))

    def get_namespace(self):
        namespace = {}

        # Gather Django models and constants from each app
        for app in APPS:
            self.django_models[app] = []

            # Models
            app_models = sys.modules['{}.models'.format(app)]
            for name in dir(app_models):
                model = getattr(app_models, name)
                try:
                    if issubclass(model, Model) and model._meta.app_label == app:
                        namespace[name] = model
                        self.django_models[app].append(name)
                except TypeError:
                    pass

            # Constants
            try:
                app_constants = sys.modules['{}.constants'.format(app)]
                for name in dir(app_constants):
                    namespace[name] = getattr(app_constants, name)
            except KeyError:
                pass

        # Load convenience commands
        namespace.update({
            'lsmodels': self._lsmodels,
        })

        return namespace

    def handle(self, **options):
        shell = code.interact(banner=BANNER_TEXT, local=self.get_namespace())
        return shell
