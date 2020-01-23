from django.conf import settings as django_settings
from packaging import version

from utilities.versions import get_latest_version


def settings(request):
    """
    Expose Django settings in the template context. Example: {{ settings.DEBUG }}
    """
    return {
        'settings': django_settings,
    }


def latest_version(request):
    """
    Get the latest version from the GitHub repository
    """
    github_latest_version, github_url = get_latest_version()

    latest_version_str = None
    latest_version_url = None
    if isinstance(github_latest_version, version.Version):
        current_version = version.parse(django_settings.VERSION)
        if github_latest_version > current_version:
            latest_version_str = str(github_latest_version)
            latest_version_url = github_url

    return {
        'latest_version': latest_version_str,
        'latest_version_url': latest_version_url
    }
