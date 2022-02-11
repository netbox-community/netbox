## Generic Parts
# These functions are providing the functionality to load
# arbitrary configuration files.
#
# They can be imported by other code (see `ldap_config.py` for an example).

import importlib.util
import sys
from os import scandir
from os.path import abspath, isfile


def _filename(f):
    return f.name


def _import(module_name, path, loaded_configurations):
    spec = importlib.util.spec_from_file_location("", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module

    loaded_configurations.insert(0, module)

    print(f"🧬 loaded config '{path}'")


def read_configurations(config_module, config_dir, main_config):
    loaded_configurations = []

    main_config_path = abspath(f"{config_dir}/{main_config}.py")
    if isfile(main_config_path):
        _import(f"{config_module}.{main_config}", main_config_path, loaded_configurations)
    else:
        print(f"⚠️ Main configuration '{main_config_path}' not found.")

    with scandir(config_dir) as it:
        for f in sorted(it, key=_filename):
            if not f.is_file():
                continue

            if f.name.startswith("__"):
                continue

            if not f.name.endswith(".py"):
                continue

            if f.name == f"{main_config}.py":
                continue

            if f.name == f"{config_dir}.py":
                continue

            module_name = f"{config_module}.{f.name[:-len('.py')]}".replace(".", "_")
            _import(module_name, f.path, loaded_configurations)

    if len(loaded_configurations) == 0:
        print(f"‼️ No configuration files found in '{config_dir}'.")
        raise ImportError(f"No configuration files found in '{config_dir}'.")

    return loaded_configurations


## Specific Parts
# This section's code actually loads the various configuration files
# into the module with the given name.
# It contains the logic to resolve arbitrary configuration options by
# levaraging dynamic programming using `__getattr__`.


_loaded_configurations = read_configurations(
    config_dir="/etc/netbox/config/",
    config_module="netbox.configuration",
    main_config="configuration",
)


def __getattr__(name):
    for config in _loaded_configurations:
        try:
            return getattr(config, name)
        except:
            pass
    raise AttributeError


def __dir__():
    names = []
    for config in _loaded_configurations:
        names.extend(config.__dir__())
    return names
