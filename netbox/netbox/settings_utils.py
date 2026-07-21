"""Startup helpers for settings.py. Import-safe: no Django settings access at import time."""

import importlib
import importlib.util
import os
import sys
import warnings
from typing import NamedTuple

from django.core.exceptions import ImproperlyConfigured

__all__ = (
    'InstallPaths',
    'get_configuration_dir',
    'load_configuration',
    'load_ldap_config',
    'resolve_install_paths',
    'secret_key_hint',
)


class InstallPaths(NamedTuple):
    """Filesystem layout resolved from the install mode (wheel vs. source checkout)."""
    install_mode: str      # 'wheel' or 'checkout'
    base_dir: str          # package data root (BASE_DIR)
    netbox_root: str       # instance root for mutable files (NETBOX_ROOT)
    docs_root: str         # documentation sources on a checkout, the pre-rendered site in a wheel (DOCS_ROOT default)
    static_docs_root: str  # built documentation, source of the STATICFILES 'docs' prefix


def resolve_install_paths(settings_dir, environ):
    """Resolve the install mode and filesystem roots for this NetBox installation.

    A wheel bundles package data (including the pre-rendered documentation site)
    under netbox/_data and keeps mutable instance files under an external instance root
    (NETBOX_ROOT, default /opt/netbox); a source checkout keeps the historical layout,
    where both roots are the project directory. All wheel-vs-checkout branching lives
    here so settings.py stays declarative.
    """
    bundled_data = os.path.join(settings_dir, '_data')
    if os.path.isdir(bundled_data):
        install_mode = 'wheel'
        base_dir = bundled_data
        netbox_root = os.path.abspath(environ.get('NETBOX_ROOT', '/opt/netbox'))
        docs_root = os.path.join(base_dir, 'docs')
        # The wheel bundles the pre-rendered documentation site at _data/docs; it serves as
        # both the DOCS_ROOT default and the STATICFILES 'docs' prefix source.
        static_docs_root = docs_root
    else:
        install_mode = 'checkout'
        base_dir = os.path.dirname(settings_dir)
        netbox_root = base_dir
        docs_root = os.path.join(os.path.dirname(base_dir), 'docs')
        static_docs_root = os.path.join(base_dir, 'project-static', 'docs')
    return InstallPaths(
        install_mode=install_mode,
        base_dir=base_dir,
        netbox_root=netbox_root,
        docs_root=docs_root,
        static_docs_root=static_docs_root,
    )


def secret_key_hint(install_mode, base_dir):
    """Return the command to suggest in the SECRET_KEY-too-short error, based on install mode.

    generate_secret_key.py is not packaged in a wheel, so a wheel install points at the
    `netbox secret-key` console command instead of the (nonexistent) script path.
    """
    if install_mode == 'wheel':
        return 'netbox secret-key'
    return f'python {base_dir}/generate_secret_key.py'


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
        # Remove only the entry this helper inserted at index 0.
        if sys.path and sys.path[0] == module_dir:
            sys.path.pop(0)
    return module


def get_configuration_dir(module):
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
