import os
from pkgutil import ModuleInfo, get_importer

__all__ = (
    'PythonModuleMixin',
)


class PythonModuleMixin:

    @property
    def path(self):
        return os.path.splitext(self.file_path)[0]

    def get_module_info(self):
        path = os.path.dirname(self.full_path)
        module_name = os.path.basename(self.path)
        return ModuleInfo(
            module_finder=get_importer(path),
            name=module_name,
            ispkg=False
        )

    def get_module(self):
        importer, module_name, _ = self.get_module_info()
        module = importer.find_module(module_name).load_module(module_name)
        return module
