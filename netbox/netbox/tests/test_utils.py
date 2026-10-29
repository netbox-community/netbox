from importlib import import_module

from django.test import SimpleTestCase

from netbox import utils


# TODO: Remove in NetBox v5.0
class RelocatedFunctionsTestCase(SimpleTestCase):
    """
    Verify that functions relocated from netbox.utils remain importable from it, with a deprecation warning.
    (Ref: #23547)
    """
    def test_relocated_functions(self):
        for name, module in utils.RELOCATED_FUNCTIONS.items():
            with self.subTest(name=name):
                with self.assertWarnsRegex(DeprecationWarning, rf'{name}\(\) from netbox\.utils'):
                    func = getattr(utils, name)
                self.assertIs(func, getattr(import_module(module), name))

    def test_unknown_attribute(self):
        with self.assertRaises(AttributeError):
            utils.nonexistent_function
