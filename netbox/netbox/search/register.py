import importlib
import inspect
import sys

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import module_has_submodule

from extras.registry import registry
from .backends import default_search_engine


def get_app_modules():
    """
    Returns all app modules (installed apps) - yields tuples of (app_name, module)
    """
    for app in apps.get_app_configs():
        yield app.name, app.module


def register():

    # for name, module in SEARCH_TYPES.items():
    #     default_search_engine.register(name, module)

    for app_label, models in registry['search'].items():
        for name, cls in models.items():
            default_search_engine.register(name, cls)

    for name, module in get_app_modules():
        submodule_name = "search_indexes"
        if module_has_submodule(module, submodule_name):
            module_name = f"{name}.{submodule_name}"
            if name in settings.PLUGINS:
                search_module = importlib.import_module(module_name)
            else:
                search_module = sys.modules[module_name]

            cls_objects = inspect.getmembers(search_module, predicate=inspect.isclass)
            for cls_name, cls_obj in inspect.getmembers(search_module, predicate=inspect.isclass):
                if getattr(cls_obj, "search_index", False) and getattr(cls_obj, "model", None):
                    cls_name = cls_obj.model.__name__.lower()
                    if not default_search_engine.is_registered(cls_name, cls_obj):
                        default_search_engine.register(cls_name, cls_obj)


def register_search(model):
    def _wrapper(cls):
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        registry['search'][app_label][model_name] = cls

        return cls

    return _wrapper
