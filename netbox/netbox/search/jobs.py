import logging

from netbox.jobs import JobRunner
from netbox.search.backends import search_backend

# Internal search-indexing machinery; not part of the public/plugin API.

logger = logging.getLogger(__name__)


class SearchCacheJob(JobRunner):
    """
    Background job which applies deferred updates to the global search cache.
    """
    class Meta:
        name = 'Search cache update'

    def run(self, using=None, cache_groups=None, remove_groups=None, **kwargs):
        search_backend._apply_deferred_updates(
            using=using,
            cache_groups=cache_groups,
            remove_groups=remove_groups,
            log=self.logger,
        )
