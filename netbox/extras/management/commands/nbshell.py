import code
import platform
import sys

from django import get_version
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

APPS = ['circuits', 'dcim', 'extras', 'ipam', 'tenancy', 'users', 'virtualization']

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

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--command',
            help='Python code to execute (instead of starting an interactive shell)',
        )

    def _lsmodels(self):
        for app, models in self.django_models.items():
            app_name = apps.get_app_config(app).verbose_name
            print(f'{app_name}:')
            for m in models:
                print(f'  {m}')

    def get_namespace(self):
        namespace = {}

        # Gather Django models and constants from each app
        for app in APPS:
            self.django_models[app] = []

            # Load models from each app
            for model in apps.get_app_config(app).get_models():
                namespace[model.__name__] = model
                self.django_models[app].append(model.__name__)

            # Constants
            try:
                app_constants = sys.modules[f'{app}.constants']
                for name in dir(app_constants):
                    namespace[name] = getattr(app_constants, name)
            except KeyError:
                pass

        # Additional objects to include
        namespace['ContentType'] = ContentType
        namespace['User'] = User

        # Load convenience commands
        namespace.update({
            'lsmodels': self._lsmodels,
        })

        return namespace

    def handle(self, **options):
        # If Python code has been passed, execute it and exit.
        if options['command']:
            exec(options['command'], self.get_namespace())
            return

        shell = code.interact(banner=BANNER_TEXT, local=self.get_namespace())
        return shell
