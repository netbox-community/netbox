from contextlib import contextmanager
from urllib.parse import urlparse

from netbox.registry import registry
from utilities.choices import Choice

__all__ = (
    'DataBackend',
    'get_data_backend_choices',
    'register_data_backend',
)


class DataBackend:
    """
    A data backend represents a specific system of record for data, such as a git repository or Amazon S3 bucket.

    Attributes:
        name: The identifier under which this backend will be registered in NetBox
        label: The human-friendly name for this backend
        is_local: A boolean indicating whether this backend accesses local data
        parameters: A dictionary mapping configuration form field names to their classes
        sensitive_parameters: An iterable of field names for which the values should not be displayed to the user
    """
    is_local = False
    parameters = {}
    sensitive_parameters = []

    # Prevent Django's template engine from calling the backend
    # class when referenced via DataSource.backend_class
    do_not_call_in_templates = True

    def __init__(self, url, **kwargs):
        self.url = url
        self.params = kwargs
        self.config = self.init_config()

    def init_config(self):
        """
        A hook to initialize the instance's configuration. The data returned by this method is assigned to the
        instance's `config` attribute upon initialization, which can be referenced by the `fetch()` method.
        """
        return

    @property
    def url_scheme(self):
        return urlparse(self.url).scheme.lower()

    @contextmanager
    def fetch(self):
        """
        A context manager which performs the following:

        1. Handles all setup and synchronization
        2. Yields the local path at which data has been replicated
        3. Performs any necessary cleanup
        """
        raise NotImplementedError()


def get_data_backend_choices():
    return [
        (None, '---------'),
        *[
            Choice(name, cls.label) for name, cls in registry['data_backends'].items()
        ]
    ]


def register_data_backend():
    """
    Decorator for registering a DataBackend class.
    """
    def _wrapper(cls):
        registry['data_backends'][cls.name] = cls
        return cls

    return _wrapper
