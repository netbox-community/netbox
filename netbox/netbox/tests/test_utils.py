from django.test import SimpleTestCase

from netbox import utils
from netbox.data_backends import get_data_backend_choices, register_data_backend
from utilities.request import register_request_processor

# TODO: Remove in NetBox v5.0
RELOCATED_FUNCTIONS = (
    get_data_backend_choices,
    register_data_backend,
    register_request_processor,
)


# TODO: Remove in NetBox v5.0
class RelocatedFunctionsTestCase(SimpleTestCase):
    """
    Verify that functions relocated from netbox.utils remain importable from it, with a deprecation warning.
    (Ref: #23547)
    """
    def test_relocated_functions(self):
        for func in RELOCATED_FUNCTIONS:
            name = func.__name__
            with self.subTest(name=name):
                with self.assertWarnsRegex(DeprecationWarning, rf'{name}\(\) from netbox\.utils'):
                    self.assertIs(getattr(utils, name), func)

    def test_wildcard_import(self):
        namespace = {}
        with self.assertWarns(DeprecationWarning):
            exec('from netbox.utils import *', namespace)
        for func in RELOCATED_FUNCTIONS:
            self.assertIs(namespace[func.__name__], func)

    def test_unknown_attribute(self):
        with self.assertRaises(AttributeError):
            utils.nonexistent_function
