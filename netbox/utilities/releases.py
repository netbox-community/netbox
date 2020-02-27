import requests
from cacheops import cached
from django.conf import settings
from packaging import version


@cached(timeout=settings.UPDATE_CACHE_TIMEOUT, extra=settings.UPDATE_REPO_URL)
def get_releases(pre_releases=False):
    url = '{}/releases'.format(settings.UPDATE_REPO_URL)
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
    if settings.UPDATE_REPO_URL:
        releases = get_releases(pre_releases)
        if releases:
            return max(releases)

    return 'unknown', None
