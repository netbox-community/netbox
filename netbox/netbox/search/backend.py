"""
Instantiates the search backend configured via settings.SEARCH_BACKEND.

Kept separate from backends.py (which defines the SearchBackend base class and its
implementations, e.g. CachedValueSearchBackend) so that modules which need only the
singleton -- netbox.search.jobs, and the inline fallback in netbox.search.deferred --
don't have to import backends.py itself. get_backend() dynamically imports whatever class
settings.SEARCH_BACKEND names (by default CachedValueSearchBackend in backends.py); if jobs.py
or deferred.py instead imported the singleton from backends.py, that would close a
backends -> deferred -> (this module) -> backends cycle. See #22485.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

__all__ = (
    'search_backend',
)


def get_backend():
    """
    Initializes and returns the configured search backend.
    """
    try:
        backend_cls = import_string(settings.SEARCH_BACKEND)
    except AttributeError:
        raise ImproperlyConfigured(f"Failed to import configured SEARCH_BACKEND: {settings.SEARCH_BACKEND}")

    # Initialize and return the backend instance
    return backend_cls()


search_backend = get_backend()
