import os
from importlib.machinery import SourceFileLoader

__all__ = (
    'PythonModuleMixin',
)


class PythonModuleMixin:

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
        loader = SourceFileLoader(self.python_name, self.full_path)
        module = loader.load_module()
        return module
