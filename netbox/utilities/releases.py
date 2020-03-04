import logging

from cacheops import CacheMiss, cache
from django.conf import settings

from utilities.background_tasks import get_releases

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_latest_release(pre_releases=False):
    if settings.UPDATE_REPO_URL:
        try:
            releases = cache.get('netbox_releases')
            if releases:
                return max(releases)
        except CacheMiss:
            logger.debug("Starting background task to get releases")

            # Get the releases in the background worker, it will fill the cache
            get_releases.delay(pre_releases=pre_releases)

    return 'unknown', None
