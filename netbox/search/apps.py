import inspect
import sys
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
        from .backends import default_search_engine
        from .hierarchy import SEARCH_TYPES

        for name, module in SEARCH_TYPES.items():
            default_search_engine.register(name, module)

        for name, module in get_app_modules():
            submodule_name = "search_indexes"
            if module_has_submodule(module, submodule_name):
                module_name = f"{name}.{submodule_name}"
                for cls_name, cls_obj in inspect.getmembers(sys.modules[module_name]):
                    if inspect.isclass(cls_obj) and getattr(cls_obj, "search_index", False) and getattr(cls_obj, "model", None):
                        cls_name = cls_obj.model.__name__.lower()
                        if not default_search_engine.is_registered(cls_name, cls_obj):
                            default_search_engine.register(cls_name, cls_obj)
