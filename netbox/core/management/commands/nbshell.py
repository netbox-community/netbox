import code
import platform
import sys

from colorama import Fore, Style
from django import get_version
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

from netbox.constants import CORE_APPS
from netbox.plugins.utils import get_installed_plugins

EXCLUDE_MODELS = ()


def color(color: str, text: str):
    return getattr(Fore, color.upper()) + text + Style.RESET_ALL


def bright(text: str):
    return Style.BRIGHT + text + Style.RESET_ALL


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
        for app in CORE_APPS:
            models = []

            # Load models from each app
            for model in apps.get_app_config(app).get_models():
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                if f'{app_label}.{model_name}' not in EXCLUDE_MODELS:
                    namespace[model.__name__] = model
                    models.append(model.__name__)
            self.django_models[app] = sorted(models)

            # Constants
            try:
                app_constants = sys.modules[f'{app}.constants']
                for name in dir(app_constants):
                    namespace[name] = getattr(app_constants, name)
            except KeyError:
                pass

        # Load convenience commands
        namespace.update({
            'lsmodels': self._lsmodels,
        })

        return namespace

    def get_banner_text(self):
        lines = [
            '{title} ({hostname})'.format(
                title=bright('NetBox interactive shell'),
                hostname=platform.node(),
            ),
            '{python} | {django} | {netbox}'.format(
                python=color('green', f'Python v{platform.python_version()}'),
                django=color('green', f'Django v{get_version()}'),
                netbox=color('green', settings.RELEASE.name),
            ),
        ]

        if installed_plugins := get_installed_plugins():
            plugin_list = ', '.join([
                color('cyan', f'{name} v{version}') for name, version in installed_plugins.items()
            ])
            lines.append(
                'Plugins: {plugin_list}'.format(
                    plugin_list=plugin_list
                )
            )

        lines.append(
            'lsmodels() will show available models. Use help(<model>) for more info.'
        )

        return '\n'.join([
            f'### {line}' for line in lines
        ])

    def handle(self, **options):
        namespace = self.get_namespace()

        # If Python code has been passed, execute it and exit.
        if options['command']:
            exec(options['command'], namespace)
            return

        # Try to enable tab-complete
        try:
            import readline
            import rlcompleter
        except ModuleNotFoundError:
            pass
        else:
            readline.set_completer(rlcompleter.Completer(namespace).complete)
            readline.parse_and_bind('tab: complete')

        # Run interactive shell
        shell = code.interact(banner=self.get_banner_text(), local=namespace)
        return shell
