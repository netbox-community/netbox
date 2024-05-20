import os
from importlib.machinery import SourceFileLoader

__all__ = (
    'PythonModuleMixin',
)


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
        loader = SourceFileLoader(self.python_name, self.full_path)
        module = loader.load_module()
        return module
