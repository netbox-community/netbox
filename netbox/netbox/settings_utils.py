"""Startup helpers for settings.py. Import-safe: no Django settings access at import time."""

import importlib
import importlib.util
import os
import sys
import warnings

from django.core.exceptions import ImproperlyConfigured

__all__ = ('configuration_dir', 'load_configuration', 'load_ldap_config')


def _import_module(name):
    """Import a configuration module by dotted path.

    Preserve NetBox's historical behavior: a friendly ImproperlyConfigured when the module
    itself is absent, but re-raise the original error when the module exists yet imports
    something else that is missing.
    """
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as e:
        if e.name == name:
            raise ImproperlyConfigured(
                f"Specified configuration module ({name}) not found. Please define "
                f"netbox/netbox/configuration.py per the documentation, or specify an alternate "
                f"module in the NETBOX_CONFIGURATION environment variable."
            )
        raise


def _import_from_path(module_name, path):
    """Load a configuration module from an explicit file path.

    The module is registered in sys.modules (and removed again if execution fails), and the
    file's directory is placed on sys.path for the duration of execution so the module can
    import siblings, matching normal import semantics closely enough for configuration files.
    """
    path = os.path.abspath(path)
    module_dir = os.path.dirname(path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImproperlyConfigured(f"Unable to load configuration file {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    sys.path.insert(0, module_dir)
    try:
        spec.loader.exec_module(module)
    except Exception:
        if sys.modules.get(module_name) is module:
            del sys.modules[module_name]
        raise
    finally:
        if module_dir in sys.path:
            sys.path.remove(module_dir)
    return module


def configuration_dir(module):
    """Return the directory containing a loaded configuration module (None if unknown)."""
    source = getattr(module, '__file__', None)
    return os.path.dirname(os.path.abspath(source)) if source else None


def load_configuration(*, install_mode, install_root, environ):
    """Import and return NetBox's configuration module.

    An explicit NETBOX_CONFIGURATION module always wins. In wheel mode, prefer
    <install_root>/conf/configuration.py, loaded by file path (so a stale source tree at
    <install_root>/netbox cannot shadow it and no generic 'configuration' module is left in
    sys.modules), then
    fall back to the legacy <install_root>/netbox/netbox/configuration.py with a migration
    warning. In checkout mode, keep the historical default module.
    """
    explicit = environ.get('NETBOX_CONFIGURATION')
    if explicit:
        return _import_module(explicit)

    if install_mode == 'wheel':
        conf_dir = os.path.join(install_root, 'conf')
        preferred = os.path.join(conf_dir, 'configuration.py')
        legacy = os.path.join(install_root, 'netbox', 'netbox', 'configuration.py')
        if os.path.isfile(preferred):
            if os.path.isfile(legacy):
                warnings.warn(
                    f"Both {preferred} and the legacy {legacy} exist; using {preferred} and "
                    f"ignoring the legacy file.",
                    RuntimeWarning,
                )
            return _import_from_path('netbox_local_configuration', preferred)
        if os.path.isfile(legacy):
            warnings.warn(
                f"Loaded NetBox configuration from the legacy source-tree path {legacy}. For a "
                f"pip-installed NetBox, move it to {preferred}.",
                RuntimeWarning,
            )
            return _import_from_path('netbox_legacy_configuration', legacy)
        raise ImproperlyConfigured(
            f"No NetBox configuration found. For a pip-installed NetBox, create {preferred}, "
            f"or set NETBOX_CONFIGURATION to an importable module."
        )

    return _import_module('netbox.configuration')


def load_ldap_config(config_dir, *, allow_legacy_fallback=False):
    """Load ldap_config.py from the active configuration directory (settings.CONFIGURATION_DIR).

    One rule for every install method: the active ldap_config.py is the one next to the
    active configuration.py. Checkout installs may additionally allow a legacy fallback to
    the historical netbox/netbox/ldap_config.py module, because a custom NETBOX_CONFIGURATION
    can live outside the source tree while LDAP config stayed inside it; the fallback warns
    so those installs can migrate to the sibling rule.
    """
    path = os.path.join(config_dir, 'ldap_config.py') if config_dir else None
    if path and os.path.isfile(path):
        return _import_from_path('netbox.ldap_config', path)
    if allow_legacy_fallback:
        try:
            module = importlib.import_module('netbox.ldap_config')
        except ModuleNotFoundError as e:
            if e.name != 'netbox.ldap_config':
                raise
        else:
            warnings.warn(
                "Loaded LDAP configuration from the legacy netbox/netbox/ldap_config.py module. "
                "Move ldap_config.py into the directory containing the active configuration.py; "
                "this fallback may be removed in a future release.",
                RuntimeWarning,
            )
            return module
    if not config_dir:
        raise ImproperlyConfigured(
            "LDAP configuration file not found: unable to determine the directory containing "
            "configuration.py."
        )
    raise ImproperlyConfigured(
        "LDAP configuration file not found: Check that ldap_config.py has been created "
        "alongside configuration.py. For a pip-installed NetBox, this is "
        "NETBOX_ROOT/conf/ldap_config.py."
    )
