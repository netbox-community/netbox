import logging

import requests
from django.conf import settings
from django.core.cache import cache
from django_rq import job
from packaging import version

# Get an instance of a logger
logger = logging.getLogger('netbox.releases')


@job('check_releases')
def get_releases(pre_releases=False):
    url = settings.RELEASE_CHECK_URL
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    releases = []

    try:
        logger.info(f"Fetching new releases from {url}")
        response = requests.get(url, headers=headers, proxies=settings.HTTP_PROXIES)
        response.raise_for_status()
        total_releases = len(response.json())

        for release in response.json():
            if 'tag_name' not in release:
                continue
            if not pre_releases and (release.get('devrelease') or release.get('prerelease')):
                continue
            releases.append((version.parse(release['tag_name']), release.get('html_url')))
        logger.debug(f"Found {total_releases} releases; {len(releases)} usable")

    except requests.exceptions.RequestException as exc:
        logger.exception(f"Error while fetching latest release from {url}: {exc}")
        return []

    # Cache the most recent release
    cache.set('latest_release', max(releases), settings.RELEASE_CHECK_TIMEOUT)

    return releases
