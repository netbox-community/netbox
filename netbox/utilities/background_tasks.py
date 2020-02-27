import logging

import requests
from cacheops.simple import cache, CacheMiss
from django.conf import settings
from django_rq import job
from packaging import version

# Get an instance of a logger
logger = logging.getLogger(__name__)


@job
def get_releases(pre_releases=False):
    url = '{}/releases'.format(settings.UPDATE_REPO_URL)
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }

    # Check whether this URL has failed and shouldn't be retried yet
    try:
        failed_url = cache.get('netbox_releases_no_retry')
        if url == failed_url:
            return []
    except CacheMiss:
        pass

    releases = []

    # noinspection PyBroadException
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        for release in response.json():
            if 'tag_name' not in release:
                continue

            if not pre_releases and (release.get('devrelease') or release.get('prerelease')):
                continue

            releases.append((version.parse(release['tag_name']), release.get('html_url')))
    except Exception:
        # Don't retry this URL for 15 minutes
        cache.set('netbox_releases_no_retry', url, 900)

        logger.exception("Error while fetching {}".format(url))
        return []

    cache.set('netbox_releases', releases, settings.UPDATE_CACHE_TIMEOUT)
    return releases
