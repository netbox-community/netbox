import logging

from cacheops import CacheMiss, cache
from django.conf import settings

from utilities.background_tasks import get_releases

logger = logging.getLogger('netbox.releases')


def get_latest_release(pre_releases=False):
    if settings.UPDATE_REPO_URL:
        logger.debug("Checking for most recent release")
        try:
            releases = cache.get('netbox_releases')
            if releases:
                logger.debug("Found {} cached releases. Latest: {}".format(len(releases), max(releases)))
                return max(releases)
        except CacheMiss:
            # Get the releases in the background worker, it will fill the cache
            logger.debug("Initiating background task to retrieve updated releases list")
            get_releases.delay(pre_releases=pre_releases)

    else:
        logger.debug("Skipping release check; UPDATE_REPO_URL not defined")

    return 'unknown', None
