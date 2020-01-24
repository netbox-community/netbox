import requests
from cacheops import cached
from django.conf import settings
from packaging import version

if settings.GITHUB_VERSION_TIMEOUT and settings.GITHUB_REPOSITORY:
    @cached(timeout=settings.GITHUB_VERSION_TIMEOUT)
    def get_latest_version():
        url = 'https://api.github.com/repos/{}/releases'.format(settings.GITHUB_REPOSITORY)
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        try:
            response = requests.get(url, headers=headers)
            versions = [(version.parse(release['tag_name']), release.get('html_url'))
                        for release in response.json()
                        if 'tag_name' in release]
            if versions:
                return max(versions)
        except Exception:
            pass

        return 'unknown', None

else:
    def get_latest_version():
        return None
