from django.conf import settings as django_settings
from packaging import version

from utilities.versions import get_latest_release


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
    latest_release, github_url = get_latest_release()

    latest_version_str = None
    latest_version_url = None
    if isinstance(latest_release, version.Version):
        current_version = version.parse(django_settings.VERSION)
        if latest_release > current_version:
            latest_version_str = str(latest_release)
            latest_version_url = github_url

    return {
        'latest_version': latest_version_str,
        'latest_version_url': latest_version_url
    }
