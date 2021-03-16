import importlib.util
import sys


def import_object(module_and_object):
    """
    Import a specific object from a specific module by name, such as "extras.plugins.utils.import_object".

    Returns the imported object, or None if it doesn't exist.
    """
    target_module_name, object_name = module_and_object.rsplit('.', 1)
    module_hierarchy = target_module_name.split('.')

    # Iterate through the module hierarchy, checking for the existence of each successive submodule.
    # We have to do this rather than jumping directly to calling find_spec(target_module_name)
    # because find_spec will raise a ModuleNotFoundError if any parent module of target_module_name does not exist.
    module_name = ""
    for module_component in module_hierarchy:
        module_name = f"{module_name}.{module_component}" if module_name else module_component
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            # No such module
            return None

    # Okay, target_module_name exists. Load it if not already loaded
    if target_module_name in sys.modules:
        module = sys.modules[target_module_name]
    else:
        module = importlib.util.module_from_spec(spec)
        sys.modules[target_module_name] = module
        spec.loader.exec_module(module)

    return getattr(module, object_name, None)
