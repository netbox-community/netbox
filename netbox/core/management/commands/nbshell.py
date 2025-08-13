import code
import platform
from collections import defaultdict
from types import SimpleNamespace

from colorama import Fore, Style
from django import get_version
from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

from netbox.constants import CORE_APPS
from netbox.plugins.utils import get_installed_plugins


def color(color: str, text: str):
    return getattr(Fore, color.upper()) + text + Style.RESET_ALL


def bright(text: str):
    return Style.BRIGHT + text + Style.RESET_ALL


def get_models(app_config):
    """
    Return a list of all non-private models within an app.
    """
    return [
        model for model in app_config.get_models()
        if not getattr(model, '_netbox_private', False)
    ]


def get_constants(app_config):
    """
    Return a dictionary mapping of all constants defined within an app.
    """
    try:
        constants = import_string(f'{app_config.name}.constants')
    except ImportError:
        return {}
    return {
        name: value for name, value in vars(constants).items()
    }


class Command(BaseCommand):
    help = "Start the Django shell with all NetBox models already imported"
    django_models = {}

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--command',
            help='Python code to execute (instead of starting an interactive shell)',
        )

    def _lsapps(self):
        for app_label in self.django_models.keys():
            app_name = apps.get_app_config(app_label).verbose_name
            print(f'{app_label} - {app_name}')

    def _lsmodels(self, app_label=None):
        """
        Return a list of all models within each app.

        Args:
            app_label: The name of a specific app
        """
        if app_label:
            if app_label not in self.django_models:
                print(f"No models listed for {app_label}")
                return
            app_labels = [app_label]
        else:
            app_labels = self.django_models.keys()  # All apps

        for app_label in app_labels:
            app_name = apps.get_app_config(app_label).verbose_name
            print(f'{app_name}:')
            for model in self.django_models[app_label]:
                print(f'  {app_label}.{model}')

    def get_namespace(self):
        namespace = defaultdict(SimpleNamespace)

        # Iterate through all core apps & plugins to compile namespace of models and constants
        for app_name in [*CORE_APPS, *get_installed_plugins().keys()]:
            app_config = apps.get_app_config(app_name)

            # Populate models
            if models := get_models(app_config):
                for model in models:
                    setattr(namespace[app_name], model.__name__, model)
                self.django_models[app_name] = sorted([
                    model.__name__ for model in models
                ])

            # Populate constants
            for const_name, const_value in get_constants(app_config).items():
                setattr(namespace[app_name], const_name, const_value)

        return {
            **namespace,
            'lsapps': self._lsapps,
            'lsmodels': self._lsmodels,
        }

    @staticmethod
    def get_banner_text():
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
            'lsapps() & lsmodels() will show available models. Use help(<model>) for more info.'
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
        return code.interact(banner=self.get_banner_text(), local=namespace)
