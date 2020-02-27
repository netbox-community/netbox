import logging

import requests
from cacheops import cache
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

    releases = []

    # noinspection PyBroadException
    try:
        response = requests.get(url, headers=headers)
        for release in response.json():
            if 'tag_name' not in release:
                continue

            if not pre_releases and (release.get('is_devrelease') or release.get('is_prerelease')):
                continue

            releases.append((version.parse(release['tag_name']), release.get('html_url')))
    except Exception:
        logger.exception("Error while fetching {}".format(url))
        return []

    logger.debug("Found NetBox releases {}".format([str(release) for release, url in releases]))

    cache.set('netbox_releases', releases, settings.UPDATE_CACHE_TIMEOUT)
    return releases
