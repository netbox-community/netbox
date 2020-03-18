import logging

from cacheops import CacheMiss, cache
from django.conf import settings
from django_rq import get_queue

from utilities.background_tasks import get_releases

logger = logging.getLogger('netbox.releases')


def get_latest_release(pre_releases=False):
    if settings.RELEASE_CHECK_URL:
        logger.debug("Checking for most recent release")
        try:
            latest_release = cache.get('latest_release')
            if latest_release:
                logger.debug("Found cached release: {}".format(latest_release))
                return latest_release
        except CacheMiss:
            # Check for an existing job. This can happen if the RQ worker process is not running.
            queue = get_queue('check_releases')
            if queue.jobs:
                logger.warning("Job to check for new releases is already queued; skipping")
            else:
                # Get the releases in the background worker, it will fill the cache
                logger.info("Initiating background task to retrieve updated releases list")
                get_releases.delay(pre_releases=pre_releases)

    else:
        logger.debug("Skipping release check; RELEASE_CHECK_URL not defined")

    return 'unknown', None
