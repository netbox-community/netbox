import logging

import requests
from cacheops.simple import cache, CacheMiss
from django.conf import settings
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

    # Check whether this URL has failed recently and shouldn't be retried yet
    try:
        if url == cache.get('latest_release_no_retry'):
            logger.info("Skipping release check; URL failed recently: {}".format(url))
            return []
    except CacheMiss:
        pass

    try:
        logger.debug("Fetching new releases from {}".format(url))
        response = requests.get(url, headers=headers, proxies=settings.HTTP_PROXIES)
        response.raise_for_status()
        total_releases = len(response.json())

        for release in response.json():
            if 'tag_name' not in release:
                continue
            if not pre_releases and (release.get('devrelease') or release.get('prerelease')):
                continue
            releases.append((version.parse(release['tag_name']), release.get('html_url')))
        logger.debug("Found {} releases; {} usable".format(total_releases, len(releases)))

    except requests.exceptions.RequestException:
        # The request failed. Set a flag in the cache to disable future checks to this URL for 15 minutes.
        logger.exception("Error while fetching {}. Disabling checks for 15 minutes.".format(url))
        cache.set('latest_release_no_retry', url, 900)
        return []

    # Cache the most recent release
    cache.set('latest_release', max(releases), settings.RELEASE_CHECK_TIMEOUT)

    return releases
