import requests
from cacheops import cached
from django.conf import settings
from packaging import version


@cached(timeout=settings.GITHUB_VERSION_TIMEOUT if settings.GITHUB_VERSION_TIMEOUT > 0 else 1)
def get_releases(pre_releases=False):
    url = 'https://api.github.com/repos/{}/releases'.format(settings.GITHUB_REPOSITORY)
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    try:
        response = requests.get(url, headers=headers)
        releases = [(version.parse(release['tag_name']), release.get('html_url'))
                    for release in response.json()
                    if 'tag_name' in release]
    except Exception:
        releases = []

    if not pre_releases:
        releases = [(release, url)
                    for release, url in releases
                    if not release.is_devrelease and not release.is_prerelease]

    return releases


def get_latest_release(pre_releases=False):
    if settings.GITHUB_VERSION_TIMEOUT > 0 and settings.GITHUB_REPOSITORY:
        releases = get_releases(pre_releases)
        if releases:
            return max(releases)

    return 'unknown', None
