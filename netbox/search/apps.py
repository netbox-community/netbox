from django.apps import AppConfig

from django.apps import apps
from django.utils.module_loading import module_has_submodule
from netbox import denormalized


def get_app_modules():
    """
    Returns all app modules (installed apps) - yields tuples of (app_name, module)
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def get_app_submodules(submodule_name):
    """
    Searches each app module for the specified submodule - yields tuples of (app_name, module)
    """
    for name, module in get_app_modules():
        if module_has_submodule(module, submodule_name):
            yield name, import_module(f"{name}.{submodule_name}")


class SearchConfig(AppConfig):
    name = "search"
    verbose_name = "search"

    def ready(self):
        for name, module in get_app_modules():
            submodule_name = "search_indexes"
            if module_has_submodule(module, submodule_name):
                print(f"{name}.{submodule_name}")
