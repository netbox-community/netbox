import importlib.abc
import importlib.util
import os
import sys
from django.core.files.storage import storages

__all__ = (
    'PythonModuleMixin',
)


class CustomStoragesLoader(importlib.abc.Loader):
    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        storage = storages.create_storage(storages.backends["scripts"])
        with storage.open(self.filename, 'rb') as f:
            code = f.read()
        exec(code, module.__dict__)


def load_module(module_name, filename):
    spec = importlib.util.spec_from_file_location(module_name, filename)
    if spec is None:
        raise ModuleNotFoundError(f"Could not find module: {module_name}")
    loader = CustomStoragesLoader(filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    loader.exec_module(module)
    return module


class PythonModuleMixin:

    def get_jobs(self, name):
        """
        Returns a list of Jobs associated with this specific script or report module
        :param name: The class name of the script or report
        :return: List of Jobs associated with this
        """
        return self.jobs.filter(
            name=name
        )

    @property
    def path(self):
        return os.path.splitext(self.file_path)[0]

    @property
    def python_name(self):
        path, filename = os.path.split(self.full_path)
        name = os.path.splitext(filename)[0]
        if name == '__init__':
            # File is a package
            return os.path.basename(path)
        else:
            return name

    def get_module(self):
        # loader = SourceFileLoader(self.python_name, self.full_path)
        # module = loader.load_module()
        # module = load_module(self.python_name, self.full_path)
        module = load_module(self.python_name, self.name)
        return module
