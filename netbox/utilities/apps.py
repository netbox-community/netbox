from django.apps import apps


def get_installed_apps():
    """
    Return the name and version number for each installed Django app.
    """
    installed_apps = {}
    for app_config in apps.get_app_configs():
        app = app_config.module
        if version := getattr(app, 'VERSION', getattr(app, '__version__', None)):
            if type(version) is tuple:
                version = '.'.join(str(n) for n in version)
            elif not isinstance(version, str):
                # Skip non-serializable version types (e.g. setuptools-scm placeholders)
                continue
            installed_apps[app_config.name] = version
    return {
        k: v for k, v in sorted(installed_apps.items())
    }
