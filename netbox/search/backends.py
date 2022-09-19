from abc import ABC
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.signals import post_save, pre_delete

# The cache for the initialized backend.
_backends_cache = {}


def get_backend(backend_name=None):
    """Initializes and returns the search backend."""
    global _backends_cache
    if not backend_name:
        backend_name = getattr(settings, "SEARCH_BACKEND", "search.backends.PostgresIcontainsSearchBackend")

    # Try to use the cached backend.
    if backend_name in _backends_cache:
        return _backends_cache[backend_name]

    # Load the backend class.
    backend_module_name, backend_cls_name = backend_name.rsplit(".", 1)
    backend_module = import_module(backend_module_name)
    try:
        backend_cls = getattr(backend_module, backend_cls_name)
    except AttributeError:
        raise ImproperlyConfigured(f"Could not find a class named {backend_module_name} in {backend_cls_name}")

    # Initialize the backend.
    backend = backend_cls()
    _backends_cache[backend_name] = backend
    return backend


class SearchEngineError(Exception):

    """Something went wrong with a search engine."""


class SearchBackend(object):

    """A search engine capable of performing multi-table searches."""

    _created_engines: dict = dict()

    @classmethod
    def get_created_engines(cls):
        """Returns all created search engines."""
        return list(cls._created_engines.items())

    def __init__(self, engine_slug: str):
        """Initializes the search engine."""
        # Check the slug is unique for this project.
        if engine_slug in SearchBackend._created_engines:
            raise SearchEngineError(f"A search engine has already been created with the slug {engine_slug}")

        # Initialize this engine.
        self._registered_models = {}
        self._engine_slug = engine_slug

        # Store a reference to this engine.
        self.__class__._created_engines[engine_slug] = self

    def is_registered(self, model):
        """Checks whether the given model is registered with this search engine."""
        return model in self._registered_models

    def register(self, model):
        """
        Registers the given model with this search engine.

        If the given model is already registered with this search engine, a
        RegistrationError will be raised.
        """
        # Check for existing registration.
        if self.is_registered(model):
            raise RegistrationError(f"{model} is already registered with this search engine")

        # Connect to the signalling framework.
        if self._use_hooks():
            post_save.connect(self._post_save_receiver, model)
            pre_delete.connect(self._pre_delete_receiver, model)

    # Signalling hooks.

    def _use_hooks(self):
        raise NotImplementedError

    def _post_save_receiver(self, instance, **kwargs):
        """Signal handler for when a registered model has been saved."""
        raise NotImplementedError

    def _pre_delete_receiver(self, instance, **kwargs):
        """Signal handler for when a registered model has been deleted."""
        raise NotImplementedError

    # Searching.

    def search(self, search_text, models=(), exclude=(), ranking=True, backend_name=None):
        """Performs a search using the given text, returning a queryset of SearchEntry."""
        raise NotImplementedError


class PostgresIcontainsSearchBackend(SearchBackend):
    def _use_hooks(self):
        return False


# The main search methods.
default_search_engine = SearchBackend("default")
search = default_search_engine.search
